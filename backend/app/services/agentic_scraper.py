import hashlib
import requests
import traceback
from playwright.sync_api import sync_playwright
from app.services.html_purifier import clean_html_to_markdown
from app.services.llm_agent import llm_pipeline
from app.models.domain import PageFingerprint
from sqlalchemy.orm import Session
import datetime

def calculate_hash(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

class AgenticScraper:
    def __init__(self, university_name: str, base_url: str, start_urls: list, db: Session):
        self.university_name = university_name
        self.base_url = base_url
        self.start_urls = start_urls
        self.db = db
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
    def _is_page_changed(self, url: str) -> bool:
        """
        Performs a lightweight request to check if the page's structure/text has changed
        compared to the last known hash in the database.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return True # If it fails, assume we need to force a full playwright check
                
            response.encoding = response.apparent_encoding
            clean_md = clean_html_to_markdown(response.text, base_url=self.base_url)
            current_hash = calculate_hash(clean_md)
            
            fingerprint = self.db.query(PageFingerprint).filter(PageFingerprint.url == url).first()
            
            if fingerprint and fingerprint.content_hash == current_hash:
                print(f"  [{self.university_name}] Hash matched for {url}. Skipping (No changes).")
                # Update last checked time
                fingerprint.last_checked_at = datetime.datetime.utcnow()
                self.db.commit()
                return False
                
            # If changed or new, update the fingerprint table
            print(f"  [{self.university_name}] Changes detected for {url}. Proceeding to deep scrape.")
            if fingerprint:
                fingerprint.content_hash = current_hash
                fingerprint.last_checked_at = datetime.datetime.utcnow()
            else:
                new_fingerprint = PageFingerprint(url=url, content_hash=current_hash)
                self.db.add(new_fingerprint)
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"  [{self.university_name}] Lightweight pre-check failed for {url}: {e}")
            return True # Fallback to full scrape on error

    def scrape_latest_news(self) -> list:
        """
        Navigates the start_urls (if changed), extracts HTML, converts to clean Markdown,
        and uses the Navigator Agent to intelligently find news links.
        """
        news_items = []
        seen_urls = set()
        
        urls_to_scrape = [url for url in self.start_urls if self._is_page_changed(url)]
        
        if not urls_to_scrape:
            return []
            
        with sync_playwright() as p:
            # Use chromium, headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 800}
            )
            
            for url in urls_to_scrape:
                try:
                    print(f"  [{self.university_name}] Playwright Navigating to: {url}")
                    page = context.new_page()
                    # Wait for network to be mostly idle to ensure JS renders
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    html_content = page.content()
                    page.close()
                    
                    # Convert to Markdown for LLM
                    markdown_content = clean_html_to_markdown(html_content, base_url=self.base_url)
                    
                    if not markdown_content:
                        continue
                        
                    # Let LLM Navigator find the links
                    print(f"  [{self.university_name}] Analyzing links with LLM Navigator...")
                    discovered_links = llm_pipeline.navigator_agent(markdown_content)
                    
                    for link_obj in discovered_links:
                        link_url = link_obj.get("url")
                        link_title = link_obj.get("title")
                        
                        if not link_url or link_url in seen_urls:
                            continue
                            
                        # Basic sanity check
                        if link_url.endswith(".pdf") or link_url.startswith("#") or "javascript" in link_url:
                            continue
                            
                        news_items.append({"title": link_title, "url": link_url})
                        seen_urls.add(link_url)
                        
                except Exception as e:
                    print(f"  [{self.university_name}] Playwright Error on {url}: {e}")
                    # traceback.print_exc()
            
            browser.close()
            
        return news_items

    def fetch_article_content(self, url: str) -> str:
        """
        Uses Playwright to fetch the article detail page, ensuring dynamic 
        content is loaded, then cleans it to markdown.
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                
                # Use domcontentloaded for details page to speed things up a bit
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                
                # Small wait in case there's an immediate fetch
                page.wait_for_timeout(1000)
                
                html_content = page.content()
                browser.close()
                
                # We don't necessarily need base_url resolution for detail text extraction
                cleaned_text = clean_html_to_markdown(html_content)
                # Keep it under a reasonable limit for the Extractor Agent
                return cleaned_text[:8000]
        except Exception as e:
            print(f"  [{self.university_name}] Failed to fetch detail {url}: {e}")
            return ""

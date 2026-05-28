import requests
import traceback
from playwright.sync_api import sync_playwright
from app.services.html_purifier import clean_html_to_markdown
from app.services.llm_agent import llm_pipeline
from sqlalchemy.orm import Session
import datetime

class AgenticScraper:
    def __init__(self, university_name: str, base_url: str, start_urls: list, db: Session):
        self.university_name = university_name
        self.base_url = base_url
        self.start_urls = start_urls
        self.db = db
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_latest_news(self) -> list:
        """
        Navigates the start_urls, extracts HTML, converts to clean Markdown,
        and uses the Navigator Agent to intelligently find news links.
        Always processes every URL (Hash checking is disabled).
        """
        news_items = []
        seen_urls = set()
        
        if not self.start_urls:
            return []
            
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 800}
            )
            
            for url in self.start_urls:
                try:
                    print(f"  [{self.university_name}] Playwright Navigating to: {url} (Forced Scrape)")
                    page = context.new_page()
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    html_content = page.content()
                    page.close()
                    
                    markdown_content = clean_html_to_markdown(html_content, base_url=self.base_url)
                    
                    if not markdown_content:
                        continue
                        
                    print(f"  [{self.university_name}] Analyzing links with LLM Navigator...")
                    discovered_links = llm_pipeline.navigator_agent(markdown_content)
                    
                    for link_obj in discovered_links:
                        link_url = link_obj.get("url")
                        link_title = link_obj.get("title")
                        
                        if not link_url or link_url in seen_urls:
                            continue
                            
                        if link_url.endswith(".pdf") or link_url.startswith("#") or "javascript" in link_url:
                            continue
                            
                        news_items.append({"title": link_title, "url": link_url})
                        seen_urls.add(link_url)
                        
                except Exception as e:
                    print(f"  [{self.university_name}] Playwright/LLM Error on {url}: {e}")
            
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

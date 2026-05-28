import os
import sys
import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import domain
from app.services.agentic_scraper import AgenticScraper
from app.services.llm_agent import llm_pipeline
import datetime
import time

def setup_university(db: Session, name: str, name_en: str, official_url: str, logo_url: str = None):
    uni = db.query(domain.University).filter(domain.University.name == name).first()
    if not uni:
        uni = domain.University(
            name=name,
            name_en=name_en,
            official_url=official_url,
            logo_url=logo_url
        )
        db.add(uni)
        db.commit()
        db.refresh(uni)
    return uni

def run_all_tasks():
    db = SessionLocal()
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'universities.json')
        if not os.path.exists(config_path):
            print(f"Error: Configuration file {config_path} not found.")
            return
            
        with open(config_path, 'r', encoding='utf-8') as f:
            universities_config = json.load(f)

        for config in universities_config:
            scraper = AgenticScraper(
                university_name=config["name"],
                base_url=config["base_url"],
                start_urls=config["start_urls"],
                db=db # Pass DB session for fingerprinting
            )
            uni_model = setup_university(db, config["name"], config["name_en"], config["url"], "")
            
            print(f"=====================================")
            print(f"Scraping {config['name']} with Agentic Playwright Scraper...")
            news_list = scraper.scrape_latest_news()
            
            if not news_list:
                print(f"No new candidate links to process for {config['name']}.")
                continue
                
            print(f"Found {len(news_list)} candidate links via LLM Navigator.")
            
            for item in news_list:
                existing = db.query(domain.RawNews).filter(domain.RawNews.url == item["url"]).first()
                if existing:
                    continue
                    
                print(f"Processing new article: {item['title']}")
                raw_text = scraper.fetch_article_content(item["url"])
                if not raw_text:
                    print(f"Could not fetch content for {item['url']}")
                    continue
                
                full_text = f"Title: {item['title']}\n\nContent:\n{raw_text}"
                try:
                    processed_data = llm_pipeline.process_news(full_text)
                except Exception as e:
                    print(f"Skipping article due to LLM pipeline error: {e}")
                    continue
                
                if processed_data and processed_data.get("is_relevant", True):
                    new_raw = domain.RawNews(
                        university_id=uni_model.id,
                        source_type="website",
                        url=item["url"],
                        raw_text=raw_text
                    )
                    db.add(new_raw)
                    db.flush()
                    
                    new_processed = domain.ProcessedInfo(
                        raw_news_id=new_raw.id,
                        category=processed_data.get("category", "其他"),
                        summary=processed_data.get("summary", "暂无摘要"),
                        important_dates=processed_data.get("important_dates_text", ""),
                        published_at=processed_data.get("published_at", ""),
                        target_faculties=json.dumps(processed_data.get("target_faculties", []), ensure_ascii=False),
                        timeline_events=json.dumps(processed_data.get("timeline", []), ensure_ascii=False),
                        exam_requirements=json.dumps(processed_data.get("exam_requirements", {}), ensure_ascii=False)
                    )
                    db.add(new_processed)
                    db.commit()
                    print(f"Saved: {item['title']} - Category: {processed_data.get('category', '其他')}")
                else:
                    print(f"Article ignored by LLM (irrelevant): {item['title']}")
                    
                time.sleep(2) # Rate limit
                
    finally:
        db.close()

if __name__ == "__main__":
    run_all_tasks()

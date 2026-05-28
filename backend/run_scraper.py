import os
import sys
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import domain
from app.services.scrapers import (
    WasedaScraper, 
    UTokyoScraper, KyotoUScraper, OsakaUScraper, TohokuUScraper,
    HokkaidoUScraper, NagoyaUScraper, TsukubaUScraper, ChibaUScraper,
    YNUScraper, ScienceTokyoScraper, UECScraper, TUATScraper,
    KeioScraper, TMUScraper
)
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
        scrapers_registry = [
            # Phase 1
            {"scraper": WasedaScraper(), "name": "早稲田大学", "name_en": "Waseda University", "url": "https://www.waseda.jp/inst/admission/", "logo": ""},
            # Phase 2
            {"scraper": UTokyoScraper(), "name": "東京大学", "name_en": "The University of Tokyo", "url": "https://www.u-tokyo.ac.jp/ja/admissions/index.html", "logo": ""},
            {"scraper": KyotoUScraper(), "name": "京都大学", "name_en": "Kyoto University", "url": "https://www.kyoto-u.ac.jp/ja/admissions", "logo": ""},
            {"scraper": OsakaUScraper(), "name": "大阪大学", "name_en": "Osaka University", "url": "https://www.osaka-u.ac.jp/ja/admissions", "logo": ""},
            {"scraper": TohokuUScraper(), "name": "東北大学", "name_en": "Tohoku University", "url": "https://www.tohoku.ac.jp/japanese/studentinfo/admission/", "logo": ""},
            # Phase 3
            {"scraper": HokkaidoUScraper(), "name": "北海道大学", "name_en": "Hokkaido University", "url": "https://www.hokudai.ac.jp/", "logo": ""},
            {"scraper": NagoyaUScraper(), "name": "名古屋大学", "name_en": "Nagoya University", "url": "https://www.nagoya-u.ac.jp/", "logo": ""},
            {"scraper": TsukubaUScraper(), "name": "筑波大学", "name_en": "University of Tsukuba", "url": "https://www.tsukuba.ac.jp/", "logo": ""},
            {"scraper": ChibaUScraper(), "name": "千葉大学", "name_en": "Chiba University", "url": "https://www.chiba-u.ac.jp/", "logo": ""},
            # Phase 4
            {"scraper": YNUScraper(), "name": "横浜国立大学", "name_en": "Yokohama National University", "url": "https://www.ynu.ac.jp/", "logo": ""},
            {"scraper": ScienceTokyoScraper(), "name": "東京科学大学", "name_en": "Institute of Science Tokyo", "url": "https://www.isct.ac.jp/ja", "logo": ""},
            {"scraper": UECScraper(), "name": "電気通信大学", "name_en": "The University of Electro-Communications", "url": "https://www.uec.ac.jp/", "logo": ""},
            {"scraper": TUATScraper(), "name": "東京農工大学", "name_en": "Tokyo University of Agriculture and Technology", "url": "https://www.tuat.ac.jp/", "logo": ""},
            # Phase 5
            {"scraper": KeioScraper(), "name": "慶應義塾大学", "name_en": "Keio University", "url": "https://www.keio.ac.jp/ja/", "logo": ""},
            {"scraper": TMUScraper(), "name": "東京都立大学", "name_en": "Tokyo Metropolitan University", "url": "https://www.tmu.ac.jp/", "logo": ""}
        ]

        for entry in scrapers_registry:
            scraper = entry["scraper"]
            uni_model = setup_university(db, entry["name"], entry["name_en"], entry["url"], entry["logo"])
            
            print(f"=====================================")
            print(f"Scraping {entry['name']}...")
            news_list = scraper.scrape_latest_news()
            print(f"Found {len(news_list)} news items.")
            
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
                
                if processed_data:
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
                        category=processed_data["category"],
                        summary=processed_data["summary"],
                        important_dates=processed_data["important_dates"]
                    )
                    db.add(new_processed)
                    db.commit()
                    print(f"Saved: {item['title']} - Category: {processed_data['category']}")
                else:
                    print(f"Article ignored by LLM (irrelevant): {item['title']}")
                    
                time.sleep(2) # Rate limit
                
    finally:
        db.close()

if __name__ == "__main__":
    run_all_tasks()

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    name_en = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    official_url = Column(String, nullable=True)
    x_handle = Column(String, nullable=True)
    
    news = relationship("RawNews", back_populates="university")

class RawNews(Base):
    __tablename__ = "raw_news"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"))
    source_type = Column(String, nullable=False) # e.g., "website", "x"
    url = Column(String, unique=True, index=True, nullable=False)
    raw_text = Column(Text, nullable=False)
    scraped_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    university = relationship("University", back_populates="news")
    processed_info = relationship("ProcessedInfo", back_populates="raw_news", uselist=False)

class ProcessedInfo(Base):
    __tablename__ = "processed_info"

    id = Column(Integer, primary_key=True, index=True)
    raw_news_id = Column(Integer, ForeignKey("raw_news.id"), unique=True)
    category = Column(String, index=True, nullable=False) # 出愿情报, Open Campus, 讲座, 变更, 其他
    summary = Column(String(500), nullable=False) # ~100 chars chinese summary
    important_dates = Column(Text, nullable=True) # JSON or simple text
    
    # 新增结构化字段 (兼容老版本，允许为空)
    target_faculties = Column(Text, nullable=True) 
    timeline_events = Column(Text, nullable=True)
    exam_requirements = Column(Text, nullable=True)
    
    published_at = Column(String, nullable=True) # 官网上的发布时间，如 "2024/05/20"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    raw_news = relationship("RawNews", back_populates="processed_info")

class PageFingerprint(Base):
    __tablename__ = "page_fingerprints"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    content_hash = Column(String, nullable=False)
    last_checked_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

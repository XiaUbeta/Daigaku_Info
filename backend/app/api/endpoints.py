from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List

from app.core.database import get_db
from app.models import domain, schemas

router = APIRouter()

# --- Universities ---
@router.get("/universities/", response_model=List[schemas.UniversityResponse])
def read_universities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    universities = db.query(domain.University).offset(skip).limit(limit).all()
    return universities

@router.post("/universities/", response_model=schemas.UniversityResponse)
def create_university(university: schemas.UniversityCreate, db: Session = Depends(get_db)):
    db_university = domain.University(**university.model_dump())
    db.add(db_university)
    db.commit()
    db.refresh(db_university)
    return db_university

# --- Processed Information ---
@router.get("/news/", response_model=List[schemas.ProcessedInfoResponse])
def read_processed_news(
    skip: int = 0, 
    limit: int = 50, 
    university_id: int = None,
    category: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(domain.ProcessedInfo).join(domain.RawNews)
    
    if university_id:
        query = query.filter(domain.RawNews.university_id == university_id)
    if category:
        query = query.filter(domain.ProcessedInfo.category == category)
        
    # Order by official published date descending. 
    # If published_at is '不明' or null, fallback to scraped_at for the sort key.
    # We sort primarily by the calculated date (either published or scraped)
    effective_date = case(
        (
            (
                (domain.ProcessedInfo.published_at == '不明') | 
                (domain.ProcessedInfo.published_at == None) | 
                (domain.ProcessedInfo.published_at == '')
            ),
            func.to_char(domain.RawNews.scraped_at, 'YYYY/MM/DD')
        ),
        else_=domain.ProcessedInfo.published_at
    )
    
    query = query.order_by(effective_date.desc())
    
    news = query.offset(skip).limit(limit).all()
    return news

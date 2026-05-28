from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UniversityBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    logo_url: Optional[str] = None
    official_url: Optional[str] = None
    x_handle: Optional[str] = None

class UniversityCreate(UniversityBase):
    pass

class UniversityResponse(UniversityBase):
    id: int
    
    class Config:
        from_attributes = True

class ProcessedInfoBase(BaseModel):
    category: str
    summary: str
    important_dates: Optional[str] = None

class RawNewsBase(BaseModel):
    source_type: str
    url: str
    raw_text: str
    scraped_at: datetime

class RawNewsResponse(RawNewsBase):
    id: int
    university_id: int
    
    class Config:
        from_attributes = True

class ProcessedInfoResponse(ProcessedInfoBase):
    id: int
    created_at: datetime
    raw_news: RawNewsResponse
    
    class Config:
        from_attributes = True

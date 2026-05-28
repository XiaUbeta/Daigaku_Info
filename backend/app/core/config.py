from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Japanese University Admissions System"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/info_db"
    
    # LLM Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: Optional[str] = None # Support for Siliconflow or custom endpoints
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()

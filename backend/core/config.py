import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    
    DATABASE_URL: Optional[str] = None
    
    LLM_MODEL: str = "gpt-5-mini"
    
    ALLOWED_ORIGINS: str = ""
    
    RATE_LIMIT_ENABLED: bool = True
    
    SESSION_DAILY_LIMIT: int = 3
    IP_DAILY_LIMIT: int = 6
    
    OPENAI_API_KEY: str
    
    def __init__(self, **values):
        super().__init__(**values)
        if not self.DATABASE_URL:
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT")
            db_name = os.getenv("DB_NAME")
            if all([db_user, db_password, db_host, db_port, db_name]):
                self.DATABASE_URL = (
                    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                )
                print(f"Using DATABASE_URL from individual environment variables: {self.DATABASE_URL}")
            elif self.DEBUG:
                self.DATABASE_URL = "sqlite:///./database.db"
                print(f"Using SQLite database: {self.DATABASE_URL}")
            else:
                raise ValueError(
                    "DATABASE_URL or DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME must be set"
                )
            
    # Because .env does not support lists, we need to parse the ALLOWED_ORIGINS string into a list of strings
    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
settings = Settings()
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Sprint Training System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_CHANGE_THIS_IN_PROD"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 Days
    
    # Database
    # Default to SQLite for local dev ease, change to POSTGRES in env
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./sql_app.db"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

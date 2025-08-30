from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Legal AI RAG API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    
    database_url: Optional[str] = None
    secret_key: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"


settings = Settings()
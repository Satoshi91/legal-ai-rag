from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Legal AI RAG API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "your-secret-key-here"
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # OpenRouter Configuration (for ChatGPT-5)
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-5"
    
    # Vector Store Configuration
    vector_store_path: str = "./data/vector_store"
    
    class Config:
        env_file = ".env"


settings = Settings()
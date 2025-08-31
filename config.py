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
    
    # Pinecone Configuration
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: str = "legal-documents"
    
    # Project Settings
    project_name: str = "legal-xml-vectorization"
    dimension: str = "3072"
    metric: str = "cosine"
    
    class Config:
        env_file = ".env"


settings = Settings()
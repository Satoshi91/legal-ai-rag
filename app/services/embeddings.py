from openai import OpenAI
from typing import List
from config import settings


class EmbeddingsService:
    def __init__(self):
        if not settings.openai_api_key:
            print("⚠️ WARNING: OpenAI API key is not set. Embeddings service will not work.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
        
        self.model = "text-embedding-3-large"
    
    async def get_embedding(self, text: str) -> List[float]:
        """単一テキストの埋め込みを取得"""
        if not self.client:
            raise Exception("OpenAI API key is not configured. Cannot generate embeddings.")
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """複数テキストの埋め込みを一括取得"""
        if not self.client:
            raise Exception("OpenAI API key is not configured. Cannot generate embeddings.")
        
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise Exception(f"Failed to get embeddings: {str(e)}")


# シングルトンインスタンス
embeddings_service = EmbeddingsService()
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class DocumentMetadata(BaseModel):
    law_name: str
    article: str
    title: str
    category: str


class SearchResult(BaseModel):
    document: str
    similarity_score: float
    metadata: DocumentMetadata


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int


class HealthResponse(BaseModel):
    status: str
    vector_store_info: Optional[Dict[str, Any]] = None


# Chat related models
class ChatRequest(BaseModel):
    message: str
    max_context_docs: int = 3


class ChatResponse(BaseModel):
    user_query: str
    ai_response: str
    context_documents: List[SearchResult]
    total_context_docs: int
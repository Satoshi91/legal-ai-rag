from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class DocumentMetadata(BaseModel):
    law_name: str = ""
    article: Union[str, float] = Field(default="", description="Article number or identifier")
    title: str = ""
    category: str = ""


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
class Message(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="Conversation history")
    max_context_docs: int = Field(default=3, description="Maximum number of context documents")


class ChatResponse(BaseModel):
    user_query: str
    ai_response: str
    context_documents: List[SearchResult]
    total_context_docs: int
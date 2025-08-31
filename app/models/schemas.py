from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class DocumentMetadata(BaseModel):
    ArticleNum: int = Field(default=0, description="Article number")
    ArticleTitle: str = Field(default="", description="Article title")
    LawID: str = Field(default="", description="Law ID")
    LawTitle: str = Field(default="", description="Law title")
    LawType: str = Field(default="", description="Law type (e.g., Act, CabinetOrder)")
    filename: str = Field(default="", description="Original filename")
    original_text: str = Field(default="", description="Original text content")
    revisionID: str = Field(default="", description="Revision ID")
    updateDate: str = Field(default="", description="Update date")


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
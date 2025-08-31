from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, SearchResult, DocumentMetadata
from app.services.rag import rag_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """AIチャット（RAG機能付き）"""
    try:
        # メッセージ履歴の検証
        if not request.messages:
            raise HTTPException(status_code=422, detail="Messages array cannot be empty")
        
        # RAGパイプライン実行
        rag_result = await rag_service.chat_with_rag(
            messages=request.messages,
            max_context_docs=request.max_context_docs
        )
        
        # レスポンス形式に変換
        context_results = []
        for doc in rag_result["context_documents"]:
            search_result = SearchResult(
                document=doc["document"],
                similarity_score=doc["similarity_score"],
                metadata=DocumentMetadata(**doc["metadata"])
            )
            context_results.append(search_result)
        
        return ChatResponse(
            user_query=rag_result["user_query"],
            ai_response=rag_result["ai_response"],
            context_documents=context_results,
            total_context_docs=rag_result["total_context_docs"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
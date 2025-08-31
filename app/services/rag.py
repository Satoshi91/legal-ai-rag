from typing import Dict, Any, List
import time
from app.models.schemas import Message
from app.utils.railway_logger import railway_logger
from .search import search_service
from .chat import chat_service


class RAGService:
    def __init__(self):
        self.search_service = search_service
        self.chat_service = chat_service
    
    async def chat_with_rag(
        self, 
        messages: List[Message], 
        max_context_docs: int = 3
    ) -> Dict[str, Any]:
        """RAGパイプライン: 検索 → 回答生成"""
        start_time = time.time()
        
        # 最新のユーザーメッセージを取得
        user_query = ""
        for message in reversed(messages):
            if message.role == "user":
                user_query = message.content
                break
        
        if not user_query:
            raise ValueError("No user message found in conversation history")
        
        # RAGパイプライン開始ログ
        railway_logger.log_rag_pipeline(
            stage="start",
            user_query=user_query
        )
        
        # 1. 関連条文を検索
        search_results = await self.search_service.search_documents(
            query=user_query,
            n_results=max_context_docs
        )
        
        # 検索完了ログ
        railway_logger.log_rag_pipeline(
            stage="search_complete",
            user_query=user_query,
            context_docs_count=len(search_results)
        )
        
        # 2. AI回答を生成
        ai_response = await self.chat_service.generate_response(
            messages=messages,
            context_documents=search_results
        )
        
        # 生成完了ログ
        total_time_ms = (time.time() - start_time) * 1000
        railway_logger.log_rag_pipeline(
            stage="complete",
            user_query=user_query,
            context_docs_count=len(search_results),
            total_time_ms=total_time_ms
        )
        
        # 3. 結果を構造化して返す
        return {
            "user_query": user_query,
            "ai_response": ai_response,
            "context_documents": search_results,
            "total_context_docs": len(search_results)
        }


# シングルトンインスタンス
rag_service = RAGService()
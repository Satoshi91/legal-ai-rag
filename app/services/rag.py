from typing import Dict, Any, List
from app.models.schemas import Message
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
        
        # 最新のユーザーメッセージを取得
        user_query = ""
        for message in reversed(messages):
            if message.role == "user":
                user_query = message.content
                break
        
        if not user_query:
            raise ValueError("No user message found in conversation history")
        
        # 1. 関連条文を検索
        search_results = await self.search_service.search_documents(
            query=user_query,
            n_results=max_context_docs
        )
        
        # 2. AI回答を生成
        ai_response = await self.chat_service.generate_response(
            messages=messages,
            context_documents=search_results
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
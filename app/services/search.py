from typing import List, Dict, Any
from .embeddings import embeddings_service
from .vector_store import vector_store


class SearchService:
    def __init__(self):
        self.embeddings_service = embeddings_service
        self.vector_store = vector_store
    
    async def search_documents(
        self, 
        query: str, 
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """クエリに基づいて関連文書を検索"""
        
        # クエリの埋め込みを生成
        query_embedding = await self.embeddings_service.get_embedding(query)
        
        # ベクター検索を実行
        raw_results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=n_results
        )
        
        # 結果を整形
        formatted_results = []
        
        if raw_results["documents"] and len(raw_results["documents"]) > 0:
            documents = raw_results["documents"][0]
            metadatas = raw_results["metadatas"][0] if raw_results["metadatas"] else []
            distances = raw_results["distances"][0] if raw_results["distances"] else []
            
            for i, doc in enumerate(documents):
                result = {
                    "document": doc,
                    "similarity_score": 1 - distances[i] if i < len(distances) else 0,  # コサイン距離を類似度に変換
                    "metadata": metadatas[i] if i < len(metadatas) else {}
                }
                formatted_results.append(result)
        
        return formatted_results


# シングルトンインスタンス
search_service = SearchService()
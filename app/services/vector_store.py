from pinecone import Pinecone
from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime
from config import settings
from app.utils.railway_logger import railway_logger


class VectorStore:
    def __init__(self):
        # Pineconeクライアントを初期化
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY is required")
            
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        
        # インデックス名
        self.index_name = settings.pinecone_index_name
        
        # インデックスに接続
        try:
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            raise Exception(f"Failed to connect to Pinecone index '{self.index_name}': {str(e)}")
    
    def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str],
        embeddings: List[List[float]]
    ):
        """文書をベクターストアに追加"""
        try:
            # Pinecone upsert用のベクターデータを準備
            vectors = []
            for i, (doc_id, embedding, metadata) in enumerate(zip(ids, embeddings, metadatas)):
                # メタデータに文書内容も追加
                full_metadata = {**metadata, "document": documents[i]}
                vectors.append({
                    "id": doc_id,
                    "values": embedding,
                    "metadata": full_metadata
                })
            
            # Pineconeにupsert
            self.index.upsert(vectors=vectors)
            return True
        except Exception as e:
            raise Exception(f"Failed to add documents: {str(e)}")
    
    def search(
        self, 
        query_embedding: List[float], 
        n_results: int = 5
    ) -> Dict[str, Any]:
        """類似文書を検索"""
        try:
            # Pineconeリクエストログ（Railway最適化）
            start_time = time.time()
            railway_logger.log_pinecone_request(
                operation="query",
                index_name=self.index_name,
                vector_dimension=len(query_embedding),
                top_k=n_results
            )
            
            # Pineconeで検索を実行
            pinecone_results = self.index.query(
                vector=query_embedding,
                top_k=n_results,
                include_metadata=True,
                namespace=""
            )
            
            # Pineconeレスポンスログ（Railway最適化）
            response_time_ms = (time.time() - start_time) * 1000
            matches_metadata = [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata_keys": list(match.metadata.keys()) if match.metadata else []
                } for match in pinecone_results.matches
            ]
            
            railway_logger.log_pinecone_response(
                operation="query",
                matches_count=len(pinecone_results.matches),
                response_time_ms=response_time_ms,
                matches_metadata=matches_metadata
            )
            
            # ChromaDB形式のレスポンスに変換
            documents = []
            metadatas = []
            distances = []
            
            for match in pinecone_results.matches:
                # メタデータから文書内容を取得（'original_text'フィールドを使用）
                if "original_text" in match.metadata:
                    documents.append(match.metadata["original_text"])
                    # Pineconeの元のメタデータをそのまま保持（original_textは除く）
                    metadata = {k: v for k, v in match.metadata.items() if k != "original_text"}
                    metadatas.append(metadata)
                    # Pineconeのスコアは類似度なので、距離に変換（1 - score）
                    distances.append(1 - match.score)
            
            return {
                "documents": [documents],
                "metadatas": [metadatas], 
                "distances": [distances]
            }
        except Exception as e:
            raise Exception(f"Failed to search documents: {str(e)}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """インデックス情報を取得"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "index_name": self.index_name,
                "document_count": stats.total_vector_count,
                "dimension": stats.dimension
            }
        except Exception as e:
            raise Exception(f"Failed to get index info: {str(e)}")


# シングルトンインスタンス
vector_store = VectorStore()
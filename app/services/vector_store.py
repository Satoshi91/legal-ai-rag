import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
from config import settings


class VectorStore:
    def __init__(self):
        # ChromaDBクライアントを初期化
        os.makedirs(settings.vector_store_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=settings.vector_store_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # コレクション名
        self.collection_name = "legal_documents"
        
        # コレクションを取得または作成
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str],
        embeddings: List[List[float]]
    ):
        """文書をベクターストアに追加"""
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
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
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            return results
        except Exception as e:
            raise Exception(f"Failed to search documents: {str(e)}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """コレクション情報を取得"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count
            }
        except Exception as e:
            raise Exception(f"Failed to get collection info: {str(e)}")


# シングルトンインスタンス
vector_store = VectorStore()
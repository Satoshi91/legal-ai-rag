import json
import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embeddings import embeddings_service
from app.services.vector_store import vector_store


async def ingest_legal_data():
    """サンプル法律データをChromaDBに投入"""
    
    print("Loading sample legal data...")
    
    # サンプルデータを読み込み
    with open("data/sample_legal_texts.json", "r", encoding="utf-8") as f:
        legal_data = json.load(f)
    
    print(f"Loaded {len(legal_data)} legal documents")
    
    # 文書テキストを作成（検索用）
    documents = []
    metadatas = []
    ids = []
    
    for item in legal_data:
        # 検索対象となるテキストを結合
        full_text = f"{item['law_name']} {item['article']} {item['title']}: {item['content']}"
        documents.append(full_text)
        
        # メタデータ
        metadatas.append({
            "law_name": item["law_name"],
            "article": item["article"],
            "title": item["title"],
            "category": item["category"]
        })
        
        ids.append(item["id"])
    
    print("Generating embeddings...")
    
    # 埋め込みを生成（バッチ処理）
    embeddings = await embeddings_service.get_embeddings(documents)
    
    print(f"Generated {len(embeddings)} embeddings")
    
    print("Storing in ChromaDB...")
    
    # ChromaDBに保存
    vector_store.add_documents(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )
    
    print("✅ Data ingestion completed!")
    
    # コレクション情報を表示
    info = vector_store.get_collection_info()
    print(f"Collection: {info['collection_name']}")
    print(f"Total documents: {info['document_count']}")


if __name__ == "__main__":
    asyncio.run(ingest_legal_data())
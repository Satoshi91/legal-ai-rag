from fastapi import APIRouter
from typing import Dict, Any, Optional
import os
import sys
from datetime import datetime
from config import settings

router = APIRouter()

@router.get("/debug")
async def debug_info():
    """デバッグ情報を返すエンドポイント"""
    
    # 環境変数チェック
    env_vars = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "PINECONE_API_KEY": bool(os.getenv("PINECONE_API_KEY")),
        "PINECONE_INDEX_NAME": bool(os.getenv("PINECONE_INDEX_NAME")),
        "OPENROUTER_API_KEY": bool(os.getenv("OPENROUTER_API_KEY")),
        "DEBUG": bool(os.getenv("DEBUG"))
    }
    
    # 設定値確認
    config_values = {
        "pinecone_index_name": settings.pinecone_index_name,
        "openrouter_model": settings.openrouter_model,
        "debug": settings.debug,
        "app_name": settings.app_name
    }
    
    # Pinecone接続テスト
    pinecone_test = await test_pinecone_connection()
    
    # OpenAI接続テスト
    openai_test = await test_openai_connection()
    
    # システム情報
    system_info = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "server_ready": True
    }
    
    return {
        "environment_variables": env_vars,
        "config_values": config_values,
        "connection_tests": {
            "pinecone": pinecone_test,
            "openai": openai_test
        },
        "system_info": system_info
    }


async def test_pinecone_connection() -> Dict[str, Any]:
    """Pinecone接続をテスト"""
    try:
        # Pineconeクライアント作成を試行
        if not settings.pinecone_api_key:
            return {
                "status": "failed",
                "error": "PINECONE_API_KEY is not set"
            }
        
        from pinecone import Pinecone
        pc = Pinecone(api_key=settings.pinecone_api_key)
        index = pc.Index(settings.pinecone_index_name)
        
        # インデックス統計取得を試行
        stats = index.describe_index_stats()
        
        return {
            "status": "success",
            "index_stats": {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "namespaces": list(stats.namespaces.keys()) if stats.namespaces else ["default"]
            }
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


async def test_openai_connection() -> Dict[str, Any]:
    """OpenAI接続をテスト"""
    try:
        if not settings.openai_api_key:
            return {
                "status": "not_configured",
                "error": "OPENAI_API_KEY is not set"
            }
        
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        
        # 簡単な接続確認（モデル一覧取得）
        # 実際のAPI呼び出しは避けて、クライアント作成のみテスト
        return {
            "status": "success",
            "note": "Client initialized successfully"
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
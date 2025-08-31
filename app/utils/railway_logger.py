"""
Railway最適化ログシステム

Railway.appの構造化ログ機能を最大限活用するためのログシステム
- JSON形式での構造化ログ出力
- Railway Log Explorerでの検索・フィルタリング最適化
- メタデータの適切な構造化
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    SYSTEM = "system"
    PINECONE = "pinecone"
    OPENROUTER = "openrouter"
    RAG = "rag"
    CHAT = "chat"


class RailwayLogger:
    def __init__(self, service_name: str = "legal-ai-rag"):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        
        # Railway用のJSONフォーマッターを設定
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(self._create_json_formatter())
            self.logger.addHandler(handler)
    
    def _create_json_formatter(self):
        """Railway最適化JSONフォーマッターを作成"""
        class RailwayJSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": record.levelname.lower(),
                    "service": "legal-ai-rag",
                    "message": record.getMessage(),
                }
                
                # 追加メタデータがある場合は追加
                if hasattr(record, 'extra_data'):
                    log_entry.update(record.extra_data)
                
                return json.dumps(log_entry, ensure_ascii=False)
        
        return RailwayJSONFormatter()
    
    def _log_structured(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        **metadata
    ):
        """構造化ログを出力"""
        log_data = {
            "category": category.value,
            "metadata": metadata,
        }
        
        # レベルに応じてログ出力
        getattr(self.logger, level.value)(
            message,
            extra={"extra_data": log_data}
        )
    
    def log_request(
        self,
        method: str,
        path: str,
        user_query: Optional[str] = None,
        request_id: Optional[str] = None,
        **additional_metadata
    ):
        """HTTPリクエストログ"""
        metadata = {
            "http_method": method,
            "http_path": path,
            "request_id": request_id,
            **additional_metadata
        }
        
        if user_query:
            metadata["user_query"] = user_query[:100]  # 長すぎる場合は切り詰め
        
        self._log_structured(
            LogLevel.INFO,
            LogCategory.REQUEST,
            f"{method} {path}",
            **metadata
        )
    
    def log_pinecone_request(
        self,
        operation: str,
        index_name: str,
        vector_dimension: int,
        top_k: int,
        request_id: Optional[str] = None
    ):
        """Pineconeリクエストログ"""
        self._log_structured(
            LogLevel.INFO,
            LogCategory.PINECONE,
            f"Pinecone {operation}",
            operation=operation,
            index_name=index_name,
            vector_dimension=vector_dimension,
            top_k=top_k,
            request_id=request_id
        )
    
    def log_pinecone_response(
        self,
        operation: str,
        matches_count: int,
        response_time_ms: float,
        request_id: Optional[str] = None,
        matches_metadata: Optional[list] = None
    ):
        """Pineconeレスポンスログ"""
        metadata = {
            "operation": operation,
            "matches_count": matches_count,
            "response_time_ms": response_time_ms,
            "request_id": request_id
        }
        
        if matches_metadata:
            metadata["top_match_scores"] = [
                match.get("score", 0) for match in matches_metadata[:3]
            ]
        
        self._log_structured(
            LogLevel.INFO,
            LogCategory.PINECONE,
            f"Pinecone {operation} completed",
            **metadata
        )
    
    def log_openrouter_request(
        self,
        model: str,
        messages_count: int,
        temperature: float,
        max_tokens: int,
        request_id: Optional[str] = None
    ):
        """OpenRouterリクエストログ"""
        self._log_structured(
            LogLevel.INFO,
            LogCategory.OPENROUTER,
            f"OpenRouter chat request",
            model=model,
            messages_count=messages_count,
            temperature=temperature,
            max_tokens=max_tokens,
            request_id=request_id
        )
    
    def log_openrouter_response(
        self,
        model: str,
        response_length: int,
        response_time_ms: float,
        usage: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """OpenRouterレスポンスログ"""
        self._log_structured(
            LogLevel.INFO,
            LogCategory.OPENROUTER,
            f"OpenRouter chat response",
            model=model,
            response_length=response_length,
            response_time_ms=response_time_ms,
            usage=usage,
            request_id=request_id
        )
    
    def log_rag_pipeline(
        self,
        stage: str,  # "start", "search_complete", "generation_complete", "complete"
        user_query: str,
        context_docs_count: Optional[int] = None,
        total_time_ms: Optional[float] = None,
        request_id: Optional[str] = None
    ):
        """RAGパイプライン処理ログ"""
        metadata = {
            "stage": stage,
            "user_query_length": len(user_query),
            "user_query": user_query[:100],  # 長すぎる場合は切り詰め
            "request_id": request_id
        }
        
        if context_docs_count is not None:
            metadata["context_docs_count"] = context_docs_count
        
        if total_time_ms is not None:
            metadata["total_time_ms"] = total_time_ms
        
        self._log_structured(
            LogLevel.INFO,
            LogCategory.RAG,
            f"RAG pipeline {stage}",
            **metadata
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        error_details: Optional[Dict] = None,
        request_id: Optional[str] = None
    ):
        """エラーログ"""
        metadata = {
            "error_type": error_type,
            "request_id": request_id
        }
        
        if error_details:
            metadata["error_details"] = error_details
        
        self._log_structured(
            LogLevel.ERROR,
            LogCategory.ERROR,
            error_message,
            **metadata
        )
    
    def log_system_event(
        self,
        event: str,
        message: str,
        **metadata
    ):
        """システムイベントログ"""
        self._log_structured(
            LogLevel.INFO,
            LogCategory.SYSTEM,
            message,
            event=event,
            **metadata
        )


# シングルトンインスタンス
railway_logger = RailwayLogger()
import httpx
import json
import time
from typing import List, Dict, Any
from datetime import datetime
from config import settings
from app.utils.railway_logger import railway_logger


class ChatService:
    def __init__(self):
        if not settings.openrouter_api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.model = settings.openrouter_model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "Legal AI RAG System"
        }
    
    async def generate_response(
        self, 
        messages: List, 
        context_documents: List[Dict[str, Any]]
    ) -> str:
        """会話履歴と関連条文からAI回答を生成"""
        
        # コンテキスト文書を整形
        context_text = self._format_context(context_documents)
        
        # 会話履歴をOpenRouter形式に変換
        conversation_messages = []
        
        # システムプロンプトを追加
        system_prompt = f"""あなたは日本の法律に精通した専門家です。正確で分かりやすい法的回答を提供してください。

【重要】必ず日本語で回答してください。

以下の関連条文を参考に回答してください：
{context_text}

回答指針：
1. 関連条文を根拠として明示してください
2. 法律用語は分かりやすく説明してください
3. 具体的で実践的なアドバイスを含めてください
4. 必要に応じて注意事項や例外についても言及してください"""

        conversation_messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 会話履歴を追加
        for message in messages:
            conversation_messages.append({
                "role": message.role,
                "content": message.content
            })
        
        # OpenRouterリクエスト準備とログ（Railway最適化）
        openrouter_request = {
            "model": self.model,
            "messages": conversation_messages,
            "temperature": 0.3,
            "max_tokens": 1500
        }
        
        start_time = time.time()
        railway_logger.log_openrouter_request(
            model=self.model,
            messages_count=len(conversation_messages),
            temperature=0.3,
            max_tokens=1500
        )

        # OpenRouter APIを呼び出し
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=openrouter_request
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # OpenRouterレスポンスログ（Railway最適化）
                    response_time_ms = (time.time() - start_time) * 1000
                    message = result["choices"][0]["message"]
                    content = message.get("content", "")
                    
                    # GPT-5の場合、reasoningフィールドから回答を取得
                    if not content and "reasoning" in message:
                        content = message["reasoning"]
                    
                    # reasoning_detailsのsummaryからも回答を取得
                    if not content and "reasoning_details" in message:
                        for detail in message["reasoning_details"]:
                            if detail.get("type") == "reasoning.summary":
                                content = detail.get("summary", "")
                                break
                    
                    final_content = content or "申し訳ございませんが、回答を生成できませんでした。"
                    
                    railway_logger.log_openrouter_response(
                        model=result.get("model", self.model),
                        response_length=len(final_content),
                        response_time_ms=response_time_ms,
                        usage=result.get("usage", {})
                    )
                    
                    return final_content
                else:
                    # エラーレスポンス（Railway最適化）
                    railway_logger.log_error(
                        error_type="openrouter_api_error",
                        error_message=f"OpenRouter API error: {response.status_code}",
                        error_details={
                            "status_code": response.status_code,
                            "error_text": response.text,
                            "response_time_ms": (time.time() - start_time) * 1000
                        }
                    )
                    
                    raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            raise Exception(f"Failed to generate chat response: {str(e)}")
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """関連条文を読みやすい形式に整形"""
        if not documents:
            return "関連する条文が見つかりませんでした。"
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            law_title = metadata.get("LawTitle", "不明")
            article_num = metadata.get("ArticleNum", 0)
            article_title = metadata.get("ArticleTitle", "")
            content = doc.get("document", "")
            
            # 条文番号の表示形式を整理
            article_display = f"第{article_num}条" if article_num > 0 else article_title
            
            context_parts.append(
                f"【参考条文{i}】\n"
                f"{law_title} {article_display}\n"
                f"{content}\n"
            )
        
        return "\n".join(context_parts)
    


# シングルトンインスタンス
chat_service = ChatService()
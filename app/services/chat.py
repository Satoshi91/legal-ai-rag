import httpx
from typing import List, Dict, Any
from config import settings


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
        
        # OpenRouter APIを呼び出し
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": conversation_messages,
                        "temperature": 0.3,
                        "max_tokens": 1500
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
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
                    
                    return content or "申し訳ございませんが、回答を生成できませんでした。"
                else:
                    print(f"OpenRouter API error: {response.status_code} - {response.text}")
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
            law_name = metadata.get("law_name", "不明")
            article = metadata.get("article", "不明")
            title = metadata.get("title", "")
            content = doc.get("document", "").split(": ", 1)[-1]  # 冗長部分を除去
            
            context_parts.append(
                f"【参考条文{i}】\n"
                f"{law_name} {article} {title}\n"
                f"{content}\n"
            )
        
        return "\n".join(context_parts)
    


# シングルトンインスタンス
chat_service = ChatService()
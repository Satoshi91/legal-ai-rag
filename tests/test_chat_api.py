import httpx
import json
import re
import time
from typing import Dict, Any, List
from datetime import datetime


class ChatAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def is_japanese_response(self, text: str) -> bool:
        """レスポンスが日本語を含むかチェック"""
        # ひらがな、カタカナ、漢字の正規表現
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
        return bool(japanese_pattern.search(text))
    
    def check_response_content(self, response: str, checks: Dict[str, Any]) -> Dict[str, bool]:
        """レスポンスの内容をチェック"""
        results = {}
        
        # 日本語チェック
        if checks.get("contains_japanese"):
            results["contains_japanese"] = self.is_japanese_response(response)
        
        # 最小文字数チェック
        if "response_length_min" in checks:
            results["response_length_min"] = len(response) >= checks["response_length_min"]
        
        # 特定の文字列が含まれているかチェック
        if "should_contain" in checks:
            should_contain = checks["should_contain"]
            results["should_contain"] = all(keyword in response for keyword in should_contain)
        
        return results
    
    async def test_chat_endpoint(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """チャットエンドポイントをテスト"""
        start_time = time.time()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/chat",
                json=test_case["request"]
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get("ai_response", "")
                
                # 期待値チェック
                check_results = {}
                if "expected_checks" in test_case:
                    check_results = self.check_response_content(
                        ai_response, 
                        test_case["expected_checks"]
                    )
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "user_query": response_data.get("user_query", ""),
                    "ai_response": ai_response,
                    "context_documents_count": len(response_data.get("context_documents", [])),
                    "total_context_docs": response_data.get("total_context_docs", 0),
                    "check_results": check_results,
                    "all_checks_passed": all(check_results.values()) if check_results else True,
                    "full_response_data": response_data
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "error": response.text,
                    "check_results": {},
                    "all_checks_passed": False
                }
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": False,
                "status_code": None,
                "response_time": response_time,
                "error": str(e),
                "check_results": {},
                "all_checks_passed": False
            }
    
    async def health_check(self) -> bool:
        """サーバーの健全性チェック"""
        try:
            # まず /health エンドポイントを試す
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                return True
        except:
            pass
        
        try:
            # /health が失敗した場合、ルートエンドポイントを試す
            response = await self.client.get(f"{self.base_url}/")
            return response.status_code == 200
        except:
            return False


def load_test_cases(file_path: str) -> List[Dict[str, Any]]:
    """テストケースをJSONファイルから読み込み"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_test_result(test_name: str, result: Dict[str, Any], request_data: Dict[str, Any] = None) -> str:
    """テスト結果を整形してログ用文字列に変換"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    output = [
        f"=" * 80,
        f"テスト名: {test_name}",
        f"実行時刻: {timestamp}",
        f"成功: {'✓' if result['success'] else '✗'}",
        f"ステータスコード: {result.get('status_code', 'N/A')}",
        f"レスポンス時間: {result['response_time']:.2f}秒",
        ""
    ]
    
    # リクエストデータを表示
    if request_data:
        output.extend([
            "📤 リクエスト (JSON):",
            "-" * 40,
            json.dumps(request_data, ensure_ascii=False, indent=2),
            "-" * 40,
            ""
        ])
    
    if result["success"]:
        output.extend([
            f"ユーザークエリ: {result.get('user_query', 'N/A')}",
            f"コンテキスト文書数: {result.get('context_documents_count', 0)}",
            f"総コンテキスト文書数: {result.get('total_context_docs', 0)}",
            "",
            "AI回答:",
            "-" * 40,
            result.get('ai_response', 'No response'),
            "-" * 40,
            ""
        ])
        
        # 完全なレスポンスJSONを表示
        if result.get('full_response_data'):
            output.extend([
                "📥 レスポンス (JSON):",
                "-" * 40,
                json.dumps(result['full_response_data'], ensure_ascii=False, indent=2),
                "-" * 40,
                ""
            ])
        
        # チェック結果
        if result.get('check_results'):
            output.append("チェック結果:")
            for check_name, passed in result['check_results'].items():
                status = "✓" if passed else "✗"
                output.append(f"  {check_name}: {status}")
            
            output.append(f"全てのチェック通過: {'✓' if result['all_checks_passed'] else '✗'}")
    else:
        output.extend([
            f"エラー: {result.get('error', 'Unknown error')}",
        ])
    
    output.append("=" * 80)
    output.append("")
    
    return "\n".join(output)
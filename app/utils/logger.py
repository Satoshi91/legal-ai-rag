import logging
import json
from datetime import datetime
from pathlib import Path


class DetailedLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # コンソールハンドラーを設定
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # ファイルハンドラーを設定
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "api_detailed.log", encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # 重複ハンドラーを避けるために既存のハンドラーをクリア
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def log_api_request(self, service: str, operation: str, request_data: dict):
        """API リクエストをログ出力"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "operation": operation,
            "type": "request",
            "data": request_data
        }
        self.logger.info(f"📤 {service.upper()} REQUEST: {json.dumps(log_data, ensure_ascii=False, indent=2)}")
    
    def log_api_response(self, service: str, operation: str, response_data: dict):
        """API レスポンスをログ出力"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "operation": operation,
            "type": "response",
            "data": response_data
        }
        self.logger.info(f"📥 {service.upper()} RESPONSE: {json.dumps(log_data, ensure_ascii=False, indent=2)}")
    
    def log_api_error(self, service: str, operation: str, error_data: dict):
        """API エラーをログ出力"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "operation": operation,
            "type": "error",
            "data": error_data
        }
        self.logger.error(f"❌ {service.upper()} ERROR: {json.dumps(log_data, ensure_ascii=False, indent=2)}")


# シングルトンインスタンス
detailed_logger = DetailedLogger("api_logger")
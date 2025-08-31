#!/usr/bin/env python3
"""
Railway ログ取得スクリプト

Railway CLI を使用してアプリケーションログを取得し、
ローカルファイルに保存するスクリプト
"""

import argparse
import subprocess
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


class RailwayLogFetcher:
    def __init__(self, project_id: Optional[str] = None, service_name: Optional[str] = None):
        self.project_id = project_id
        self.service_name = service_name
        
        # ログ保存ディレクトリ
        self.log_dir = Path("railway_logs")
        self.log_dir.mkdir(exist_ok=True)
    
    def check_railway_cli(self) -> bool:
        """Railway CLI がインストールされているかチェック"""
        try:
            result = subprocess.run(
                ["railway", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Railway CLI not found. Install it with: npm install -g @railway/cli")
            return False
    
    def get_project_info(self) -> Dict[str, Any]:
        """プロジェクト情報を取得"""
        try:
            result = subprocess.run(
                ["railway", "status", "--json"],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get project info: {e}")
            return {}
    
    def fetch_logs(
        self,
        lines: int = 100,
        follow: bool = False,
        deployment_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> str:
        """ログを取得"""
        cmd = ["railway", "logs"]
        
        if lines:
            cmd.extend(["--lines", str(lines)])
        
        if follow:
            cmd.append("--follow")
        
        if deployment_id:
            cmd.extend(["--deployment", deployment_id])
        
        if start_time:
            cmd.extend(["--start", start_time])
        
        if end_time:
            cmd.extend(["--end", end_time])
        
        try:
            print(f"🔄 Fetching logs with command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to fetch logs: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            return ""
    
    def save_logs(self, logs: str, suffix: str = "") -> str:
        """ログをファイルに保存"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"railway_logs_{timestamp}"
        if suffix:
            filename += f"_{suffix}"
        filename += ".log"
        
        log_file = self.log_dir / filename
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"# Railway Logs - {datetime.now().isoformat()}\n")
                f.write(f"# Fetched at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# " + "="*70 + "\n\n")
                f.write(logs)
            
            print(f"📝 Logs saved to: {log_file}")
            return str(log_file)
        except Exception as e:
            print(f"❌ Failed to save logs: {e}")
            return ""
    
    def fetch_and_save_recent_logs(self, lines: int = 200) -> str:
        """最近のログを取得して保存"""
        print(f"🔄 Fetching recent {lines} log lines...")
        logs = self.fetch_logs(lines=lines)
        
        if logs:
            return self.save_logs(logs, "recent")
        return ""
    
    def fetch_and_save_error_logs(self, lines: int = 500) -> str:
        """エラーログを取得して保存"""
        print(f"🔄 Fetching error logs...")
        logs = self.fetch_logs(lines=lines)
        
        if logs:
            # エラーログのみフィルタリング
            error_lines = []
            for line in logs.split('\n'):
                if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'critical']):
                    error_lines.append(line)
            
            if error_lines:
                error_logs = '\n'.join(error_lines)
                return self.save_logs(error_logs, "errors")
            else:
                print("ℹ️  No error logs found")
        return ""
    
    def fetch_and_save_time_range_logs(self, hours_back: int = 1) -> str:
        """指定時間範囲のログを取得"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        start_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        print(f"🔄 Fetching logs from {start_str} to {end_str}")
        logs = self.fetch_logs(
            lines=1000,
            start_time=start_str,
            end_time=end_str
        )
        
        if logs:
            return self.save_logs(logs, f"last_{hours_back}h")
        return ""
    
    def watch_logs(self):
        """リアルタイムでログを監視"""
        print("👀 Watching logs in real-time (Press Ctrl+C to stop)...")
        try:
            subprocess.run([
                "railway", "logs", "--follow"
            ])
        except KeyboardInterrupt:
            print("\n⏹️  Log watching stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Railway ログ取得ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
    python scripts/railway_logs.py --recent 100          # 最近の100行を取得
    python scripts/railway_logs.py --errors              # エラーログのみ取得
    python scripts/railway_logs.py --hours-back 2        # 過去2時間のログを取得
    python scripts/railway_logs.py --watch               # リアルタイム監視
    python scripts/railway_logs.py --lines 500 --save    # 500行取得して保存
"""
    )
    
    parser.add_argument(
        "--recent",
        type=int,
        help="最近のN行のログを取得して保存"
    )
    
    parser.add_argument(
        "--errors",
        action="store_true",
        help="エラーログのみ取得"
    )
    
    parser.add_argument(
        "--hours-back",
        type=int,
        help="指定時間前からのログを取得（時間単位）"
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="リアルタイムでログを監視"
    )
    
    parser.add_argument(
        "--lines",
        type=int,
        default=100,
        help="取得するログ行数 (デフォルト: 100)"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="ログをファイルに保存"
    )
    
    args = parser.parse_args()
    
    # Railway CLI チェック
    fetcher = RailwayLogFetcher()
    if not fetcher.check_railway_cli():
        return 1
    
    # プロジェクト情報表示
    project_info = fetcher.get_project_info()
    if project_info:
        print(f"📊 Project: {project_info.get('project', {}).get('name', 'Unknown')}")
        print(f"🚀 Environment: {project_info.get('environment', {}).get('name', 'Unknown')}")
        print("")
    
    # コマンド実行
    if args.recent:
        fetcher.fetch_and_save_recent_logs(args.recent)
    elif args.errors:
        fetcher.fetch_and_save_error_logs()
    elif args.hours_back:
        fetcher.fetch_and_save_time_range_logs(args.hours_back)
    elif args.watch:
        fetcher.watch_logs()
    elif args.save:
        logs = fetcher.fetch_logs(lines=args.lines)
        if logs:
            fetcher.save_logs(logs, "manual")
    else:
        # デフォルト: コンソールに出力
        logs = fetcher.fetch_logs(lines=args.lines)
        print(logs)
    
    return 0


if __name__ == "__main__":
    exit(main())
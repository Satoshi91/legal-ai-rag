#!/usr/bin/env python3
"""
チャットAPI テストランナー

使用方法:
    python tests/test_runner.py [オプション]

オプション:
    --url URL           APIサーバーのベースURL (デフォルト: http://localhost:8000)
    --test-file FILE    テストケースファイルのパス (デフォルト: tests/test_data/chat_test_cases.json)
    --log-file FILE     ログファイルのパス (デフォルト: tests/logs/chat_test_results.log)
    --verbose           詳細な出力を表示
    --single TEST_NAME  指定したテストケースのみ実行
"""

import asyncio
import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from test_chat_api import ChatAPITester, load_test_cases, format_test_result


class TestRunner:
    def __init__(self, base_url: str, test_file: str, log_file: str, verbose: bool = False):
        self.base_url = base_url
        self.test_file = test_file
        self.verbose = verbose
        
        # ログファイル名にタイムスタンプを追加
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        log_dir = os.path.dirname(log_file)
        log_filename = os.path.basename(log_file)
        log_name, log_ext = os.path.splitext(log_filename)
        timestamped_filename = f"{timestamp}_{log_name}{log_ext}"
        self.log_file = os.path.join(log_dir, timestamped_filename)
        
        # ログディレクトリを作成
        os.makedirs(log_dir, exist_ok=True)
    
    def print_and_log(self, message: str, log_only: bool = False):
        """コンソールとログファイルに出力"""
        if not log_only:
            print(message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    
    async def run_all_tests(self, single_test: str = None):
        """全てのテストを実行"""
        # テストケースを読み込み
        try:
            test_cases = load_test_cases(self.test_file)
        except Exception as e:
            self.print_and_log(f"❌ テストケースファイルの読み込みに失敗: {e}")
            return False
        
        # 特定のテストのみ実行する場合
        if single_test:
            test_cases = [tc for tc in test_cases if tc.get('name') == single_test]
            if not test_cases:
                self.print_and_log(f"❌ テストケース '{single_test}' が見つかりません")
                return False
        
        # ログファイルの初期化
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"チャットAPI テスト結果ログ\n")
            f.write(f"実行開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"対象サーバー: {self.base_url}\n")
            f.write(f"テストケース数: {len(test_cases)}\n")
            f.write("=" * 100 + "\n\n")
        
        self.print_and_log(f"🚀 テスト開始: {len(test_cases)}件のテストケースを実行します")
        self.print_and_log(f"📊 対象サーバー: {self.base_url}")
        self.print_and_log(f"📝 ログファイル: {self.log_file}")
        self.print_and_log("")
        
        # サーバーの健全性チェック
        async with ChatAPITester(self.base_url) as tester:
            if not await tester.health_check():
                self.print_and_log(f"❌ サーバーに接続できません: {self.base_url}")
                self.print_and_log("   サーバーが起動していることを確認してください")
                return False
            
            self.print_and_log("✅ サーバー接続確認完了")
            self.print_and_log("")
            
            # テスト実行統計
            total_tests = len(test_cases)
            passed_tests = 0
            failed_tests = 0
            total_response_time = 0
            
            # 各テストケースを実行
            for i, test_case in enumerate(test_cases, 1):
                test_name = test_case.get('name', f'Test {i}')
                test_description = test_case.get('description', '')
                
                self.print_and_log(f"[{i}/{total_tests}] 実行中: {test_name}")
                if self.verbose and test_description:
                    self.print_and_log(f"    説明: {test_description}")
                
                # テスト実行
                result = await tester.test_chat_endpoint(test_case)
                
                # 結果の統計更新
                if result['success'] and result.get('all_checks_passed', True):
                    passed_tests += 1
                    status = "✅ 成功"
                else:
                    failed_tests += 1
                    status = "❌ 失敗"
                
                total_response_time += result.get('response_time', 0)
                
                # 結果出力
                self.print_and_log(f"    結果: {status} ({result.get('response_time', 0):.2f}秒)")
                
                if not result['success'] or not result.get('all_checks_passed', True):
                    if result.get('error'):
                        self.print_and_log(f"    エラー: {result['error']}")
                    
                    failed_checks = [
                        check for check, passed in result.get('check_results', {}).items() 
                        if not passed
                    ]
                    if failed_checks:
                        self.print_and_log(f"    失敗したチェック: {', '.join(failed_checks)}")
                
                # 詳細ログをファイルに書き込み
                detailed_log = format_test_result(test_name, result, test_case.get('request'))
                self.print_and_log(detailed_log, log_only=True)
                
                if self.verbose:
                    self.print_and_log("")
        
        # 結果サマリー
        self.print_and_log("")
        self.print_and_log("=" * 60)
        self.print_and_log("📊 テスト結果サマリー")
        self.print_and_log("=" * 60)
        self.print_and_log(f"総テスト数: {total_tests}")
        self.print_and_log(f"成功: {passed_tests} ✅")
        self.print_and_log(f"失敗: {failed_tests} ❌")
        self.print_and_log(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        self.print_and_log(f"平均レスポンス時間: {total_response_time/total_tests:.2f}秒")
        self.print_and_log(f"完了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return failed_tests == 0


def main():
    parser = argparse.ArgumentParser(
        description="チャットAPI テストランナー",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--url', 
        default='http://localhost:8000',
        help='APIサーバーのベースURL (デフォルト: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--test-file',
        default='tests/test_data/chat_test_cases.json',
        help='テストケースファイルのパス (デフォルト: tests/test_data/chat_test_cases.json)'
    )
    
    parser.add_argument(
        '--log-file',
        default='tests/logs/chat_test_results.log',
        help='ログファイルのパス (デフォルト: tests/logs/chat_test_results.log)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='詳細な出力を表示'
    )
    
    parser.add_argument(
        '--single',
        help='指定したテストケースのみ実行'
    )
    
    args = parser.parse_args()
    
    # パスを絶対パスに変換
    test_file = os.path.abspath(args.test_file)
    log_file = os.path.abspath(args.log_file)
    
    if not os.path.exists(test_file):
        print(f"❌ テストケースファイルが見つかりません: {test_file}")
        return 1
    
    runner = TestRunner(args.url, test_file, log_file, args.verbose)
    
    try:
        success = asyncio.run(runner.run_all_tests(args.single))
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️  テストが中断されました")
        return 1
    except Exception as e:
        print(f"❌ テスト実行中にエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
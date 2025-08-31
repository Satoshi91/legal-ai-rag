#!/usr/bin/env python3
"""
Railway デプロイ済みアプリのデバッグエンドポイントをテストするスクリプト
"""
import requests
import json
import sys
from datetime import datetime

# Railway app URLを設定
RAILWAY_APP_URL = "https://legal-ai-rag-production.up.railway.app"

def fetch_debug_info():
    """デバッグ情報を取得して表示"""
    debug_endpoint = f"{RAILWAY_APP_URL}/api/v1/debug"
    print(f"🔍 デバッグ情報を取得中...")
    print(f"URL: {debug_endpoint}")
    print("-" * 60)
    
    try:
        response = requests.get(debug_endpoint, timeout=30)
        response.raise_for_status()
        
        debug_data = response.json()
        
        print("✅ デバッグ情報取得成功")
        print(f"取得時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 環境変数設定状況
        print("\n📋 環境変数設定状況:")
        for key, value in debug_data.get("environment_variables", {}).items():
            status = "✅ 設定済み" if value else "❌ 未設定"
            print(f"  {key}: {status}")
        
        # 設定値確認
        print("\n⚙️  設定値:")
        for key, value in debug_data.get("config_values", {}).items():
            print(f"  {key}: {value}")
        
        # 接続テスト結果
        print("\n🔌 接続テスト結果:")
        connection_tests = debug_data.get("connection_tests", {})
        
        # Pinecone接続テスト
        pinecone_test = connection_tests.get("pinecone", {})
        pinecone_status = pinecone_test.get("status", "unknown")
        if pinecone_status == "success":
            print("  🟢 Pinecone: 接続成功")
            index_stats = pinecone_test.get("index_stats", {})
            if index_stats:
                print(f"    - 総ベクトル数: {index_stats.get('total_vector_count', 'N/A')}")
                print(f"    - 次元数: {index_stats.get('dimension', 'N/A')}")
                print(f"    - ネームスペース: {index_stats.get('namespaces', 'N/A')}")
        else:
            print(f"  🔴 Pinecone: 接続失敗 - {pinecone_test.get('error', 'Unknown error')}")
        
        # OpenAI接続テスト
        openai_test = connection_tests.get("openai", {})
        openai_status = openai_test.get("status", "unknown")
        if openai_status == "success":
            print("  🟢 OpenAI: 接続成功")
        elif openai_status == "not_configured":
            print(f"  🟡 OpenAI: 未設定 - {openai_test.get('error', 'No details')}")
        else:
            print(f"  🔴 OpenAI: 接続失敗 - {openai_test.get('error', 'Unknown error')}")
        
        # システム情報
        print("\n💻 システム情報:")
        system_info = debug_data.get("system_info", {})
        for key, value in system_info.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
        
        # 問題の診断
        print("\n🩺 診断結果:")
        env_vars = debug_data.get("environment_variables", {})
        
        issues = []
        if not env_vars.get("OPENAI_API_KEY"):
            issues.append("OpenAI APIキーが設定されていません")
        if not env_vars.get("PINECONE_API_KEY"):
            issues.append("Pinecone APIキーが設定されていません")
        if pinecone_status != "success":
            issues.append("Pinecone接続に失敗しています")
        
        if issues:
            print("⚠️  発見された問題:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ 問題は発見されませんでした")
        
        return debug_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析エラー: {e}")
        print(f"レスポンス内容: {response.text}")
        return None
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return None

def test_health_endpoint():
    """ヘルスエンドポイントもテスト"""
    health_url = f"{RAILWAY_APP_URL}/health"
    print(f"\n🏥 ヘルスチェック: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        response.raise_for_status()
        health_data = response.json()
        print(f"✅ ヘルスチェック成功: {health_data}")
        return True
    except Exception as e:
        print(f"❌ ヘルスチェック失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Railway デバッグ情報取得スクリプト")
    print(f"対象URL: {RAILWAY_APP_URL}")
    print("=" * 60)
    
    # まずヘルスチェック
    if test_health_endpoint():
        # デバッグ情報取得
        debug_info = fetch_debug_info()
        
        if debug_info:
            print(f"\n📄 デバッグ情報をJSONで出力:")
            print(json.dumps(debug_info, indent=2, ensure_ascii=False))
        else:
            print("\n❌ デバッグ情報の取得に失敗しました")
            sys.exit(1)
    else:
        print("\n❌ アプリケーションが正常に動作していません")
        sys.exit(1)
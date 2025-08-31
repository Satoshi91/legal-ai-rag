# Railway ログシステム

このプロジェクトでは、Railway.app での運用に最適化された構造化ログシステムを実装しています。

## 🏗️ 構造化ログの特徴

### JSON形式での出力
すべてのログは JSON 形式で出力され、Railway の Log Explorer で効率的に検索・フィルタリングできます。

```json
{
  "timestamp": "2025-08-31T20:06:23.123456+00:00",
  "level": "info",
  "service": "legal-ai-rag",
  "message": "RAG pipeline start",
  "category": "rag",
  "metadata": {
    "stage": "start",
    "user_query_length": 15,
    "user_query": "契約とは何ですか？"
  }
}
```

### カテゴリ別ログ分類
- **request**: HTTP リクエスト
- **response**: HTTP レスポンス  
- **pinecone**: Pinecone ベクター検索
- **openrouter**: OpenRouter API 呼び出し
- **rag**: RAG パイプライン処理
- **error**: エラー情報
- **system**: システムイベント

## 🔍 Railway でのログ確認方法

### 1. Railway ダッシュボード
- **Observability タブ** → **Log Explorer** でアクセス
- JSON フィールドでの検索・フィルタリングが可能
- リアルタイム監視

### 2. フィルタリング例
```
# Pinecone 関連のログのみ表示
category:"pinecone"

# エラーログのみ表示
level:"error"

# 特定のクエリに関連するログ
metadata.user_query:"契約"

# レスポンス時間が長いログ
metadata.response_time_ms:>5000
```

### 3. 時系列での監視
- RAG パイプラインの各段階を追跡
- API 呼び出しの詳細なタイミング分析
- エラーの根本原因分析

## 🛠️ Railway CLI でのログ取得

### スクリプトの使用
```bash
# Railway CLI が必要
npm install -g @railway/cli
railway login

# 最近の100行を取得して保存
python scripts/railway_logs.py --recent 100

# エラーログのみ取得
python scripts/railway_logs.py --errors

# 過去2時間のログを取得
python scripts/railway_logs.py --hours-back 2

# リアルタイム監視
python scripts/railway_logs.py --watch
```

### 手動でのログ取得
```bash
# 基本的なログ取得
railway logs

# 最近の500行
railway logs --lines 500

# リアルタイム監視
railway logs --follow

# 時間範囲指定
railway logs --start "2025-08-31T12:00:00" --end "2025-08-31T13:00:00"
```

## 📊 ログの活用例

### 1. パフォーマンス監視
```json
{
  "category": "rag",
  "metadata": {
    "stage": "complete",
    "total_time_ms": 6750,
    "context_docs_count": 3
  }
}
```

### 2. API 使用量追跡
```json
{
  "category": "openrouter",
  "metadata": {
    "model": "anthropic/claude-3.5-sonnet",
    "usage": {
      "prompt_tokens": 1250,
      "completion_tokens": 480,
      "total_tokens": 1730
    }
  }
}
```

### 3. 検索品質分析
```json
{
  "category": "pinecone",
  "metadata": {
    "matches_count": 3,
    "top_match_scores": [0.847, 0.723, 0.695]
  }
}
```

## ⚠️ 注意事項

### セキュリティ
- API キーはログに出力されません
- ユーザークエリは100文字で切り詰められます
- 機密情報の漏洩を防ぐためのフィルタリングを実装済み

### パフォーマンス
- 構造化ログは最小限のオーバーヘッドで実装
- Railway の自動ログ処理を活用
- ログレベル調整でノイズを削減

## 🚀 本番環境での推奨設定

### railway.toml 設定
```toml
[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT --log-level info"
```

### 環境変数
```bash
# ログレベル設定
LOGGING_LEVEL=info

# 本番環境では debug レベルは避ける
# LOGGING_LEVEL=debug  # 開発時のみ
```

これにより、Railway 上で効率的にログを監視・分析し、システムの健全性を維持できます。
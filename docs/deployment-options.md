# Railway デプロイメントオプション

このプロジェクトは、Railway Poetry デプロイメント問題の解決策を実装しています。

## オプション1: Poetry + Nixpacks (推奨)

**設定ファイル**: `nixpacks.toml`

```toml
providers = ["python"]

[phases.setup]
nixPkgs = ["poetry"]

[phases.install]
cmds = [
    "pip install poetry==1.8.5",
    "poetry config virtualenvs.create false",
    "poetry config installer.max-workers 10",
    "poetry install --only main --no-interaction --no-ansi -vvv"
]

[start]
cmd = "poetry run uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**特徴**:
- Poetry 1.8.5を明示的にインストール（依存関係解決の問題を回避）
- 並列処理で高速化（max-workers 10）
- 詳細ログ出力（-vvv）
- 固定バージョン依存関係

## オプション2: requirements.txt フォールバック

**設定ファイル**: `nixpacks-fallback.toml`

```toml
providers = ["python"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**使用方法**:
1. 現在のnixpacks.tomlをリネーム: `mv nixpacks.toml nixpacks-poetry.toml`
2. フォールバック設定を有効化: `mv nixpacks-fallback.toml nixpacks.toml`
3. デプロイ

**特徴**:
- 確実性が高い
- ビルド時間短縮
- Poetry依存関係解決問題を回避

## Railway設定

### 環境変数
- `PYTHON_VERSION=3.9`
- `POETRY_VERSION=1.8.5`
- その他API key等

### デプロイ設定 (railway.toml)
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "poetry run uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

## トラブルシューティング

1. **Poetry依存関係解決タイムアウト** → オプション2（requirements.txt）を使用
2. **Poetry コマンド未検出** → nixpacks.tomlでPoetry 1.8.5を明示的インストール
3. **Nixガベージコレクション失敗** → フォールバック方式を使用

## 参考資料
- [Railway Poetry デプロイメント トラブルシューティングガイド](./railway-poetry-deployment-troubleshooting.md)
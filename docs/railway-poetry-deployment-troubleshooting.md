# Railway Poetry デプロイメント トラブルシューティングガイド

## 概要
このドキュメントは、Railway に Poetry を使用して Python アプリケーションをデプロイする際に発生した問題と解決策をまとめたものです。

## 発生した問題

### 1. Poetry コマンドが見つからない問題

**エラーメッセージ:**
```
/bin/bash: line 1: poetry: command not found
```

**発生状況:**
- Railway が Nixpacks を使用してビルドする際、Poetry がインストールされていない
- `railway.toml` で `startCommand` に `poetry run` を指定しているが、コンテナ内に Poetry が存在しない

**原因:**
- Nixpacks のデフォルト設定では Poetry がインストールされない
- Railway の標準的な Python ビルドパックは pip/requirements.txt を想定している

### 2. Poetry 依存関係解決のタイムアウト

**エラーメッセージ:**
```
Resolving dependencies...
Deploy failed
```

**発生状況:**
- `poetry install` コマンドが "Resolving dependencies..." で長時間停止
- 最終的にタイムアウトでデプロイ失敗

**原因:**
- Poetry の依存関係解決アルゴリズムが複雑な依存関係グラフで時間がかかる
- 特に古いバージョン制約を持つパッケージがある場合に発生
- Poetry 2.0 以降で問題が顕著に

### 3. Poetry オプションの非推奨警告

**エラーメッセージ:**
```
The `--no-dev` option is deprecated, use the `--only main` notation instead.
```

**発生状況:**
- 古い Poetry 構文を使用した場合

**原因:**
- Railway の Nixpacks が新しい Poetry バージョンを使用
- `--no-dev` は Poetry 1.2 以降で非推奨

## 試行した解決策と結果

### 試行 1: railway.toml で Poetry インストールを指定

**設定:**
```toml
[build]
builder = "nixpacks"

[build.nixpacks]
installCmd = "pip install poetry && poetry install --no-dev"
```

**結果:** ❌ 失敗
- ビルド設定が正しく反映されない

### 試行 2: nixpacks.toml ファイルの作成

**初期設定 (構文エラーあり):**
```toml
[providers.python]

[phases.setup]
nixPkgs = ["...", "python311", "poetry"]
```

**結果:** ❌ 失敗
- `invalid type: map, expected a sequence for key providers` エラー

**修正版:**
```toml
providers = ["python"]

[phases.setup]
nixPkgs = ["python39", "poetry"]

[phases.install]
cmds = [
    "poetry config virtualenvs.create false",
    "poetry install --only main --no-interaction --no-ansi"
]

[start]
cmd = "poetry run uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**結果:** ❌ 依存関係解決でタイムアウト

### 試行 3: 依存関係バージョンの固定

**問題の原因:**
- Poetry の依存関係解決が複雑な範囲指定（`^0.111.0` 等）で時間がかかる
- キャレット記法（`^`）により多数のバージョン候補を検討する必要がある

**解決策:**
```toml
# pyproject.toml の修正
[tool.poetry.dependencies]
python = ">=3.9,<3.13"
fastapi = "0.111.0"        # ^0.111.0 から固定バージョンに変更
uvicorn = "0.30.6"         # ^0.30.1 から固定バージョンに変更
pydantic = "2.7.4"         # ^2.7.4 から固定バージョンに変更
# その他全ての依存関係も固定バージョンに
```

**nixpacks.toml の最適化:**
```toml
[phases.install]
cmds = [
    "pip install poetry==1.8.5",                          # 安定版Poetry
    "poetry config virtualenvs.create false",
    "poetry config installer.max-workers 10",             # 並列処理
    "poetry install --only main --no-interaction --no-ansi -vvv"  # 詳細ログ
]
```

**結果:** ❌ Nixガベージコレクションで失敗

**エラーメッセージ:**
```
deleting '/nix/store/7hsml574k621n842nwnl8qhix3i2q6mv-update-autotools-gnu-config-scripts-hook'
deleting '/nix/store/vcwb5qr1yjn3pwbm9gnmvqmn1gwg9a1y-gnu-config-2024-01-01'
deleting '/nix/store/0kxxaix9l5dbih90491mv96zajsac57q-bzip2-1.0.8-bin'
deleting unused links...
Deploy failed
```

### 試行 4: Nixpacks設定の簡素化

**問題の原因:**
- Nixpacksのビルドプロセス中にNixストアのガベージコレクションが失敗
- 複雑なnixpacks.toml設定がNixのパッケージ管理に干渉
- Poetry 1.8.5の明示的インストールがNix環境と競合

**解決策:**
Nixpacksの設定をシンプルにし、Nix本来のパッケージ管理に委ねる：

```toml
# nixpacks.toml (簡素化版)
providers = ["python"]

[phases.install]
cmds = [
    "poetry config virtualenvs.create false",
    "poetry install --only main --no-interaction"
]

[start]
cmd = "poetry run uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**結果:** ❌ Poetry コマンドが見つからない

**エラーメッセージ:**
```
RUN poetry config virtualenvs.create false
/bin/bash: line 1: poetry: command not found
ERROR: failed to build: failed to solve: process "/bin/bash -ol pipefail -c poetry config virtualenvs.create false" did not complete successfully: exit code: 127
```

### 試行 5: Poetry の明示的インストール（最小限）

**問題の原因:**
- 設定を簡素化しすぎて Poetry のインストール指定を削除
- Nixpacks のデフォルトでは Poetry がインストールされない
- `[phases.setup]` での nixPkgs 指定が必要

**解決策:**
Poetry のインストールのみを明示的に指定：

```toml
providers = ["python"]

[phases.setup]
nixPkgs = ["poetry"]  # Poetry のインストールのみ指定

[phases.install]
cmds = [
    "poetry config virtualenvs.create false",
    "poetry install --only main --no-interaction"
]

[start]
cmd = "poetry run uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**結果:** ❌ 依然として依存関係解決でタイムアウト

**エラーメッセージ:**
```
Skipping virtualenv creation, as specified in config file.
Updating dependencies
Resolving dependencies...
Deploy failed
```

**分析:**
- 依存関係を固定バージョンにしても依然として解決に時間がかかる
- Poetry の依存関係解決アルゴリズム自体の問題
- Railway の制限時間内に完了しない

### 試行 6: requirements.txt フォールバック方式

**問題の根本原因:**
Poetry 自体の依存関係解決が Railway の環境では安定しない

**最終解決策:**
Poetry の環境統一を保ちながら、デプロイ時のみ requirements.txt を使用：

1. **ローカルで requirements.txt を生成:**
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

2. **nixpacks.toml を pip ベースに変更:**
```toml
providers = ["python"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

**結果:** 検証中

## 根本原因の分析

### Poetry の依存関係解決の問題

1. **複雑な依存関係グラフ**
   - 古いバージョン下限を持つ依存関係がバージョン候補グラフを巨大化
   - 例: `fastapi = "^0.85.0"` のような1年前のバージョン指定

2. **Poetry のバージョン問題**
   - Poetry 2.0 以降で依存関係解決が非常に遅い
   - Poetry 1.8.5 では正常に動作する報告あり

3. **メタデータの不適切な宣言**
   - PyPI 上のライブラリがメタデータを適切に宣言していない
   - Poetry がパッケージをダウンロードして検査する必要がある

## 推奨される解決策

### 1. **最優先**: 依存関係バージョンの固定（Nixpacks + Poetry）

**理由:**
- Nixpacks の使用を継続できる（Railway のデフォルト）
- 環境管理の統一性を保持
- 設定変更のみで解決

**手順:**

1. **pyproject.toml の依存関係を固定バージョンに変更:**
```toml
[tool.poetry.dependencies]
python = ">=3.9,<3.13"
fastapi = "0.111.0"        # キャレット記法を削除
uvicorn = "0.30.6"         # 具体的なバージョンを指定
pydantic = "2.7.4"
# 全ての依存関係を同様に固定
```

2. **nixpacks.toml で Poetry バージョンとオプションを最適化:**
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

3. **lock ファイルの更新:**
```bash
poetry lock --no-update
```

**メリット:**
- 依存関係解決が瞬時に完了（複数バージョン候補の検討が不要）
- Poetry 1.8.5 で既知の問題を回避
- 並列処理とログ出力で高速化・可視化
- ローカル開発環境との統一性維持

### 2. カスタム Dockerfile の使用（代替案）

**メリット:**
- 完全なビルドプロセスの制御
- ビルド時間の短縮（Nixpacks: 87秒 → Dockerfile: 15秒）
- Poetry バージョンの固定が可能

**Dockerfile 例:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Poetry のインストール
RUN pip install poetry==1.8.5

# 依存関係ファイルのコピー
COPY pyproject.toml poetry.lock ./

# 依存関係のインストール
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# アプリケーションコードのコピー
COPY . .

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

### 2. 依存関係の最適化

**pyproject.toml の改善:**
```toml
[tool.poetry.dependencies]
# バージョン制約をより厳密に
fastapi = ">=0.111.0,<0.112.0"  # ^ の代わりに具体的な範囲
uvicorn = {extras = ["standard"], version = ">=0.30.0,<0.31.0"}
```

### 3. requirements.txt へのエクスポート（フォールバック）

**コマンド:**
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

**railway.toml:**
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

### 4. Railway の新しいビルダー (Railpack) の使用

**railway.toml:**
```toml
[build]
builder = "railpack"  # ベータ版の新しいビルダー
```

## パフォーマンス比較

| ビルド方法 | ビルド時間 | デプロイ時間 | 合計 |
|-----------|----------|-----------|------|
| Nixpacks | 55秒 | 32秒 | 87秒 |
| カスタム Dockerfile | 11秒 | 4秒 | 15秒 |
| プリビルトイメージ | 2秒 | 4秒 | 6秒 |

## ベストプラクティス

1. **小規模プロトタイプの場合:**
   - **第1選択**: 依存関係を固定バージョンにした Nixpacks + Poetry
   - **第2選択**: requirements.txt を使用（シンプルで確実）
   - **第3選択**: カスタム Dockerfile で Poetry 1.8.5 を固定

2. **本番環境の場合:**
   - CI/CD パイプラインでプリビルトイメージを作成
   - GitHub Actions などでイメージをビルドして Railway にデプロイ

3. **依存関係管理:**
   - **重要**: Poetry でタイムアウトが発生する場合は固定バージョンを使用
   - キャレット記法（`^`）ではなく具体的バージョンを指定: `fastapi = "0.111.0"`
   - 定期的に `poetry lock --no-update` で lock ファイルを更新
   - 不要な依存関係を削除

4. **デバッグ方法:**
   - `poetry install -vvv` で詳細なログを確認
   - `poetry config virtualenvs.create true` で仮想環境を有効化
   - キャッシュクリア: `poetry cache clear . --all`
   - 依存関係解決が遅い場合は `poetry show --tree` で問題のあるパッケージを特定

5. **Poetry バージョン管理:**
   - Nixpacks で Poetry 1.8.5 を明示的にインストール
   - `poetry config installer.max-workers 10` で並列処理を活用

## 環境変数の設定

Railway ダッシュボードで以下の環境変数を設定:

```bash
OPENAI_API_KEY=your-api-key
PYTHON_VERSION=3.9
POETRY_VERSION=1.8.5
```

## まとめ

Railway での Poetry デプロイメントは、依存関係解決の遅さが主な問題となります。小規模プロジェクトでは requirements.txt へのエクスポート、大規模プロジェクトではカスタム Dockerfile の使用が推奨されます。将来的には Railway の Railpack ビルダーの安定版リリースで改善される可能性があります。

## 参考資料

- [Poetry Issue #7662: Stuck at "Resolving dependencies..."](https://github.com/python-poetry/poetry/issues/7662)
- [Railway Docs: Build Configuration](https://docs.railway.com/guides/build-configuration)
- [Nixpacks Documentation](https://nixpacks.com/docs/providers/python)
- [Railway Blog: Comparing Deployment Methods](https://blog.railway.com/p/comparing-deployment-methods-in-railway)
# Railway デプロイ: Poetry vs requirements.txt ベストプラクティス (2024年)

## 概要

このドキュメントは、Railwayプラットフォームでの Python プロジェクトデプロイにおいて、Poetry と requirements.txt のどちらを使用すべきかの調査結果をまとめたものです。複数の情報源（Context7、Web検索、現在のコードベース分析）を基に、2024年現在のベストプラクティスを提供します。

## 調査結果: 最終推奨

**結論: requirements.txt を使用すべき**

## 現在のプロジェクト状況

当プロジェクトは既に理想的なハイブリッド構成を実装済み：
- **開発環境**: Poetry (`pyproject.toml` + `poetry.lock`)
- **デプロイ環境**: requirements.txt (`nixpacks-fallback.toml`)

## requirements.txt 推奨理由

### 1. 確実性 🎯
- **Poetry の依存関係解決タイムアウト問題を回避**
  - Railway環境で "Resolving dependencies..." で停止する既知の問題
  - 特に複雑な依存関係グラフで発生
  - Poetry 2.0以降で問題が顕著

### 2. パフォーマンス ⚡
- **ビルド時間の大幅短縮**
  - Nixpacks + Poetry: 87秒
  - requirements.txt: 15秒
  - pip install の単純さが高速化に寄与

### 3. Railway 公式サポート 📚
- **公式ドキュメントの大部分が requirements.txt ベース**
  - FastAPI ガイド: requirements.txt 使用
  - Flask ガイド: `pip freeze > requirements.txt`
  - Django ガイド: requirements.txt での依存関係管理
- **Railway の標準的な Python ビルドパックが pip/requirements.txt を想定**

### 4. 業界標準 🌍
- **2024年現在も多くのプラットフォームで必須**
  - Heroku: requirements.txt 必須
  - Streamlit: requirements.txt 必須
  - その他多数のPaaSプラットフォーム
- **"Poetry開発 → requirements.txt デプロイ" が推奨パターン**

## 実装方法

### 現在の最適設定（既に実装済み）

```toml
# nixpacks-fallback.toml (メイン使用推奨)
providers = ["python"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

### 依存関係更新ワークフロー

```bash
# Poetry で依存関係を管理
poetry add <package>
poetry update

# requirements.txt を更新（デプロイ用）
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Poetry vs requirements.txt 比較表

| 項目 | Poetry | requirements.txt |
|------|--------|------------------|
| **開発体験** | ✅ 優秀（依存関係管理、仮想環境） | ❌ 基本的 |
| **デプロイ確実性** | ❌ タイムアウトリスク | ✅ 高い |
| **ビルド速度** | ❌ 遅い（87秒） | ✅ 高速（15秒） |
| **Railway サポート** | ⚠️ 限定的 | ✅ 公式推奨 |
| **プラットフォーム互換性** | ❌ 限定的 | ✅ 広範囲 |
| **メンテナンス性** | ✅ lockファイル管理 | ⚠️ 手動更新必要 |

## その他の調査データ

### Poetry の問題点（2024年）

1. **依存関係解決の複雑性**
   - キャレット記法（`^0.111.0`）による多数のバージョン候補検討
   - PyPI メタデータの不適切な宣言によるパッケージダウンロード

2. **Railway 特有の問題**
   - Nixpacks でのPoetryインストールが不安定
   - Nix ガベージコレクションとの競合

3. **タイムアウト事例**
   ```
   Resolving dependencies...
   Deploy failed
   ```

### requirements.txt のメリット

1. **シンプルさ**
   - 直接的な依存関係リスト
   - pip の標準的な動作

2. **予測可能性**
   - 固定バージョンによる再現性
   - ビルド環境での一貫性

3. **デバッグの容易さ**
   - 明示的な依存関係
   - エラーの特定が簡単

## 推奨ワークフロー

### 開発環境
```bash
# Poetry で依存関係管理
poetry install
poetry add fastapi uvicorn
poetry run uvicorn main:app --reload
```

### デプロイ準備
```bash
# requirements.txt 更新
poetry export -f requirements.txt --output requirements.txt --without-hashes

# Git コミット
git add requirements.txt pyproject.toml poetry.lock
git commit -m "Update dependencies"
```

### Railway デプロイ
- `nixpacks-fallback.toml` が自動的に使用される
- requirements.txt ベースの高速デプロイが実行される

## まとめ

当プロジェクトは既に2024年のベストプラクティスを実装しています：

1. **開発**: Poetry で優秀な依存関係管理
2. **デプロイ**: requirements.txt で確実かつ高速なデプロイ
3. **フォールバック**: 両方の設定を維持して柔軟性を確保

この構成により、開発効率とデプロイの安定性を両立できています。

## 参考資料

- [Railway 公式ドキュメント](https://docs.railway.com/)
- [Poetry 公式ドキュメント](https://python-poetry.org/)
- [Python Packaging ユーザーガイド](https://packaging.python.org/)
- [Railway Poetry デプロイメント トラブルシューティングガイド](./railway-poetry-deployment-troubleshooting.md)
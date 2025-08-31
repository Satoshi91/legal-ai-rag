# チャットAPI テストシステム

FastAPIサーバーのチャットエンドポイントを効率的にテストするためのツールです。

## ファイル構成

```
tests/
├── README.md                     # このファイル
├── test_runner.py               # メインのテスト実行スクリプト
├── test_chat_api.py            # APIテスト用のユーティリティ
├── test_data/
│   └── chat_test_cases.json    # テストケース定義
└── logs/
    └── YYYY-MM-DD_HHMMSS_chat_test_results.log   # 実行結果ログ（実行時刻付き）
```

## 使用方法

### 1. サーバー起動
まず、FastAPIサーバーを起動してください：

```bash
# メインディレクトリから
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# または仮想環境を有効化してから
poetry shell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. テスト実行

#### 全テストケースを実行
```bash
poetry run python tests/test_runner.py
```

#### 特定のテストケースのみ実行
```bash
poetry run python tests/test_runner.py --single "基本的な法律質問"
```

#### 詳細な出力を表示
```bash
poetry run python tests/test_runner.py --verbose
```

#### 異なるサーバーURLを指定
```bash
poetry run python tests/test_runner.py --url http://localhost:3000
```

### 3. ログ確認
テスト結果は実行時刻付きのログファイルに保存されます：
- `tests/logs/YYYY-MM-DD_HHMMSS_chat_test_results.log`

例：`tests/logs/2025-08-31_194821_chat_test_results.log`

各実行ごとに新しいログファイルが作成されるため、過去の実行結果も保持されます。

## テストケース

現在以下のテストケースが定義されています：

1. **基本的な法律質問** - 民法に関する基本的な質問
2. **会話履歴を含む質問** - 複数ターンの会話
3. **具体的な条文に関する質問** - 特定の法律条文について
4. **実務的な法律相談** - 実際の法的問題に関する質問
5. **商法に関する質問** - 商法の基本概念について
6. **短い質問** - 簡潔な質問に対する回答
7. **複雑な法的概念** - 複雑な法律概念の説明

## テストケースの追加

`tests/test_data/chat_test_cases.json` ファイルを編集して新しいテストケースを追加できます。

### テストケースの形式

```json
{
  "name": "テスト名",
  "description": "テストの説明",
  "request": {
    "messages": [
      {
        "role": "user",
        "content": "質問内容"
      }
    ],
    "max_context_docs": 3
  },
  "expected_checks": {
    "contains_japanese": true,
    "response_length_min": 50,
    "should_contain": ["キーワード1", "キーワード2"]
  }
}
```

### チェック項目

- `contains_japanese`: レスポンスに日本語が含まれているか
- `response_length_min`: レスポンスの最小文字数
- `should_contain`: レスポンスに含まれるべきキーワードの配列

## トラブルシューティング

### サーバー接続エラー
```
❌ サーバーに接続できません: http://localhost:8000
```
- FastAPIサーバーが起動していることを確認
- ポート番号が正しいか確認
- `--url` オプションで正しいURLを指定

### テストケースファイルが見つからない
```
❌ テストケースファイルが見つかりません
```
- `tests/test_data/chat_test_cases.json` ファイルが存在することを確認
- `--test-file` オプションで正しいパスを指定

## 出力例

```
🚀 テスト開始: 7件のテストケースを実行します
📊 対象サーバー: http://localhost:8000
📝 ログファイル: tests/logs/chat_test_results.log

✅ サーバー接続確認完了

[1/7] 実行中: 基本的な法律質問
    結果: ✅ 成功 (2.45秒)
[2/7] 実行中: 会話履歴を含む質問  
    結果: ✅ 成功 (3.12秒)
...

============================================================
📊 テスト結果サマリー
============================================================
総テスト数: 7
成功: 7 ✅
失敗: 0 ❌
成功率: 100.0%
平均レスポンス時間: 2.84秒
完了時刻: 2024-01-XX XX:XX:XX
```
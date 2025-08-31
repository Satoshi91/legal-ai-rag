# 法令AIチャットAPI使用方法

## エンドポイント
```
POST /chat
```

## リクエスト形式

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "messages": [
    {
      "role": "user",
      "content": "労働基準法について教えてください"
    },
    {
      "role": "assistant", 
      "content": "労働基準法は労働条件の最低基準を定めた法律です..."
    },
    {
      "role": "user",
      "content": "残業時間の上限について詳しく知りたいです"
    }
  ],
  "max_context_docs": 5
}
```

### パラメータ
- `messages` (array, 必須): 会話履歴の配列
  - `role` (string): "user" または "assistant"
  - `content` (string): メッセージ内容
- `max_context_docs` (integer, オプション): コンテキストとして使用する文書数（デフォルト: 3）

## レスポンス形式

### 成功時 (200 OK)
```json
{
  "user_query": "契約とは何ですか？",
  "ai_response": "契約とは、法律上の合意を指し、特定の内容に基づいて当事者間で義務や権利を生じさせるものです。日本の民法第522条によれば、契約は一方の当事者が契約内容を示して申し入れ（申込み）を行い、相手方がそれを承諾することで成立します。ここで重要なのは、契約が成立するためには、特別な法律の定めがない限り、書面を作成する必要はないという点です。つまり、口頭での合意でも契約は成立します。\n\n具体的な例として、友人との間で「来週の土曜日に一緒に映画を見に行こう」と約束する場合、これは日常的な約束であり、法律上の契約とはみなされません。しかし、例えば「あなたが私の家のペンキを塗ってくれたら、1万円を支払います」といった合意は、民法第632条に基づく請負契約として法律上の契約となります。この場合、ペンキを塗るという仕事を完成することと、その結果に対して報酬を支払うことが約束されているためです。\n\n注意事項として、契約内容が法律に違反していたり、公序良俗に反する場合は無効となることがあります。また、政府契約のように特別な法律が適用される場合もあります（政府契約の支払遅延防止等に関する法律第2条）。\n\n実践的なアドバイスとしては、重要な契約はできるだけ書面に残し、双方が内容を確認し合意した証拠を持つことが望ましいです。これにより、後々のトラブルを防ぐことができます。",
  "context_documents": [
    {
      "document": "第五百二十二条\n契約は、契約の内容を示してその締結を申し入れる意思表示（以下「申込み」という。）に対して相手方が承諾をしたときに成立する。\n２\n                  契約の成立には、法令に特別の定めがある場合を除き、書面の作成その他の方式を具備することを要しない。",
      "similarity_score": 0.46674638999999996,
      "metadata": {
        "ArticleNum": 522,
        "ArticleTitle": "第五百二十二条",
        "LawID": "129AC0000000089",
        "LawTitle": "民法",
        "LawType": "Act",
        "filename": "129AC0000000089_20250606_507AC0000000057.xml",
        "original_text": "",
        "revisionID": "507AC0000000057",
        "updateDate": "20250606"
      }
    },
    {
      "document": "第二条\nこの法律において「政府契約」とは、国を当事者の一方とする契約で、国以外の者のなす工事の完成若しくは作業その他の役務の給付又は物件の納入に対し国が対価の支払をなすべきものをいう。",
      "similarity_score": 0.452919453,
      "metadata": {
        "ArticleNum": 2,
        "ArticleTitle": "第二条",
        "LawID": "324AC1000000256",
        "LawTitle": "政府契約の支払遅延防止等に関する法律",
        "LawType": "Act",
        "filename": "324AC1000000256_20191216_501AC0000000016.xml",
        "original_text": "",
        "revisionID": "501AC0000000016",
        "updateDate": "20191216"
      }
    }
  ],
  "total_context_docs": 3
}
```

### エラー時 (500 Internal Server Error)
```json
{
  "detail": "エラーメッセージ"
}
```

## 使用例

### JavaScript/TypeScript
```javascript
const chatWithLegalAI = async (messages, maxContextDocs = 3) => {
  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages,
        max_context_docs: maxContextDocs
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Legal Chat API error:', error);
    throw error;
  }
};

// 使用例1: 基本的な質問
const basicMessages = [
  { role: 'user', content: '労働基準法について教えてください' }
];

chatWithLegalAI(basicMessages)
  .then(response => {
    console.log('AI回答:', response.ai_response);
    console.log('関連条文数:', response.total_context_docs);
  });

// 使用例2: 会話履歴を含む質問
const conversationMessages = [
  { role: 'user', content: '労働基準法について教えてください' },
  { role: 'assistant', content: '労働基準法は労働条件の最低基準を定めた法律です...' },
  { role: 'user', content: '残業代の計算方法について詳しく教えてください' }
];

chatWithLegalAI(conversationMessages, 5)
  .then(response => {
    console.log('AI回答:', response.ai_response);
    console.log('参照された条文:', response.context_documents);
  });
```

### React Hook例
```javascript
import { useState } from 'react';

export const useLegalChatAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);

  const sendMessage = async (message, maxContextDocs = 3) => {
    setLoading(true);
    setError(null);

    const newMessage = { role: 'user', content: message };
    const messages = [...conversationHistory, newMessage];

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages,
          max_context_docs: maxContextDocs
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      // 会話履歴を更新
      const assistantMessage = { role: 'assistant', content: data.ai_response };
      setConversationHistory([...messages, assistantMessage]);
      
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = () => {
    setConversationHistory([]);
  };

  return { 
    sendMessage, 
    loading, 
    error, 
    conversationHistory,
    clearConversation
  };
};

// 使用例
const LegalChatComponent = () => {
  const { sendMessage, loading, conversationHistory } = useLegalChatAPI();
  const [inputMessage, setInputMessage] = useState('');

  const handleSend = async () => {
    try {
      const response = await sendMessage(inputMessage, 5);
      console.log('回答:', response.ai_response);
      setInputMessage('');
    } catch (error) {
      console.error('送信エラー:', error);
    }
  };

  return (
    <div>
      {/* チャット履歴表示 */}
      {conversationHistory.map((msg, index) => (
        <div key={index} className={`message ${msg.role}`}>
          {msg.content}
        </div>
      ))}
      
      {/* 入力フォーム */}
      <input 
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        disabled={loading}
        placeholder="法律に関する質問を入力してください"
      />
      <button onClick={handleSend} disabled={loading}>
        {loading ? '送信中...' : '送信'}
      </button>
    </div>
  );
};
```

## レスポンスフィールド説明

### 基本フィールド
- `user_query`: 送信されたユーザーの最新質問（messagesの最後のuserメッセージ）
- `ai_response`: AIが生成した法律専門回答
- `total_context_docs`: 使用されたコンテキスト文書の総数

### コンテキスト文書（`context_documents`）
- `document`: 参照された法令条文の内容
- `similarity_score`: 質問との類似度スコア（0.0-1.0）
- `metadata`: 文書の詳細情報
  - `ArticleNum`: 条文番号（数値）
  - `ArticleTitle`: 条文タイトル
  - `LawID`: 法律ID
  - `LawTitle`: 法律名
  - `LawType`: 法律種別（Act等）
  - `filename`: ファイル名
  - `original_text`: 元のテキスト（通常空文字列）
  - `revisionID`: 改訂ID
  - `updateDate`: 更新日

## エラーハンドリング

### よくあるエラーケース
1. **不正なリクエスト形式** (422)
   - messagesが空の場合
   - roleが"user"または"assistant"以外の場合
2. **内部サーバーエラー** (500)
   - 検索サービスエラー
   - AI応答生成エラー

各エラーには適切な日本語メッセージが含まれます。

## 実装時の注意点

### 会話履歴の扱い
- APIは会話履歴全体を受け取り、最新のuserメッセージに対して回答を生成します
- 過去の会話内容もコンテキストとしてAI回答の生成に活用されます
- フロントエンド側で会話履歴の管理を行ってください

### パフォーマンス
- `max_context_docs`を適切に設定することで、レスポンス時間を調整できます
- 会話が長くなる場合は、古い履歴を削除することを検討してください
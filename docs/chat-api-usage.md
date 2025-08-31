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
  "user_query": "残業時間の上限について詳しく知りたいです",
  "ai_response": "労働基準法では、時間外労働の上限について以下のように定められています...",
  "context_documents": [
    {
      "document": "労働基準法第三十六条　使用者は、当該事業場に、労働者の過半数で組織する労働組合がある場合においてはその労働組合...",
      "similarity_score": 0.89,
      "metadata": {
        "law_name": "労働基準法",
        "article": "第36条",
        "title": "時間外及び休日の労働",
        "category": "労働法"
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
  - `law_name`: 法律名
  - `article`: 条文番号（文字列または数値）
  - `title`: 条文タイトル
  - `category`: 法律カテゴリ

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
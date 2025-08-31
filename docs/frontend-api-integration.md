# フロントエンド API連携ガイド

## 環境変数設定

### Vercel設定
```bash
NEXT_PUBLIC_API_URL=https://your-app-production.up.railway.app
```

## API呼び出し実装

### React/Next.js の場合

```javascript
// lib/api.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export const chatWithAI = async (message) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        // その他必要なパラメータ
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Chat API error:', error);
    throw error;
  }
};

export const searchDocuments = async (query) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        // その他検索パラメータ
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Search API error:', error);
    throw error;
  }
};
```

### React コンポーネントでの使用例

```javascript
// components/ChatInterface.jsx
import { useState } from 'react';
import { chatWithAI } from '../lib/api';

export default function ChatInterface() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await chatWithAI(message);
      setResponse(result.response || result.message);
    } catch (error) {
      setResponse('エラーが発生しました: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <form onSubmit={handleSubmit}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="質問を入力してください..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !message.trim()}>
          {loading ? '送信中...' : '送信'}
        </button>
      </form>
      
      {response && (
        <div className="response">
          <h3>回答:</h3>
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}
```

### Vue.js の場合

```javascript
// composables/useApi.js
export const useApi = () => {
  const API_BASE_URL = process.env.VITE_API_URL;

  const chatWithAI = async (message) => {
    try {
      const response = await $fetch(`${API_BASE_URL}/api/v1/chat`, {
        method: 'POST',
        body: { message }
      });
      return response;
    } catch (error) {
      console.error('Chat API error:', error);
      throw error;
    }
  };

  return { chatWithAI };
};
```

## エラーハンドリング

```javascript
// lib/errorHandler.js
export const handleApiError = (error) => {
  if (error.response) {
    // サーバーがエラーレスポンスを返した場合
    switch (error.response.status) {
      case 400:
        return 'リクエストが正しくありません';
      case 401:
        return '認証が必要です';
      case 403:
        return 'アクセスが拒否されました';
      case 404:
        return 'APIエンドポイントが見つかりません';
      case 500:
        return 'サーバーエラーが発生しました';
      default:
        return `エラー: ${error.response.status}`;
    }
  } else if (error.request) {
    // ネットワークエラー
    return 'ネットワークエラーが発生しました';
  } else {
    // その他のエラー
    return '予期しないエラーが発生しました';
  }
};
```

## ヘルスチェック機能

```javascript
// lib/healthCheck.js
export const checkApiHealth = async () => {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
    return response.ok;
  } catch (error) {
    return false;
  }
};

// アプリ起動時にAPIの可用性をチェック
export const initializeApp = async () => {
  const isHealthy = await checkApiHealth();
  if (!isHealthy) {
    console.warn('Backend API is not available');
    // ユーザーに通知または代替手段を提供
  }
  return isHealthy;
};
```

## TypeScript型定義

```typescript
// types/api.ts
export interface ChatRequest {
  message: string;
  context?: string;
}

export interface ChatResponse {
  response: string;
  sources?: string[];
  timestamp: string;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  threshold?: number;
}

export interface SearchResponse {
  results: Array<{
    content: string;
    metadata: Record<string, any>;
    score: number;
  }>;
  total: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
```

## 開発時のプロキシ設定

### Next.js (next.config.js)
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return process.env.NODE_ENV === 'development' ? [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ] : [];
  },
};

module.exports = nextConfig;
```

### Vite (vite.config.js)
```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```
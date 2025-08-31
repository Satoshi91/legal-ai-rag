from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("🚀 Starting Legal AI RAG API...")

app = FastAPI(
    title="Legal AI RAG API",
    description="API for Legal AI RAG System",
    version="0.1.0"
)

print("✅ FastAPI app created successfully")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-app.vercel.app",  # あなたのVercelドメインに変更
        "http://localhost:3000",  # ローカル開発用
        "http://localhost:5173",  # Vite開発用
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

print("✅ CORS middleware added")

# ルーターを追加（エラーハンドリング強化）
try:
    from app.routers import debug
    app.include_router(debug.router, prefix="/api/v1")
    print("✅ Debug router loaded successfully")
except Exception as e:
    print(f"⚠️ Failed to load debug router: {e}")

try:
    from app.routers import search, chat
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    print("✅ Main routers loaded successfully")
except Exception as e:
    print(f"⚠️ Failed to load main routers: {e}")
    # メインルーター読み込み失敗でも起動は継続


@app.get("/")
async def root():
    return {"message": "Welcome to Legal AI RAG API"}


@app.get("/health")
async def health_check():
    """シンプルなヘルスチェック"""
    return {
        "status": "healthy",
        "service": "Legal AI RAG API",
        "version": "0.1.0"
    }
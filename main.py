from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search, chat
from app.services.vector_store import vector_store
from app.models.schemas import HealthResponse

app = FastAPI(
    title="Legal AI RAG API",
    description="API for Legal AI RAG System",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを追加
app.include_router(search.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to Legal AI RAG API"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        vector_info = vector_store.get_collection_info()
        return HealthResponse(
            status="healthy", 
            vector_store_info=vector_info
        )
    except Exception as e:
        return HealthResponse(
            status="healthy",
            vector_store_info={"error": str(e)}
        )
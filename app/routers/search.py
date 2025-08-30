from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest, SearchResponse, SearchResult, DocumentMetadata
from app.services.search import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """法律文書を検索"""
    try:
        # 検索実行
        results = await search_service.search_documents(
            query=request.query,
            n_results=request.max_results
        )
        
        # レスポンス形式に変換
        search_results = []
        for result in results:
            search_result = SearchResult(
                document=result["document"],
                similarity_score=result["similarity_score"],
                metadata=DocumentMetadata(**result["metadata"])
            )
            search_results.append(search_result)
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
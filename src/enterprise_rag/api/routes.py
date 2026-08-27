from fastapi import APIRouter, Depends, HTTPException

from enterprise_rag.api.dependencies import build_rag_service
from enterprise_rag.api.models import (
    QueryRequest,
    QueryResponse,
    SourceResponse,
)
from enterprise_rag.rag.service import RAGService


router = APIRouter(
    prefix="/api/v1",
    tags=["rag"],
)


def get_rag_service() -> RAGService:
    return build_rag_service()


@router.post(
    "/query",
    response_model=QueryResponse,
)
def query(
    request: QueryRequest,
    rag_service: RAGService = Depends(
        get_rag_service
    ),
) -> QueryResponse:
    """Answer a question using enterprise documents."""

    try:
        response = rag_service.answer(
            request.question,
            top_k=request.top_k,
            document_family_id=(
                request.document_family_id
            ),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return QueryResponse(
        question=response.question,
        answer=response.answer,
        sources=[
            SourceResponse(
                source=source.source,
                document_family_id=source.document_family_id,
                document_version=source.document_version,
                effective_date=source.effective_date,
                page=source.page,
                chunk_index=source.chunk_index,
            )
            for source in response.sources
        ],
    )
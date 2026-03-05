"""Book-related API routes."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from ..deps import get_generation_service
from ..schemas import BookResponse, CreateBookRequest, CreateBookResponse
from ..service import BookGenerationService

router = APIRouter(prefix="/api/v1/books", tags=["books"])


@router.post("", response_model=CreateBookResponse)
async def create_book_task(
    payload: CreateBookRequest,
    service: BookGenerationService = Depends(get_generation_service),
) -> CreateBookResponse:
    return await service.create_task(payload)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    service: BookGenerationService = Depends(get_generation_service),
) -> BookResponse:
    book = await service.store.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("/{book_id}/download")
async def download_book_asset(
    book_id: str,
    asset_type: str = Query(alias="type", pattern="^(md|pdf)$"),
    service: BookGenerationService = Depends(get_generation_service),
):
    book = await service.store.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    asset_path = book.markdown_path if asset_type == "md" else book.slides_pdf_path
    if not asset_path:
        raise HTTPException(status_code=404, detail="Asset not available")

    file_path = Path(asset_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    media_type = "text/markdown" if asset_type == "md" else "application/pdf"
    return FileResponse(str(file_path), filename=file_path.name, media_type=media_type)


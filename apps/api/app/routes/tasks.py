"""Task lifecycle API routes."""

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_generation_service
from ..schemas import TaskResponse
from ..service import BookGenerationService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    service: BookGenerationService = Depends(get_generation_service),
) -> TaskResponse:
    task = await service.store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


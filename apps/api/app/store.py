"""In-memory storage for MVP task lifecycle."""

from __future__ import annotations

import asyncio
from datetime import datetime

from .schemas import BookResponse, TaskResponse


class InMemoryStore:
    """Simple in-memory state store for tasks and books."""

    def __init__(self) -> None:
        self._tasks: dict[str, TaskResponse] = {}
        self._books: dict[str, BookResponse] = {}
        self._lock = asyncio.Lock()

    async def save_task(self, task: TaskResponse) -> None:
        async with self._lock:
            self._tasks[task.task_id] = task

    async def get_task(self, task_id: str) -> TaskResponse | None:
        async with self._lock:
            return self._tasks.get(task_id)

    async def update_task(
        self,
        task_id: str,
        *,
        status: str | None = None,
        stage: str | None = None,
        progress: int | None = None,
        message: str | None = None,
        error: str | None = None,
    ) -> TaskResponse | None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            payload = task.model_dump()
            if status is not None:
                payload["status"] = status
            if stage is not None:
                payload["stage"] = stage
            if progress is not None:
                payload["progress"] = progress
            if message is not None:
                payload["message"] = message
            if error is not None:
                payload["error"] = error
            payload["updated_at"] = datetime.utcnow()
            updated = TaskResponse(**payload)
            self._tasks[task_id] = updated
            return updated

    async def save_book(self, book: BookResponse) -> None:
        async with self._lock:
            self._books[book.book_id] = book

    async def get_book(self, book_id: str) -> BookResponse | None:
        async with self._lock:
            return self._books.get(book_id)


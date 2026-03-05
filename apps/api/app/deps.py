"""Dependency providers for FastAPI routes."""

from fastapi import Request

from .service import BookGenerationService


def get_generation_service(request: Request) -> BookGenerationService:
    return request.app.state.generation_service  # type: ignore[attr-defined]


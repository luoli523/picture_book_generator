"""FastAPI entrypoint for web architecture MVP."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.books import router as books_router
from .routes.styles import router as styles_router
from .routes.tasks import router as tasks_router
from .service import BookGenerationService
from .store import InMemoryStore


def create_app() -> FastAPI:
    app = FastAPI(
        title="Picture Book Generator API",
        version="0.1.0",
        description="MVP API for book generation tasks.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    store = InMemoryStore()
    app.state.generation_service = BookGenerationService(store)

    @app.get("/healthz", tags=["system"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(books_router)
    app.include_router(tasks_router)
    app.include_router(styles_router)
    return app


app = create_app()


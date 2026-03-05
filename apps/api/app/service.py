"""Book generation orchestration service for API/worker MVP."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from picture_book_generator.core.generator import PictureBookGenerator
from picture_book_generator.core.models import BookConfig, Language
from picture_book_generator.services.notebooklm import NotebookLMService
from picture_book_generator.utils.config import get_settings

from .schemas import BookResponse, CreateBookRequest, CreateBookResponse, TaskResponse
from .store import InMemoryStore

AGE_GROUP_MAP = {
    "3-5": (3, 5),
    "6-8": (6, 8),
    "9-12": (9, 12),
}


class BookGenerationService:
    """Create and track generation tasks."""

    def __init__(self, store: InMemoryStore) -> None:
        self.store = store

    async def create_task(self, payload: CreateBookRequest) -> CreateBookResponse:
        task_id = f"task_{uuid4().hex[:10]}"
        book_id = f"book_{uuid4().hex[:10]}"
        now = datetime.utcnow()

        task = TaskResponse(
            task_id=task_id,
            book_id=book_id,
            status="queued",
            stage="prepare_context",
            progress=0,
            message="任务已创建，等待执行",
            created_at=now,
            updated_at=now,
        )
        await self.store.save_task(task)

        asyncio.create_task(self._run_generation(task_id, book_id, payload))

        return CreateBookResponse(task_id=task_id, book_id=book_id, status="queued")

    def _build_config(self, payload: CreateBookRequest) -> BookConfig:
        topic = payload.content_source.topic.strip()
        parent_story = payload.content_source.parent_story.strip()
        if not topic:
            topic = "family_story" if parent_story else "picture_book"

        min_age, max_age = AGE_GROUP_MAP[payload.child_profile.age_group]

        return BookConfig(
            topic=topic,
            language=Language(payload.book_config.language),
            age_range=(min_age, max_age),
            chapter_count=payload.book_config.chapters,
            include_illustrations=payload.book_config.include_illustrations,
            child_gender=payload.child_profile.gender,
            reading_level=payload.child_profile.reading_level,
            interests=payload.child_profile.interests,
            source_mode=payload.content_source.mode,
            parent_story=parent_story,
            style_theme=payload.style.theme_id,
            narration_tone=payload.style.tone,
            education_goal=payload.style.education_goal,
            chapter_length=payload.book_config.chapter_length,
        )

    async def _run_generation(
        self,
        task_id: str,
        book_id: str,
        payload: CreateBookRequest,
    ) -> None:
        await self.store.update_task(
            task_id,
            status="running",
            stage="prepare_context",
            progress=5,
            message="正在准备绘本生成参数",
        )

        try:
            settings = get_settings()
            config = self._build_config(payload)
            generator = PictureBookGenerator(settings)

            await self.store.update_task(
                task_id,
                stage="search_knowledge",
                progress=15,
                message="正在搜索与整理知识",
            )

            await self.store.update_task(
                task_id,
                stage="adapt_content",
                progress=30,
                message="正在适配儿童可读内容",
            )

            await self.store.update_task(
                task_id,
                stage="generate_structure",
                progress=45,
                message="正在生成绘本结构",
            )

            await self.store.update_task(
                task_id,
                stage="generate_chapters",
                progress=60,
                message="正在生成章节内容",
            )
            book = await generator.generate(config)

            await self.store.update_task(
                task_id,
                stage="export_markdown",
                progress=75,
                message="正在导出 Markdown 文件",
            )

            output_dir = Path(settings.output_dir) / "web_api"
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c for c in config.topic if c.isalnum() or c in (" ", "-", "_"))
            safe_topic = safe_topic.strip().replace(" ", "_") or "picture_book"
            markdown_path = output_dir / f"{safe_topic}_{timestamp}_{book_id}.md"
            markdown_content = book.to_markdown()
            markdown_path.write_text(markdown_content, encoding="utf-8")

            slides_pdf_path: str | None = None
            slides_error: str | None = None
            if payload.book_config.generate_slides:
                await self.store.update_task(
                    task_id,
                    stage="generate_slides",
                    progress=85,
                    message="正在生成 NotebookLM Slides（可能需要 2-5 分钟）",
                )
                try:
                    notebook_service = NotebookLMService(settings)
                    slides_pdf_path = await notebook_service.upload_and_generate_slides(
                        markdown_content,
                        title=markdown_path.name,
                        download_dir=str(output_dir),
                        language=config.language.value,
                    )
                except Exception as exc:
                    slides_error = str(exc)

            await self.store.update_task(
                task_id,
                stage="finalize",
                progress=95,
                message="正在整理结果",
            )

            book_record = BookResponse(
                book_id=book_id,
                title=book.title,
                topic=config.topic,
                language=config.language.value,
                age_group=payload.child_profile.age_group,
                style_theme=payload.style.theme_id,
                markdown_path=str(markdown_path),
                slides_pdf_path=slides_pdf_path,
                slides_error=slides_error,
                created_at=datetime.utcnow(),
            )
            await self.store.save_book(book_record)

            done_msg = "绘本生成完成"
            if slides_error:
                done_msg += f"（Slides 失败：{slides_error}）"

            await self.store.update_task(
                task_id,
                status="succeeded",
                stage="completed",
                progress=100,
                message=done_msg,
            )
        except Exception as exc:
            await self.store.update_task(
                task_id,
                status="failed",
                stage="failed",
                progress=100,
                message="任务失败",
                error=str(exc),
            )


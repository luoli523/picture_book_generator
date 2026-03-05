"""绘本生成 API + SSE 进度推送"""

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas import (
    BookResult,
    GenerateFullRequest,
    GenerateResponse,
    JobStatus,
    ProductResult,
)

router = APIRouter(prefix="/api/generate", tags=["generate"])

# 内存任务存储（个人/朋友使用场景足够）
jobs: dict[str, dict[str, Any]] = {}


def _create_job() -> str:
    job_id = uuid.uuid4().hex[:12]
    jobs[job_id] = {
        "status": "pending",
        "events": [],  # SSE 事件队列
        "book": None,
        "products": [],
        "error": None,
    }
    return job_id


def _push_event(job_id: str, event_type: str, message: str, data: dict | None = None):
    """向任务事件队列推送一条 SSE 事件"""
    if job_id not in jobs:
        return
    event = {"type": event_type, "message": message}
    if data:
        event["data"] = data
    jobs[job_id]["events"].append(event)


async def _run_generation(job_id: str, request: GenerateFullRequest):
    """后台执行绘本生成流程"""
    from picture_book_generator.core.generator import PictureBookGenerator
    from picture_book_generator.core.models import BookConfig
    from picture_book_generator.services.knowledge_search import KnowledgeSearchService
    from picture_book_generator.utils.config import Language as CoreLanguage
    from picture_book_generator.utils.config import LLMProvider as CoreLLMProvider
    from picture_book_generator.utils.config import Settings

    book_req = request.book
    job = jobs[job_id]

    try:
        job["status"] = "generating_book"

        # 构建 Settings（如果指定了 LLM provider，覆盖默认值）
        settings = Settings()
        if book_req.llm_provider:
            settings.default_llm_provider = CoreLLMProvider(book_req.llm_provider.value)

        # 映射语言
        lang_map = {"zh": CoreLanguage.CHINESE, "en": CoreLanguage.ENGLISH}
        core_lang = lang_map.get(book_req.language.value, CoreLanguage.ENGLISH)

        # 确定主题（story 模式用前 20 字作为主题标识）
        topic = book_req.topic.strip()
        if book_req.content_mode.value == "story":
            topic = book_req.story_text.strip()[:20]

        config = BookConfig(
            topic=topic,
            language=core_lang,
            age_range=(book_req.age_min, book_req.age_max),
            chapter_count=book_req.chapters,
        )

        generator = PictureBookGenerator(settings)

        # --- Step 1: 搜索知识 ---
        _push_event(job_id, "progress", "正在搜索相关知识...")
        async with KnowledgeSearchService(settings) as knowledge_service:
            knowledge = await knowledge_service.search(config.topic)
        _push_event(job_id, "progress", "知识搜索完成")

        # --- Step 2: 适配内容 ---
        _push_event(job_id, "progress", "正在将内容适配为儿童可读形式...")
        adapted_content = await generator.content_adapter.adapt(
            knowledge=knowledge,
            age_range=config.age_range,
            language=config.language,
        )
        _push_event(job_id, "progress", "内容适配完成")

        # --- Step 3: 生成绘本结构 ---
        _push_event(job_id, "progress", "正在生成绘本结构...")
        book = await generator._create_book_structure(config, adapted_content)
        _push_event(
            job_id,
            "book_title",
            f"绘本标题: {book.title}",
            {"title": book.title, "summary": book.summary},
        )

        # --- Step 4: 生成章节内容 ---
        _push_event(job_id, "progress", "正在生成章节内容...")
        book = await generator._generate_chapters(book, config, adapted_content)
        _push_event(job_id, "progress", "章节内容生成完成")

        # --- 保存 Markdown ---
        output_dir = Path(settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (" ", "-", "_")).strip()
        filename = f"{safe_topic}_{timestamp}.md" if safe_topic else f"book_{timestamp}.md"
        output_path = output_dir / filename

        markdown_content = book.to_markdown()
        output_path.write_text(markdown_content, encoding="utf-8")

        book_result = BookResult(
            title=book.title,
            topic=topic,
            language=book_req.language.value,
            markdown_path=str(output_path),
            markdown_content=markdown_content,
        )
        job["book"] = book_result.model_dump()

        _push_event(
            job_id,
            "book_complete",
            "绘本生成完成",
            {"title": book.title, "markdown_path": str(output_path)},
        )

        # --- 生成 NotebookLM 产品 ---
        if book_req.products:
            job["status"] = "generating_products"
            await _generate_products(
                job_id, request, markdown_content, filename, str(output_path.parent)
            )

        job["status"] = "completed"
        _push_event(job_id, "done", "全部完成")

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        _push_event(job_id, "error", f"生成失败: {e}")


async def _generate_products(
    job_id: str,
    request: GenerateFullRequest,
    markdown_content: str,
    title: str,
    download_dir: str,
):
    """生成 NotebookLM 产品（slides, video, audio 等）"""
    import importlib.util

    if importlib.util.find_spec("notebooklm") is None:
        _push_event(job_id, "warning", "notebooklm-py 未安装，跳过产品生成")
        return

    book_req = request.book
    opts = request.product_options
    job = jobs[job_id]

    # 初始化产品状态
    for pt in book_req.products:
        job["products"].append(
            ProductResult(product_type=pt, status="pending").model_dump()
        )

    try:
        # 上传到 NotebookLM
        _push_event(job_id, "progress", "正在上传到 NotebookLM...")

        from picture_book_generator.services.notebooklm import NotebookLMService
        from picture_book_generator.utils.config import Settings

        settings = Settings()
        nlm_service = NotebookLMService(settings)
        notebook_id, source_id, source_title = await nlm_service.upload(
            markdown_content, title=title
        )
        _push_event(job_id, "progress", "上传完成，开始生成产品...")

        # 语言映射
        lang = "zh" if book_req.language.value == "zh" else "en"
        instructions = book_req.custom_instructions or "创建适合儿童和少年阅读的，卡通风格"

        # 逐个生成产品
        for i, pt in enumerate(book_req.products):
            _update_product_status(job_id, i, "generating")
            _push_event(job_id, "product_start", f"正在生成 {pt.value}...")

            try:
                file_path = await _generate_single_product(
                    nlm_service=nlm_service,
                    notebook_id=notebook_id,
                    source_ids=[source_id],
                    source_title=source_title,
                    download_dir=download_dir,
                    product_type=pt,
                    opts=opts,
                    lang=lang,
                    instructions=instructions,
                )
                _update_product_status(job_id, i, "completed", file_path=file_path)
                _push_event(
                    job_id,
                    "product_complete",
                    f"{pt.value} 生成完成",
                    {"product_type": pt.value, "file_path": file_path},
                )
            except Exception as e:
                _update_product_status(job_id, i, "failed", error=str(e))
                _push_event(job_id, "product_error", f"{pt.value} 生成失败: {e}")

    except Exception as e:
        _push_event(job_id, "warning", f"NotebookLM 产品生成出错: {e}")


async def _generate_single_product(
    nlm_service,
    notebook_id: str,
    source_ids: list[str],
    source_title: str,
    download_dir: str,
    product_type,
    opts,
    lang: str,
    instructions: str,
) -> str:
    """生成单个 NotebookLM 产品，返回文件路径"""
    from api.schemas import ProductType

    if product_type == ProductType.SLIDES:
        return await nlm_service.generate_slides(
            notebook_id=notebook_id,
            source_ids=source_ids,
            source_title=source_title,
            download_dir=download_dir,
            instructions=instructions,
            language=lang,
            slide_format=opts.slides.slide_format.value,
            slide_length=opts.slides.slide_length.value,
        )

    # 其他产品类型通过 notebooklm-py SDK 直接调用
    from notebooklm import NotebookLMClient
    from notebooklm.rpc.types import AudioFormat as NLMAudioFormat
    from notebooklm.rpc.types import AudioLength as NLMAudioLength
    from notebooklm.rpc.types import InfographicDetail as NLMInfographicDetail
    from notebooklm.rpc.types import InfographicOrientation as NLMInfographicOrientation
    from notebooklm.rpc.types import QuizDifficulty as NLMQuizDifficulty
    from notebooklm.rpc.types import QuizQuantity as NLMQuizQuantity
    from notebooklm.rpc.types import VideoFormat as NLMVideoFormat
    from notebooklm.rpc.types import VideoStyle as NLMVideoStyle

    download_path = Path(download_dir)

    async with await NotebookLMClient.from_storage() as client:
        if product_type == ProductType.VIDEO:
            style_map = {
                "auto": NLMVideoStyle.AUTO_SELECT,
                "classic": NLMVideoStyle.CLASSIC,
                "whiteboard": NLMVideoStyle.WHITEBOARD,
                "kawaii": NLMVideoStyle.KAWAII,
                "anime": NLMVideoStyle.ANIME,
                "watercolor": NLMVideoStyle.WATERCOLOR,
                "retro_print": NLMVideoStyle.RETRO_PRINT,
                "heritage": NLMVideoStyle.HERITAGE,
                "paper_craft": NLMVideoStyle.PAPER_CRAFT,
            }
            fmt_map = {
                "explainer": NLMVideoFormat.EXPLAINER,
                "brief": NLMVideoFormat.BRIEF,
            }
            status = await client.artifacts.generate_video(
                notebook_id,
                source_ids=source_ids,
                language=lang,
                instructions=instructions,
                video_style=style_map.get(opts.video.video_style.value),
                video_format=fmt_map.get(opts.video.video_format.value),
            )
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            out = download_path / f"{source_title}_video.mp4"
            await client.artifacts.download_video(notebook_id, str(out))
            return str(out)

        if product_type == ProductType.AUDIO:
            fmt_map = {
                "deep_dive": NLMAudioFormat.DEEP_DIVE,
                "brief": NLMAudioFormat.BRIEF,
                "critique": NLMAudioFormat.CRITIQUE,
                "debate": NLMAudioFormat.DEBATE,
            }
            len_map = {
                "short": NLMAudioLength.SHORT,
                "default": NLMAudioLength.DEFAULT,
                "long": NLMAudioLength.LONG,
            }
            status = await client.artifacts.generate_audio(
                notebook_id,
                source_ids=source_ids,
                language=lang,
                instructions=instructions,
                audio_format=fmt_map.get(opts.audio.audio_format.value),
                audio_length=len_map.get(opts.audio.audio_length.value),
            )
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            out = download_path / f"{source_title}_audio.mp4"
            await client.artifacts.download_audio(notebook_id, str(out))
            return str(out)

        if product_type == ProductType.INFOGRAPHIC:
            orient_map = {
                "landscape": NLMInfographicOrientation.LANDSCAPE,
                "portrait": NLMInfographicOrientation.PORTRAIT,
                "square": NLMInfographicOrientation.SQUARE,
            }
            detail_map = {
                "concise": NLMInfographicDetail.CONCISE,
                "standard": NLMInfographicDetail.STANDARD,
                "detailed": NLMInfographicDetail.DETAILED,
            }
            status = await client.artifacts.generate_infographic(
                notebook_id,
                source_ids=source_ids,
                language=lang,
                instructions=instructions,
                orientation=orient_map.get(opts.infographic.orientation.value),
                detail_level=detail_map.get(opts.infographic.detail_level.value),
            )
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            out = download_path / f"{source_title}_infographic.png"
            await client.artifacts.download_infographic(notebook_id, str(out))
            return str(out)

        if product_type == ProductType.QUIZ:
            diff_map = {
                "easy": NLMQuizDifficulty.EASY,
                "medium": NLMQuizDifficulty.MEDIUM,
                "hard": NLMQuizDifficulty.HARD,
            }
            qty_map = {
                "fewer": NLMQuizQuantity.FEWER,
                "standard": NLMQuizQuantity.STANDARD,
            }
            status = await client.artifacts.generate_quiz(
                notebook_id,
                source_ids=source_ids,
                instructions=instructions,
                quantity=qty_map.get(opts.quiz.quantity.value),
                difficulty=diff_map.get(opts.quiz.difficulty.value),
            )
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            out = download_path / f"{source_title}_quiz.json"
            await client.artifacts.download_quiz(notebook_id, str(out))
            return str(out)

        if product_type == ProductType.FLASHCARDS:
            status = await client.artifacts.generate_flashcards(
                notebook_id,
                source_ids=source_ids,
                instructions=instructions,
            )
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            out = download_path / f"{source_title}_flashcards.json"
            await client.artifacts.download_flashcards(notebook_id, str(out))
            return str(out)

        if product_type == ProductType.MIND_MAP:
            status = await client.artifacts.generate_mind_map(
                notebook_id,
                source_ids=source_ids,
            )
            await client.artifacts.wait_for_completion(notebook_id, status.task_id)
            out = download_path / f"{source_title}_mindmap.json"
            await client.artifacts.download_mind_map(notebook_id, str(out))
            return str(out)

    raise ValueError(f"未支持的产品类型: {product_type}")


def _update_product_status(
    job_id: str, index: int, status: str, file_path: str | None = None, error: str | None = None
):
    """更新任务中某个产品的状态"""
    job = jobs.get(job_id)
    if not job or index >= len(job["products"]):
        return
    job["products"][index]["status"] = status
    if file_path:
        job["products"][index]["file_path"] = file_path
    if error:
        job["products"][index]["error"] = error


# === API 端点 ===


@router.post("", response_model=GenerateResponse)
async def create_generation(request: GenerateFullRequest):
    """创建绘本生成任务，返回 job_id"""
    job_id = _create_job()
    # 启动后台任务
    asyncio.create_task(_run_generation(job_id, request))
    return GenerateResponse(job_id=job_id, status="started")


@router.get("/{job_id}/status", response_model=JobStatus)
async def get_job_status(job_id: str):
    """查询任务状态（轮询方式）"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        book=job["book"],
        products=job["products"],
        error=job["error"],
    )


@router.get("/{job_id}/stream")
async def stream_job_events(job_id: str):
    """SSE 端点：实时推送生成进度事件"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_stream() -> AsyncGenerator[str, None]:
        cursor = 0
        while True:
            job = jobs.get(job_id)
            if not job:
                break

            # 发送新事件
            events = job["events"]
            while cursor < len(events):
                event = events[cursor]
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                cursor += 1

                # 终止事件
                if event["type"] in ("done", "error"):
                    return

            # 任务已结束但没有终止事件（安全兜底）
            if job["status"] in ("completed", "failed") and cursor >= len(events):
                return

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

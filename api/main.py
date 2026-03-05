"""FastAPI 后端入口"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routers.generate import router as generate_router

app = FastAPI(
    title="Picture Book Generator API",
    description="儿童绘本创作工坊 API",
    version="0.1.0",
)

# CORS: 允许前端 dev server 访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件: 挂载 output/ 目录供下载
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
app.mount("/files", StaticFiles(directory=str(output_dir)), name="files")


app.include_router(generate_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/config")
async def get_config():
    """返回前端需要的配置信息（可用的 LLM 提供商、语言等）"""
    from picture_book_generator.utils.config import get_settings

    settings = get_settings()

    # 检测哪些 LLM provider 已配置 API key
    available_providers = []
    if settings.anthropic_api_key:
        available_providers.append("anthropic")
    if settings.openai_api_key:
        available_providers.append("openai")
    if settings.google_api_key:
        available_providers.append("gemini")
    if settings.grok_api_key:
        available_providers.append("grok")

    return {
        "default_provider": settings.default_llm_provider.value,
        "available_providers": available_providers,
        "languages": ["zh", "en"],
    }

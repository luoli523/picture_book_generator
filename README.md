# Picture Book Generator 儿童绘本生成器

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> AI 驱动的儿童绘本创作平台 — 输入主题，自动搜索知识、适配儿童语言、生成结构化绘本，并通过 NotebookLM 生成 Slides、视频、音频、信息图等多种产品。

## 功能概览

**核心流程**: 知识搜索 → LLM 内容适配 → 结构化 Markdown 绘本 → NotebookLM 多产品生成

- **Web 应用**: Next.js 15 + Tailwind CSS v4 前端 + FastAPI 后端，SSE 实时进度推送
- **CLI 工具**: Typer + Rich 命令行界面，支持完整的生成和分享流程
- **多 LLM 支持**: Claude、GPT、Gemini、Grok 四大模型提供商
- **智能搜索**: Tavily + SerpAPI + Wikipedia 并行搜索，合并知识
- **7 种 NotebookLM 产品**:
  | 产品 | 说明 | 可选参数 |
  |------|------|----------|
  | Slides | PDF 演示文稿 | 格式 (detailed/presenter)、长度 (default/short) |
  | Video | 动画视频 | 风格 (kawaii/anime/watercolor/paper_craft 等 9 种)、格式 |
  | Audio | 播客音频 | 格式 (deep_dive/brief/critique/debate)、长度 |
  | Infographic | 信息图 | 方向 (landscape/portrait/square)、详细度 |
  | Quiz | 知识问答 | 难度 (easy/medium/hard)、数量 |
  | Flashcards | 闪卡 | - |
  | Mind Map | 思维导图 | - |
- **Telegram 分享**: Slides PDF 切图 + 双语社交媒体文案一键推送
- **双语支持**: 中文、英文

---

## 快速开始

### 方式一：Web 应用（推荐）

```bash
# 1. 安装 Python 依赖
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[web,notebooklm]"

# 2. 配置环境变量
cp .env.example .env   # 编辑 .env 填入 API Key

# 3. 登录 NotebookLM（首次使用）
notebooklm login

# 4. 启动 FastAPI 后端
uvicorn api.main:app --port 8000

# 5. 启动 Next.js 前端（新终端）
cd web
npm install
npm run dev

# 访问 http://localhost:3000
```

### 方式二：CLI 命令行

```bash
# 安装
pip install -e ".[notebooklm]"
cp .env.example .env   # 编辑 .env

# 首次登录 NotebookLM
notebooklm login

# 生成绘本 + Slides（默认）
picture-book generate ocean

# 生成中文绘本
picture-book generate 恐龙 --lang zh

# 仅生成绘本，跳过 Slides
picture-book generate dinosaur --no-nlm-slides

# 生成 + 发送到 Telegram
picture-book generate Rocket --lang zh --telegram
```

---

## 项目架构

```
picture_book_generator/
├── src/picture_book_generator/     # Python 核心库
│   ├── cli.py                      # Typer CLI 入口
│   ├── core/
│   │   ├── generator.py            # 绘本生成器（编排搜索→适配→结构→章节）
│   │   └── models.py               # Pydantic 数据模型 (BookConfig, Chapter, PictureBook)
│   ├── services/
│   │   ├── knowledge_search.py     # 并行知识搜索 (Tavily/SerpAPI/Wikipedia)
│   │   ├── content_adapter.py      # 多 LLM 内容适配（Grok 通过 OpenAI SDK + 自定义 base URL）
│   │   ├── notebooklm.py           # NotebookLM 集成 (notebooklm-py SDK)
│   │   ├── pdf_splitter.py         # PDF → PNG 拆分 (PyMuPDF)
│   │   └── telegram.py             # Telegram Bot API 推送
│   ├── prompts/                    # LLM Prompt 模板 (.txt 文件，str.format 渲染)
│   └── utils/config.py             # pydantic-settings 配置 (从 .env 加载)
├── api/                            # FastAPI 后端
│   ├── main.py                     # 应用入口 (CORS, /files/ 静态挂载, /api/health)
│   ├── schemas.py                  # Pydantic 请求/响应模型 + 所有产品选项枚举
│   └── routers/generate.py         # 生成 API (POST + SSE 流 + 轮询状态)
├── web/                            # Next.js 16 前端
│   ├── app/
│   │   ├── page.tsx                # 首页 (Hero + 功能展示)
│   │   ├── create/CreateForm.tsx   # 创建表单 (孩子信息 + 内容 + 产品选择)
│   │   ├── generate/[id]/          # 生成进度页 (SSE EventSource 实时显示)
│   │   └── result/[id]/            # 结果展示页 (产品下载 + Markdown 预览)
│   ├── lib/api.ts                  # TypeScript API 类型 + fetch 封装
│   └── next.config.ts              # API 代理 (/api/* → FastAPI:8000)
├── tests/                          # pytest + pytest-asyncio (全 mock，无网络调用)
├── output/                         # 生成产物输出目录
└── .env.example                    # 环境变量模板
```

### 数据流

```
                     Web 前端                                    FastAPI 后端
┌──────────────────────────────────────┐    ┌──────────────────────────────────────────┐
│  CreateForm                          │    │  POST /api/generate                      │
│  ├─ 孩子信息 (姓名/性别/年龄/语言)    │───▶│  ├─ 创建后台任务 (asyncio.create_task)   │
│  ├─ 内容 (主题 or 故事原文)           │    │  └─ 返回 job_id                          │
│  └─ 产品选择 (slides/video/audio...) │    │                                          │
│                                      │    │  GET /api/generate/{id}/stream (SSE)     │
│  GenerationProgress                  │◀──▶│  ├─ 知识搜索 → progress 事件              │
│  └─ EventSource 实时显示步骤          │    │  ├─ 内容适配 → progress 事件              │
│                                      │    │  ├─ 绘本结构 → book_title 事件            │
│  ResultDashboard                     │    │  ├─ 章节生成 → progress 事件              │
│  ├─ 绘本信息卡片                     │◀──▶│  ├─ NotebookLM 上传 → progress 事件       │
│  ├─ 产品网格 (状态 + 下载)           │    │  ├─ 产品生成 → product_start/complete     │
│  └─ Markdown 预览                    │    │  └─ done 事件                             │
└──────────────────────────────────────┘    └──────────────────────────────────────────┘
```

---

## 配置

### 环境变量 (.env)

```bash
# LLM 提供商（选其一配置即可）
DEFAULT_LLM_PROVIDER=grok        # anthropic | openai | gemini | grok

ANTHROPIC_API_KEY=sk-ant-xxx     # Claude
OPENAI_API_KEY=sk-xxx            # GPT
GOOGLE_API_KEY=xxx               # Gemini
GROK_API_KEY=xai-xxx             # Grok
XAI_BASE_URL=https://api.x.ai/v1

# 搜索服务（可选，不配则仅用 Wikipedia + LLM 知识）
TAVILY_API_KEY=tvly-xxx          # AI 优化搜索，推荐 (1000 次/月免费)
SERP_API_KEY=xxx                 # Google 搜索 (100 次/月免费)

# Telegram 推送（可选）
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx

# 输出
OUTPUT_DIR=./output
MAX_TOKENS=65535
```

### 安装选项

```bash
pip install -e .                        # 仅核心 CLI
pip install -e ".[notebooklm]"          # + NotebookLM 产品生成
pip install -e ".[web,notebooklm]"      # + FastAPI 后端
pip install -e ".[dev]"                 # + pytest, ruff
pip install -e ".[dev,web,notebooklm]"  # 全部
```

---

## Web 应用详情

### 页面流程

1. **首页** (`/`) — Hero 展示 + "Start Creating" 入口
2. **创建页** (`/create`) — 三段式表单：
   - 卡片 A：孩子信息（姓名、性别、年龄范围滑块、语言）
   - 卡片 B：内容（主题模式 / 故事模式，8 个热门主题快选，章节数滑块）
   - 卡片 C：产品选择（7 种产品复选卡片，各自可展开配置参数）
3. **生成页** (`/generate/[id]`) — SSE 实时进度条 + 绘本标题预览
4. **结果页** (`/result/[id]`) — 绘本信息 + 产品网格（状态/下载） + Markdown 折叠预览

### API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查 |
| `GET` | `/api/config` | 前端配置（可用 LLM、默认值等） |
| `POST` | `/api/generate` | 创建生成任务，返回 `{ job_id }` |
| `GET` | `/api/generate/{id}/stream` | SSE 实时事件流 |
| `GET` | `/api/generate/{id}/status` | 轮询任务状态 |
| `GET` | `/files/*` | 静态文件服务（生成产物下载） |

### 本地开发

```bash
# 终端 1: FastAPI 后端
source .venv/bin/activate
uvicorn api.main:app --port 8000 --reload

# 终端 2: Next.js 前端
cd web
npm run dev    # http://localhost:3000
```

Next.js 通过 `next.config.ts` 中的 rewrites 将 `/api/*` 和 `/files/*` 代理到 FastAPI 8000 端口。

---

## CLI 命令速查

### 核心命令

| 命令 | 说明 |
|------|------|
| `picture-book generate <主题>` | 生成绘本 + Slides（默认英文，5 章，7-10 岁） |
| `picture-book generate <主题> --no-nlm-slides` | 仅生成绘本 |
| `picture-book share <PDF>` | Slides PDF 切图 + 发送 Telegram |
| `picture-book upload-to-notebooklm <file>` | 手动上传到 NotebookLM |
| `picture-book generate-slides <URL\|ID>` | 从已有 notebook 生成 Slides |
| `picture-book languages` | 列出支持语言 |
| `picture-book version` | 版本信息 |

### 生成参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--lang` / `-l` | `en` | 语言：en, zh |
| `--chapters` / `-c` | `5` | 章节数 (3-10) |
| `--min-age` | `7` | 最小目标年龄 |
| `--max-age` | `10` | 最大目标年龄 |
| `--output` / `-o` | 自动命名 | 输出文件路径 |
| `--nlm-slides/--no-nlm-slides` | 启用 | 是否生成 Slides |
| `--nlm-instructions` | 卡通风格 | 自定义 NotebookLM 指令 |
| `--nlm-format` | `detailed` | Slides 格式 (detailed/presenter) |
| `--nlm-length` | `default` | Slides 长度 (default/short) |
| `--telegram` | 关闭 | 发送到 Telegram |

---

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev,web,notebooklm]"

# 运行测试
pytest -v
pytest tests/test_models.py -v                    # 单文件
pytest tests/test_generator.py::TestXxx::test_yyy  # 单用例

# 代码检查 & 格式化
ruff check src/ tests/ api/
ruff format .

# 前端
cd web
npm run lint
npm run build
```

### 测试说明

所有测试通过 mock 运行，无需网络连接。LLM 调用 mock `ContentAdapterService` 方法，搜索 mock `KnowledgeSearchService`。

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Next.js 16 + React 19 + Tailwind CSS v4 + Framer Motion + Lucide Icons |
| 后端 | FastAPI + Uvicorn + SSE (Server-Sent Events) |
| CLI | Typer + Rich |
| LLM | Anthropic SDK, OpenAI SDK, Google GenAI SDK (Grok via OpenAI + 自定义 base URL) |
| 搜索 | Tavily API, SerpAPI, Wikipedia API (httpx + tenacity 重试) |
| NotebookLM | notebooklm-py SDK |
| 配置 | pydantic-settings (.env) |
| 测试 | pytest + pytest-asyncio (全 mock) |
| Lint | Ruff (line-length 100, py310, rules E/F/I/N/W) |

---

## 故障排除

**NotebookLM `Storage file not found`** — 运行 `notebooklm login` 完成 Google 账号登录。

**Slides 生成超时** — NotebookLM 产品通常需要 2-5 分钟。超过 10 分钟自动跳过。备用方案：`python3 download_slides.py <notebook_id>`。

**API 调用失败** — 检查 `.env` 中对应 provider 的 API Key 和 `DEFAULT_LLM_PROVIDER` 设置。

**`picture-book` 命令找不到** — 确保虚拟环境已激活，或重新 `pip install -e .`。

**Web 应用 API 404** — 确保 FastAPI 后端运行在 8000 端口，Next.js 代理配置正确。

---

## License

MIT

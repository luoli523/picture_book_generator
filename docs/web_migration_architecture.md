# Web 架构迁移方案（Gradio -> Next.js + FastAPI）

## 1. 目标架构

前端与后端分离，长耗时生成任务异步化：

- 前端：Next.js（App Router）+ TypeScript + Tailwind + shadcn/ui + Framer Motion
- API：FastAPI（仅负责请求校验、任务创建、查询、下载链接）
- Worker：Celery + Redis（执行绘本生成与 NotebookLM Slides）
- 数据库：PostgreSQL（任务、绘本、生成参数、状态、产物索引）
- 文件存储：S3/R2（Markdown/PDF/图片）

## 2. 仓库结构建议

```txt
picture_book_generator/
├─ apps/
│  ├─ web/                    # Next.js
│  ├─ api/                    # FastAPI
│  └─ worker/                 # Celery worker
├─ src/picture_book_generator/# 现有核心生成逻辑（保留复用）
├─ docs/
│  └─ web_migration_architecture.md
├─ requirements.txt
└─ pyproject.toml
```

说明：
- `src/picture_book_generator` 继续作为核心领域层（搜索、适配、生成、notebooklm）
- `apps/api` 与 `apps/worker` 通过 import 复用核心逻辑，避免重复实现

## 3. 后端边界与职责

### API 服务（FastAPI）
- 参数校验
- 任务入队
- 任务状态查询
- 结果元数据与下载链接返回
- 不直接执行耗时生成

### Worker 服务（Celery）
- 拉取任务并执行：
  - 构建 `BookConfig`
  - 调用 `PictureBookGenerator`
  - 可选调用 `NotebookLMService`
  - 上传产物文件到对象存储
  - 回写任务状态

## 4. API 契约（MVP）

### `POST /api/v1/books`
创建生成任务。

Request（示例）：
```json
{
  "child_profile": {
    "age_group": "6-8",
    "gender": "girl",
    "reading_level": "basic",
    "interests": ["ocean", "plants"]
  },
  "content_source": {
    "mode": "hybrid",
    "topic": "珊瑚礁探险",
    "parent_story": "..."
  },
  "style": {
    "theme_id": "ocean_pop",
    "tone": "exploratory",
    "education_goal": "science"
  },
  "book_config": {
    "language": "zh",
    "chapters": 6,
    "chapter_length": "medium",
    "include_illustrations": true,
    "generate_slides": true
  }
}
```

Response：
```json
{
  "task_id": "task_xxx",
  "book_id": "book_xxx",
  "status": "queued"
}
```

### `GET /api/v1/tasks/{task_id}`
查询任务状态。

Response：
```json
{
  "task_id": "task_xxx",
  "status": "running",
  "stage": "generate_chapters",
  "progress": 67,
  "message": "正在生成章节内容",
  "book_id": "book_xxx"
}
```

### `GET /api/v1/books/{book_id}`
返回绘本元信息与产物链接（可为空）。

### `GET /api/v1/books/{book_id}/download?type=md|pdf`
返回短期签名下载链接或流式下载。

### `GET /api/v1/styles`
返回风格模板列表（Ocean Pop 等）。

## 5. 任务状态机

- `queued`
- `running`
  - `prepare_context`
  - `search_knowledge`
  - `adapt_content`
  - `generate_structure`
  - `generate_chapters`
  - `export_markdown`
  - `generate_slides`（可选）
  - `upload_assets`
- `succeeded`
- `failed`
- `cancelled`（预留）

## 6. 数据模型（MVP）

### `books`
- `id`
- `title`
- `topic`
- `language`
- `age_range`
- `style_theme`
- `created_at`

### `book_tasks`
- `id`
- `book_id`
- `status`
- `stage`
- `progress`
- `message`
- `error`
- `created_at`
- `updated_at`

### `book_inputs`
- `book_id`
- `payload_json`（完整输入快照，便于复现）

### `book_assets`
- `book_id`
- `asset_type` (`markdown` / `slides_pdf` / `images_zip`)
- `storage_key`
- `public_url`

## 7. 前端路由与组件清单

## 页面路由
- `/` 首页（品牌与转化）
- `/create` 绘本工坊（多步骤）
- `/tasks/:taskId` 生成中页面（可跳转）
- `/books/:bookId` 结果页（阅读与下载）
- `/styles` 风格库

## 核心组件
- `HeroOceanPop`
- `CreateWizard`
- `StepChildProfile`
- `StepContentSource`
- `StepStyleGoal`
- `StepBookConfig`
- `GenerateProgressPanel`
- `BookReader`（章节阅读器）
- `DownloadActions`
- `StyleCardGrid`

## 8. 与现有代码映射

- 复用：
  - `core/generator.py`
  - `core/models.py`
  - `services/content_adapter.py`
  - `services/knowledge_search.py`
  - `services/notebooklm.py`
- 新增：
  - `apps/api/app/schemas.py`
  - `apps/api/app/routes/books.py`
  - `apps/api/app/routes/tasks.py`
  - `apps/worker/app/tasks/generate_book.py`
  - `apps/worker/app/services/storage.py`

## 9. 分阶段落地（建议 3 个 Sprint）

### Sprint 1（骨架）
- 初始化 `apps/web` 与 `apps/api`
- 打通 `POST /books` + `GET /tasks/{id}`（先用内存状态）
- 完成 `create` 页面 UI（Ocean Pop）

### Sprint 2（可用）
- 接入 Celery + Redis + Postgres
- Worker 调用现有生成链路，产出 Markdown
- 完成结果页阅读和 Markdown 下载

### Sprint 3（完整）
- 接入 NotebookLM Slides 与 PDF 下载
- 增加失败重试与任务恢复
- 增加监控日志与基本限流

## 10. 关键技术决策（需你确认）

1. 队列：`Celery`（稳定）还是 `RQ`（更轻）
2. 存储：本地磁盘（开发）+ S3/R2（生产）
3. 任务进度：轮询（MVP）还是 WebSocket/SSE（二期）

## 11. 开工顺序（下一步）

1. 建目录：`apps/web`、`apps/api`、`apps/worker`
2. 先做 API 最小闭环：
   - `POST /api/v1/books`
   - `GET /api/v1/tasks/{task_id}`
3. 前端完成 `/create` 页面并接入上述 API
4. Worker 接入现有 `PictureBookGenerator`，先产出 Markdown
5. 最后接入 NotebookLM Slides 与下载链接

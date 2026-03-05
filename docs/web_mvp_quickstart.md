# Web MVP 本地联调（API + Next.js）

## 1. 安装 Python 依赖

```bash
cd /Users/luoli/dev/git/picture_book_generator
make setup
```

## 2. 启动 FastAPI

```bash
cd /Users/luoli/dev/git/picture_book_generator
make api-dev
```

启动后可访问：
- `http://localhost:8000/healthz`
- `http://localhost:8000/docs`

## 3. 启动 Next.js Web

```bash
cd /Users/luoli/dev/git/picture_book_generator/apps/web
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

打开：
- `http://localhost:3000/`
- `http://localhost:3000/create`

## 4. 当前 MVP 能力

1. `/create` 提交任务到 `POST /api/v1/books`
2. 前端轮询 `GET /api/v1/tasks/{task_id}` 显示进度
3. 完成后请求 `GET /api/v1/books/{book_id}` 并提供下载按钮

## 5. 注意事项

- 默认会按你的配置尝试生成 NotebookLM Slides；未登录或失败不会影响 Markdown 生成。
- API 任务状态目前是内存存储，重启后状态会丢失（后续替换为 Redis + Postgres）。

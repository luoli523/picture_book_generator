# Picture Book Generator 儿童绘本生成器

根据用户输入的主题，自动搜索知识并生成适合7-10岁儿童阅读的绘本读物。

## 功能特性

- **主题搜索**: 根据输入主题自动搜索相关知识（维基百科、Web搜索等）
- **内容适配**: 将复杂知识转化为儿童可理解的语言
- **多语言支持**: 支持中文、英文、日文、韩文
- **多LLM支持**: 支持 Claude、ChatGPT、Gemini、Grok
- **结构化输出**: 生成包含章节、插图描述、知识要点的完整绘本
- **NotebookLM集成**: 支持上传到Google NotebookLM生成播客版本

## 安装

### 基础安装

```bash
# 克隆项目
git clone <repo-url>
cd picture_book_generator

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装基础依赖
pip install -e .
```

### 可选依赖

```bash
# 开发依赖 (测试、代码检查)
pip install -e ".[dev]"

# NotebookLM集成 (浏览器自动化)
pip install -e ".[notebooklm]"
playwright install chromium
```

## 配置

### 1. 创建配置文件

```bash
cp .env.example .env
```

### 2. 配置LLM提供商

支持以下LLM提供商，选择其一配置即可：

| 提供商 | 环境变量 | 模型示例 |
|--------|----------|----------|
| Anthropic (Claude) | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| OpenAI (ChatGPT) | `OPENAI_API_KEY` | gpt-4o, gpt-5 |
| Google (Gemini) | `GOOGLE_API_KEY` | gemini-2.0-flash |
| xAI (Grok) | `XAI_API_KEY` | grok-2-latest |

**.env 配置示例**:

```bash
# 选择默认LLM提供商: anthropic, openai, gemini, grok
DEFAULT_LLM_PROVIDER=openai

# OpenAI配置
OPENAI_API_KEY=sk-xxx...
OPENAI_MODEL=gpt-5

# 或使用Claude
# DEFAULT_LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-xxx...
# ANTHROPIC_MODEL=claude-sonnet-4-20250514

# 通用配置
MAX_TOKENS=4096
OUTPUT_DIR=./output
```

### 3. 可选：配置搜索服务

搜索服务用于获取主题相关的知识内容。如果不配置，系统会使用维基百科和LLM自身知识。

| 服务 | 说明 | 获取地址 | 免费额度 |
|------|------|----------|----------|
| **Tavily** | AI优化搜索，返回结构化内容，推荐用于RAG | https://tavily.com | 1000次/月 |
| **SerpAPI** | Google搜索结果，包含知识图谱 | https://serpapi.com | 100次/月 |

```bash
# Tavily - 推荐，专为AI应用优化
TAVILY_API_KEY=tvly-xxxxx

# SerpAPI - Google搜索结果
SERP_API_KEY=xxxxx
```

**搜索优先级**: Tavily > SerpAPI > Wikipedia (并行执行，结果合并)

## 使用方法

### 命令行

```bash
# 基本用法 - 生成中文绘本
picture-book generate 恐龙

# 指定语言
picture-book generate "Space Exploration" --lang en

# 自定义参数
picture-book generate 海洋生物 \
    --lang zh \
    --chapters 8 \
    --min-age 6 \
    --max-age 9 \
    --output my_book.md

# 查看支持的语言
picture-book languages

# 查看版本
picture-book version
```

### NotebookLM 集成

```bash
# 首次使用：登录Google账号 (会打开浏览器)
picture-book notebooklm-login

# 上传绘本到NotebookLM
picture-book upload-to-notebooklm ./output/恐龙.md
```

### Python API

```python
import asyncio
from picture_book_generator.core import PictureBookGenerator, BookConfig
from picture_book_generator.core.models import Language

async def main():
    config = BookConfig(
        topic="恐龙",
        language=Language.CHINESE,
        age_range=(7, 10),
        chapter_count=5,
    )

    generator = PictureBookGenerator()
    book = await generator.generate(config)

    # 导出为Markdown
    print(book.to_markdown())

    # 保存到文件
    with open("dinosaur_book.md", "w", encoding="utf-8") as f:
        f.write(book.to_markdown())

asyncio.run(main())
```

## 项目结构

```
picture_book_generator/
├── src/
│   └── picture_book_generator/
│       ├── __init__.py
│       ├── cli.py                     # 命令行接口
│       ├── core/
│       │   ├── generator.py           # 绘本生成器核心
│       │   └── models.py              # 数据模型
│       ├── services/
│       │   ├── knowledge_search.py    # 知识搜索服务
│       │   ├── content_adapter.py     # 内容适配服务 (LLM)
│       │   └── notebooklm.py          # NotebookLM集成 (Playwright)
│       └── utils/
│           └── config.py              # 配置管理 (多LLM支持)
├── tests/
├── pyproject.toml
├── .env.example
└── README.md
```

## 工作流程

```
用户输入主题 → 知识搜索 → LLM内容适配 → 绘本生成 → 导出/上传NotebookLM
     ↓              ↓            ↓            ↓              ↓
   "恐龙"      维基百科等    GPT/Claude    Markdown      播客/问答
```

1. **输入主题**: 用户提供绘本主题（如"恐龙"、"太空"等）
2. **知识搜索**: 系统从多个来源搜索相关知识
3. **内容适配**: 使用LLM将知识转化为儿童可读内容
4. **绘本生成**: 生成结构化的绘本，包含章节、插图描述等
5. **导出/上传**: 导出为Markdown或上传到NotebookLM

## CLI 命令速查

| 命令 | 说明 |
|------|------|
| `picture-book generate <主题>` | 生成绘本 |
| `picture-book languages` | 列出支持的语言 |
| `picture-book version` | 显示版本 |
| `picture-book notebooklm-login` | 登录NotebookLM |
| `picture-book upload-to-notebooklm <文件>` | 上传到NotebookLM |

## 开发

```bash
# 运行测试
pytest

# 代码检查
ruff check .

# 格式化
ruff format .
```

## 待实现功能

- [x] 集成更多搜索源 (Tavily, SerpAPI)
- [x] NotebookLM自动上传
- [ ] 图片生成集成 (DALL-E, Midjourney等)
- [ ] PDF导出
- [ ] Web界面

## License

MIT

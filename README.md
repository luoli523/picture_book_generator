# Picture Book Generator 儿童绘本生成器

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🎨 根据主题自动生成适合 7-10 岁儿童阅读的绘本读物，支持一键生成 NotebookLM Slides 演示文稿。

**主要能力**：智能知识搜索 + LLM 内容适配 + 结构化绘本 + NotebookLM Slides 生成

## 📋 目录

- [功能特性](#-功能特性)
- [快速开始](#-快速开始)
- [安装](#-安装)
- [配置](#配置)
- [使用方法](#使用方法)
- [使用示例和最佳实践](#-使用示例和最佳实践)
- [项目结构](#-项目结构)
- [工作流程](#-工作流程)
- [CLI 命令速查](#-cli-命令速查)
- [故障排除](#-故障排除)
- [技术栈](#-技术栈)
- [开发](#-开发)

## ✨ 功能特性

- **智能主题搜索**: 自动从维基百科、Tavily、SerpAPI 搜索相关知识
- **儿童语言适配**: 使用 LLM 将复杂知识转化为儿童可理解的语言
- **多语言支持**: 中文、英文、日文、韩文（默认英文）
- **多 LLM 提供商**: 支持 Claude、ChatGPT、Gemini、Grok
- **结构化输出**: 生成包含章节、插图描述、知识要点的完整 Markdown 绘本
- **NotebookLM Slides**: 
  - 一键上传到 Google NotebookLM
  - 自动生成精美的 Slides 演示文稿（PDF）
  - 支持自定义生成指令、格式和长度
  - 智能文件管理（统一 notebook、避免重名）
- **Prompt 模板化**: 所有 LLM prompt 独立为文件，易于定制优化

## ⚡ 快速开始

```bash
# 1. 克隆并安装
git clone https://github.com/luoli523/picture_book_generator.git
cd picture_book_generator
./install.sh

# 2. 配置 LLM API（编辑 .env 文件）
# 设置 DEFAULT_LLM_PROVIDER 和对应的 API_KEY

# 3. 生成你的第一本绘本
picture-book generate ocean

# 4. （可选）生成 NotebookLM Slides
notebooklm login  # 首次使用需要登录
picture-book generate dinosaur --nlm-slides
```

## 📦 安装

### 基础安装

> **注意**: `.venv` 虚拟环境目录不包含在代码库中，需要自己创建。

### 方式一：一键安装脚本（推荐）

```bash
# 克隆项目
git clone <repo-url>
cd picture_book_generator

# 运行安装脚本
./install.sh
```

安装脚本会自动：
- ✓ 检查 Python 环境（需要 Python 3.10+）
- ✓ 创建虚拟环境（可选）
- ✓ 安装依赖包
- ✓ 创建 .env 配置文件
- ✓ 验证安装

### 方式二：手动安装

```bash
# 克隆项目
git clone <repo-url>
cd picture_book_generator

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装基础依赖
pip install -e .

# （可选）安装 NotebookLM 集成
pip install -e ".[notebooklm]"

# （可选）安装开发依赖
pip install -e ".[dev]"
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
# 基本用法 - 生成英文绘本（默认）
picture-book generate dinosaur

# 生成中文绘本
picture-book generate 恐龙 --lang zh

# 自定义参数
picture-book generate ocean \
    --lang en \
    --chapters 8 \
    --min-age 6 \
    --max-age 9 \
    --output my_book.md

# 查看支持的语言
picture-book languages

# 查看版本
picture-book version
```

### NotebookLM 集成与 Slides 生成

NotebookLM 集成特性：
- 所有绘本上传到统一的"儿童绘本" notebook
- 自动处理同名文件（添加时间戳）
- 生成 Slides 时只使用指定的绘本内容
- Slides 文件以绘本名称命名
- 支持自定义生成指令、格式和长度

```bash
# 首次使用：登录 NotebookLM（会打开浏览器）
notebooklm login

# 基础 Slides 生成（使用默认设置）
picture-book generate dinosaur --nlm-slides

# 默认设置：
# - instructions: "创建适合儿童和少年阅读的，卡通风格"
# - format: detailed（详细版本）
# - length: default（默认长度）

# 自定义 Slides 生成
picture-book generate ocean --nlm-slides \
  --nlm-instructions "创建色彩鲜艳、适合儿童的动画风格演示文稿" \
  --nlm-format presenter \
  --nlm-length short

# 参数说明：
# --nlm-instructions: 自定义生成指令（如："添加更多插图建议"）
# --nlm-format:      格式选项（默认: detailed）
#   - detailed:   详细版本（更多内容）
#   - presenter:  演讲者版本（演讲笔记）
# --nlm-length:      长度选项（默认: default）
#   - default:    默认长度
#   - short:      简短版本

# 手动上传已有绘本到NotebookLM
picture-book upload-to-notebooklm ./output/dinosaur.md

# 从已有NotebookLM笔记本生成Slides（使用所有源文件）
picture-book generate-slides https://notebooklm.google.com/notebook/xxx
# 或直接使用 notebook ID
picture-book generate-slides notebook-123456

# 备用工具：手动下载 Slides（当自动下载失败时）
python3 download_slides.py list                    # 列出所有笔记本
python3 download_slides.py <notebook_id>          # 下载指定笔记本的 Slides
```

## 💡 使用示例和最佳实践

### 示例 1：基础使用

```bash
# 生成英文绘本（默认）
picture-book generate ocean

# 生成中文绘本
picture-book generate 恐龙 --lang zh

# 自定义年龄和章节
picture-book generate space --min-age 8 --max-age 12 --chapters 8
```

### 示例 2：NotebookLM Slides（推荐工作流）

```bash
# 方式 1：一键生成绘本 + Slides
picture-book generate ocean --nlm-slides

# 方式 2：先生成绘本，后续再生成 Slides
picture-book generate dinosaur
picture-book upload-to-notebooklm ./output/dinosaur.md
# 在 NotebookLM 网页中手动生成 Slides
```

### 示例 3：自定义 Slides 风格

```bash
# 简短版本，演讲者格式
picture-book generate ocean --nlm-slides \
  --nlm-instructions "创建简洁的演讲稿格式，适合课堂演讲" \
  --nlm-format presenter \
  --nlm-length short

# 详细版本，教学重点
picture-book generate space --nlm-slides \
  --nlm-instructions "强调科学知识点，添加趣味问题，适合小学科学课" \
  --nlm-format detailed
```

### 最佳实践

1. **LLM 选择**：
   - Claude：最适合儿童内容创作，语言生动
   - GPT-4：知识全面，结构清晰
   - Gemini：多语言支持好，成本低

2. **主题选择**：
   - ✅ 具体主题：`"恐龙"`、`"太阳系"`、`"海洋生物"`
   - ❌ 抽象主题：`"科学"`、`"自然"`（范围太广）

3. **NotebookLM Slides**：
   - 默认设置已优化儿童阅读
   - 使用 `--nlm-instructions` 可针对特定场景定制
   - 生成时间通常 2-5 分钟，请耐心等待

4. **Prompt 定制**：
   - 所有 prompt 在 `src/picture_book_generator/prompts/` 目录
   - 可直接编辑 `.txt` 文件来优化生成效果
   - 修改后无需重启，立即生效

## 📁 项目结构

```
picture_book_generator/
├── install.sh                          # 一键安装脚本
├── download_slides.py                  # NotebookLM Slides 备用下载工具
├── src/
│   └── picture_book_generator/
│       ├── __init__.py
│       ├── cli.py                      # 命令行接口（Typer + Rich）
│       ├── core/
│       │   ├── generator.py            # 绘本生成器核心逻辑
│       │   └── models.py               # Pydantic 数据模型
│       ├── services/
│       │   ├── knowledge_search.py     # 知识搜索（Tavily/SerpAPI/Wikipedia）
│       │   ├── content_adapter.py      # LLM 内容适配服务
│       │   └── notebooklm.py           # NotebookLM 集成（notebooklm-py SDK）
│       ├── prompts/                    # LLM Prompt 模板目录
│       │   ├── __init__.py
│       │   ├── adapt_content.txt       # 内容适配 prompt
│       │   ├── generate_from_scratch.txt
│       │   ├── book_structure.txt      # 书籍结构生成 prompt
│       │   └── all_chapters.txt        # 章节内容生成 prompt
│       └── utils/
│           └── config.py               # 配置管理（pydantic-settings）
├── tests/
├── output/                             # 生成的绘本和 Slides 输出目录
├── pyproject.toml                      # 项目配置和依赖
├── .env.example                        # 环境变量配置模板
└── README.md
```

## 🔄 工作流程

### 基础绘本生成流程

```
用户输入主题 → 知识搜索 → LLM内容适配 → 结构化生成 → Markdown输出
     ↓              ↓            ↓               ↓              ↓
   "Ocean"    Tavily/Wiki    GPT/Claude   Title+Chapters    ocean.md
              SerpAPI        Gemini/Grok   Illustrations
```

### NotebookLM Slides 生成流程

```
绘本 Markdown → 上传到"儿童绘本"notebook → NotebookLM AI生成 → 下载 Slides PDF
      ↓                    ↓                        ↓                ↓
   ocean.md         Source: ocean          卡通风格详细版      ocean_slides.pdf
              (自动处理同名文件)         (可自定义指令)
```

### 详细步骤

1. **主题输入**: 用户提供主题（如 "Ocean"、"恐龙"等）
2. **知识搜索**: 并行搜索 Tavily、SerpAPI、Wikipedia，合并结果
3. **内容适配**: LLM 将知识转化为儿童语言（使用 prompts/ 中的模板）
4. **结构生成**: 
   - 生成书籍标题和摘要
   - 生成章节大纲
   - 生成每章详细内容、插图描述、知识要点
5. **输出**: 
   - Markdown 文件保存到 `output/` 目录
   - （可选）上传到 NotebookLM 生成 Slides PDF

## 🚀 CLI 命令速查

### 核心命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `generate <主题>` | 生成绘本（默认：英文，5章，7-10岁） | `picture-book generate ocean` |
| `generate <主题> --nlm-slides` | 生成绘本 + NotebookLM Slides | `picture-book generate ocean --nlm-slides` |
| `languages` | 列出支持的语言 | `picture-book languages` |
| `version` | 显示版本信息 | `picture-book version` |

### 生成参数

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--lang` | `-l` | `en` | 语言：en, zh, ja, ko |
| `--chapters` | `-c` | `5` | 章节数（3-10） |
| `--min-age` | - | `7` | 最小目标年龄 |
| `--max-age` | - | `10` | 最大目标年龄 |
| `--output` | `-o` | `./output/<主题>.md` | 输出文件路径 |

### NotebookLM 命令

| 命令 | 说明 |
|------|------|
| `notebooklm-login` | 登录 NotebookLM（首次使用前执行：`notebooklm login`） |
| `upload-to-notebooklm <文件>` | 手动上传绘本到"儿童绘本" notebook |
| `generate-slides <URL或ID>` | 从已有 notebook 生成 Slides |

### NotebookLM Slides 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--nlm-instructions` | "创建适合儿童和少年阅读的，卡通风格" | 自定义生成指令 |
| `--nlm-format` | `detailed` | 格式：detailed（详细）或 presenter（演讲者） |
| `--nlm-length` | `default` | 长度：default（默认）或 short（简短） |

### 辅助工具

| 工具 | 说明 |
|------|------|
| `./install.sh` | 一键安装和环境配置 |
| `python3 download_slides.py list` | 列出所有 NotebookLM 笔记本 |
| `python3 download_slides.py <ID>` | 手动下载 Slides（备用方案） |

## 🐛 故障排除

### NotebookLM 相关

**问题：`Storage file not found`**
```bash
# 解决：需要先登录 NotebookLM
notebooklm login
# 按提示在浏览器中完成 Google 账号登录
```

**问题：Slides 生成超时**
- NotebookLM 生成 Slides 通常需要 2-5 分钟
- 如果超过 10 分钟，可能失败
- 使用备用工具手动下载：`python3 download_slides.py <notebook_id>`

**问题：找不到 Slides 文件**
- 检查 `output/` 目录
- 文件命名格式：`<主题>_slides.pdf`

### LLM 相关

**问题：API 调用失败**
- 检查 `.env` 文件中的 API_KEY 是否正确
- 确认 `DEFAULT_LLM_PROVIDER` 设置正确
- 检查 API 配额是否用完

**问题：生成内容质量不佳**
- 尝试切换不同的 LLM 提供商
- 编辑 `src/picture_book_generator/prompts/` 中的 prompt 模板
- 增加 `MAX_TOKENS` 值（在 .env 中）

### 安装相关

**问题：`picture-book` 命令找不到**
```bash
# 确保已激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或重新安装
pip install -e .
```

## 👨‍💻 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .

# 格式化
ruff format .
```

## 🤝 贡献

欢迎贡献！请：
1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

## 🔮 技术栈

- **CLI**: Typer + Rich（命令行界面和美化输出）
- **LLM**: 多提供商支持（Anthropic、OpenAI、Google、xAI）
- **搜索**: Tavily API、SerpAPI、Wikipedia API
- **异步**: asyncio + httpx（并发请求）
- **配置**: pydantic-settings（类型安全的配置管理）
- **NotebookLM**: notebooklm-py SDK（官方 Python 接口）
- **Prompt**: 模板化管理（独立 .txt 文件）

## ✅ 已完成功能

- [x] 多语言绘本生成（中英日韩）
- [x] 多 LLM 提供商支持
- [x] 知识搜索集成（Tavily、SerpAPI、Wikipedia）
- [x] Prompt 模板化管理
- [x] NotebookLM Slides 自动生成
- [x] NotebookLM 智能文件管理
- [x] 一键安装脚本
- [x] 实时进度显示

## 🚧 计划功能

- [ ] 图片生成集成（DALL-E、Midjourney、Stable Diffusion）
- [ ] PDF 导出（带排版和插图）
- [ ] Web 界面（Gradio 或 Streamlit）
- [ ] 批量生成模式
- [ ] 绘本模板系统

## 📊 生成示例

### 生成的绘本 Markdown
- 包含书籍标题和摘要
- 5-10 个章节，每章包含：
  - 章节内容（儿童语言）
  - 插图描述（可用于 AI 图片生成）
  - 知识要点总结
- 参考资料链接

### NotebookLM Slides PDF
- 自动生成的精美演示文稿
- 卡通风格、适合儿童
- 详细版本（默认）或演讲者版本
- 通常 15-30 页

## 🔗 相关资源

- **NotebookLM**: https://notebooklm.google.com
- **notebooklm-py**: https://github.com/teng-lin/notebooklm-py
- **Tavily AI Search**: https://tavily.com
- **SerpAPI**: https://serpapi.com

## 📝 License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🌟 Star History

如果这个项目对你有帮助，请给个 ⭐️！

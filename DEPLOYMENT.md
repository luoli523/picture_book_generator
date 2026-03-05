# 📦 Web 应用部署指南

本指南介绍如何将儿童绘本生成器部署为 Web 应用。

## 🐍 Python 运行环境约定

- 本地运行或自托管服务器：统一使用项目根目录 `.venv`
- Hugging Face Spaces / Railway / Render：由平台自动管理 Python 运行环境，无需手动创建 `.venv`

## 🚀 部署选项

### 选项 1: Hugging Face Spaces（推荐，免费）

Hugging Face Spaces 提供免费的 Gradio 应用托管。

#### 步骤：

1. **创建 Space**
   - 访问 https://huggingface.co/spaces
   - 点击 "Create new Space"
   - 选择 "Gradio" 作为 SDK
   - 设置为 Public 或 Private

2. **上传代码**
   ```bash
   # 克隆 Space 仓库
   git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   cd YOUR_SPACE_NAME
   
   # 复制项目文件
   cp -r /path/to/picture_book_generator/* .
   
   # 提交
   git add .
   git commit -m "Initial commit"
   git push
   ```

3. **配置环境变量**
   - 在 Space 设置中添加 Secrets：
     - `OPENAI_API_KEY` 或其他 LLM API Key
     - `DEFAULT_LLM_PROVIDER`
     - 其他必需的环境变量

4. **访问应用**
   - Space 会自动构建和部署
   - 访问 `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`

#### 限制：
- ⚠️ CPU 限制（生成速度较慢）
- ⚠️ 15 分钟超时限制
- ⚠️ NotebookLM 登录在共享环境中可能有问题

---

### 选项 2: Railway（简单，$5-10/月）

Railway 提供更好的性能和更长的超时时间。

#### 步骤：

1. **安装 Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **创建项目**
   ```bash
   cd picture_book_generator
   railway init
   ```

3. **配置环境变量**
   ```bash
   railway variables set OPENAI_API_KEY=your-key
   railway variables set DEFAULT_LLM_PROVIDER=openai
   # 添加其他变量...
   ```

4. **部署**
   ```bash
   # 创建 Procfile
   echo "web: python app.py" > Procfile
   
   # 部署
   railway up
   ```

5. **生成域名**
   ```bash
   railway domain
   ```

---

### 选项 3: Render（免费层可用）

#### 步骤：

1. **连接 GitHub 仓库**
   - 访问 https://render.com
   - 创建新的 Web Service
   - 连接到你的 GitHub 仓库

2. **配置**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Environment**: Python 3.10+

3. **添加环境变量**
   - 在 Render 面板中添加环境变量

4. **部署**
   - Render 会自动构建和部署

---

### 选项 4: 本地运行

最简单的方式，适合个人使用或开发测试。

```bash
# 进入项目目录
cd picture_book_generator

# 创建并激活 .venv
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行应用
python app.py

# 访问 http://localhost:7860
```

#### 公开分享（临时）：
在 `app.py` 中设置 `share=True`：
```python
demo.launch(share=True)  # 生成公开分享链接
```

---

## 🔐 安全配置

### API Key 管理

**选项 A: 环境变量（推荐用于个人/团队）**
```bash
# 在部署平台设置环境变量
OPENAI_API_KEY=sk-xxx
```

**选项 B: 让用户输入（推荐用于公开服务）**
修改 `app.py`，添加 API Key 输入框：
```python
api_key_input = gr.Textbox(
    label="OpenAI API Key",
    type="password",
    placeholder="sk-xxx",
)
```

### 速率限制

为防止滥用，建议添加速率限制：

```python
import time
from collections import defaultdict

# 简单的速率限制器
last_request = defaultdict(float)

def rate_limit(user_id: str, max_per_hour: int = 10):
    now = time.time()
    if now - last_request[user_id] < 3600 / max_per_hour:
        raise gr.Error("请求过于频繁，请稍后再试")
    last_request[user_id] = now
```

---

## 📊 成本估算

### 每次生成成本（使用 OpenAI）

| 组件 | Token 用量 | 成本 (GPT-4o) |
|------|-----------|--------------|
| 知识搜索 | 500-1000 | $0.003-0.006 |
| 内容适配 | 2000-3000 | $0.012-0.018 |
| 书籍结构 | 1000-1500 | $0.006-0.009 |
| 章节内容 | 3000-5000 | $0.018-0.030 |
| NotebookLM | 免费 | $0 |
| **总计** | ~6500-10500 | **$0.04-0.06** |

### 月度成本估算

| 生成次数/月 | LLM 成本 | 托管成本 | 总成本 |
|------------|---------|---------|--------|
| 100 | $4-6 | $0 (HF) | $4-6 |
| 500 | $20-30 | $10 (Railway) | $30-40 |
| 1000 | $40-60 | $20 (Railway) | $60-80 |

---

## 🐛 故障排除

### 问题：NotebookLM 登录失败

**原因**: 共享托管环境无法交互式登录

**解决方案**:
1. 本地运行 `notebooklm login`
2. 复制认证文件到服务器
3. 或者禁用 NotebookLM 功能

### 问题：生成超时

**原因**: 免费托管有超时限制

**解决方案**:
1. 使用付费托管（Railway/Render）
2. 减少章节数
3. 使用更快的 LLM（如 Gemini）

### 问题：API Key 无效

**检查**:
1. 环境变量是否正确设置
2. API Key 是否有效
3. 是否有足够的配额

---

## 📈 性能优化

### 1. 缓存结果
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generate(topic: str, language: str, ...):
    # 缓存相同参数的结果
    pass
```

### 2. 使用更快的 LLM
- Gemini 2.0 Flash（最快）
- GPT-4o mini（平衡）
- Claude Haiku（便宜）

### 3. 异步处理
```python
# 使用 Gradio 的异步支持
async def generate_async(...):
    # 异步生成
    pass
```

---

## 🎯 下一步

1. ✅ 部署到 Hugging Face Spaces
2. ⚡ 添加用户认证（可选）
3. 💰 集成支付系统（可选）
4. 📊 添加使用统计
5. 🔔 添加邮件通知

---

## 📚 相关资源

- [Gradio 文档](https://gradio.app/docs/)
- [Hugging Face Spaces 指南](https://huggingface.co/docs/hub/spaces)
- [Railway 文档](https://docs.railway.app/)
- [Render 文档](https://render.com/docs)

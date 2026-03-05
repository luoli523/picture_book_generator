# 儿童绘本网站改版蓝图（V1）

## 1. 目标与定位

### 1.1 目标用户
- 3-12 岁孩子的家长（核心）
- 小学教师/培训机构老师（次要）

### 1.2 价值主张
- 为“我家孩子”定制绘本，而不是通用绘本
- 通过可视化配置快速生成可阅读、可下载、可分享的成品
- 家长可提供自己的故事草稿，系统自动改写成绘本结构

### 1.3 成功指标（MVP）
- 首次访问到开始生成的转化率 > 25%
- 生成任务完成率 > 80%
- 下载率（Markdown/PDF 任一）> 40%
- 二次生成率（同用户二次使用）> 20%

## 2. 产品范围（MVP）

### 2.1 必做
- 首页（营销 + 功能导流）
- 绘本工坊（多步骤生成器）
- 结果页（在线预览 + 下载）
- 我的绘本（本地/账号态可扩展）

### 2.2 暂缓
- 社区广场（UGC）
- 支付系统
- 多人协作编辑

## 3. 信息架构（IA）

1. `/` 首页  
2. `/create` 绘本工坊（核心）  
3. `/styles` 风格库  
4. `/library` 我的绘本  
5. `/book/:id` 绘本详情与阅读  
6. `/safety` 安全与隐私说明  

## 4. 页面方案

## 4.1 首页
- Hero：一句话价值 + 主 CTA（开始制作）
- 快速示例：展示 4 种风格封面卡
- 3 步流程：填写孩子信息 -> 选择故事来源 -> 生成与下载
- 家长场景区块：睡前故事/科普启蒙/情绪引导
- FAQ：时间、隐私、内容安全

## 4.2 绘本工坊 `/create`（向导式）

步骤 1：孩子画像
- 年龄段：3-5 / 6-8 / 9-12
- 性别：男孩/女孩/不限定
- 阅读能力：启蒙/基础/进阶
- 兴趣标签：恐龙、太空、海洋、自然、情绪管理等

步骤 2：故事来源
- 选项 A：主题生成（输入主题）
- 选项 B：家长提供故事（长文本）
- 选项 C：混合模式（主题 + 草稿）

步骤 3：绘本风格
- 视觉风格（卡片选择）
- 叙事语气：温柔陪伴/冒险探索/幽默搞笑/科普严谨
- 教育目标：知识学习/行为习惯/情绪认知/睡前安抚

步骤 4：高级参数
- 语言：zh/en/ja/ko
- 章节：3-10
- 每章长度：短/中/长
- 是否生成插图提示词
- 是否生成 NotebookLM Slides

步骤 5：生成与预览
- 显示任务状态（检索/改写/章节生成/导出）
- 先返回封面 + 前两章预览（可快速重试）
- 再返回完整版本（Markdown + PDF/Slides）

## 4.3 结果页 `/book/:id`
- 绘本封面
- 元信息：孩子年龄段、主题、风格、创建时间
- 在线翻页阅读（章节导航）
- 下载：Markdown / Slides PDF
- 二次编辑：复制参数重新生成

## 4.4 风格库 `/styles`
- 风格列表 + 示例页
- 每个风格展示：
  - 封面示例
  - 颜色与字体
  - 文风关键词
  - 适合年龄段

## 5. 风格模板（首批 4 套）

## 5.1 Sunny Story（暖阳纸本）
- 关键词：温暖、亲子、睡前
- 配色：奶油白 / 日光黄 / 木质棕 / 草绿
- 字体：Baloo 2（标题）+ Noto Sans SC（正文）

## 5.2 Ocean Pop（海洋活力）
- 关键词：科普、探索、明快
- 配色：海军蓝 / 青绿 / 浅蓝 / 珊瑚橙
- 字体：Fredoka（标题）+ Noto Sans SC（正文）

## 5.3 Forest Sketch（森林手绘）
- 关键词：自然、手作、安静
- 配色：苔藓绿 / 卡其 / 米白 / 树皮棕
- 字体：Comfortaa（标题）+ Noto Sans SC（正文）

## 5.4 Space Quest（太空冒险）
- 关键词：冒险、想象、科技启蒙
- 配色：深蓝黑 / 星光白 / 电光青 / 亮橙
- 字体：Bungee（标题）+ Noto Sans SC（正文）

## 6. 关键交互与体验细节

- 使用“问答向导”替代传统大表单
- 每个步骤右侧实时预览“生成设定摘要”
- 风格选择采用大卡片（封面缩略图 + 关键词）
- 生成阶段展示可视化进度条与阶段说明
- 异常可恢复：失败后保留已填参数，支持一键重试

## 7. 字段定义（前后端契约草案）

```json
{
  "child_profile": {
    "age_group": "6-8",
    "gender": "girl",
    "reading_level": "basic",
    "interests": ["ocean", "animals"]
  },
  "content_source": {
    "mode": "hybrid",
    "topic": "海洋探险",
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

## 8. 与现有代码的映射

- 继续复用 `PictureBookGenerator.generate()` 主流程
- 在生成前新增“参数增强层”：
  - 将孩子画像、风格、教育目标拼接到 prompt 上下文
  - 统一映射到 `BookConfig` 与 `ContentAdapterService` 输入
- 继续复用 NotebookLM 服务、PDF 拆分和 Telegram 服务

建议新增模块：
- `src/picture_book_generator/web/schemas.py`（请求/响应模型）
- `src/picture_book_generator/web/prompt_enhancer.py`（风格与人群参数注入）
- `src/picture_book_generator/web/tasks.py`（异步任务管理）

## 9. 前端视觉与技术建议

## 9.1 技术栈（建议）
- Next.js + TypeScript + Tailwind CSS + Framer Motion
- 组件层：Radix UI 或 shadcn/ui（可定制）
- 状态管理：Zustand（轻量）

## 9.2 视觉规范（核心变量）
- 圆角：16px/24px
- 阴影：柔和大面积，避免硬边
- 卡片：高留白 + 插画缩略图 + 色块背景
- 动效：页面首屏渐入，步骤切换滑动，卡片 hover 轻浮起

## 10. 后端 API 草案

- `POST /api/v1/books/generate` 创建任务
- `GET /api/v1/books/tasks/:task_id` 查询进度
- `GET /api/v1/books/:book_id` 获取结果与元数据
- `GET /api/v1/books/:book_id/download?type=md|pdf` 下载文件
- `GET /api/v1/styles` 风格模板列表

响应示例（任务进度）：

```json
{
  "task_id": "task_123",
  "status": "running",
  "stage": "generate_chapters",
  "progress": 68,
  "message": "正在生成章节内容"
}
```

## 11. 内容安全与隐私

- 默认启用儿童安全内容约束（过滤暴力/成人/恐怖描述）
- 家长输入故事仅用于本次生成（默认不训练）
- 提供“清空我的数据”入口
- 明确标注 AI 生成内容需家长审阅

## 12. 里程碑计划（4 周）

第 1 周：体验与架构
- 定稿 IA、线框、视觉方向
- 定义 API 契约与字段映射

第 2 周：前后端骨架
- 前端页面框架 + 向导流程
- 后端任务 API + 状态查询

第 3 周：生成与结果链路
- 接入现有生成逻辑
- 完成结果页阅读与下载

第 4 周：打磨与上线
- 动效、可用性、移动端适配
- 性能优化与异常处理

## 13. 我们下一步的决策点

1. 确认品牌视觉方向（4 套风格中先主推哪一套）
2. 确认 MVP 是否包含“我的绘本”登录态
3. 确认首发是否保留 NotebookLM Slides（默认开/默认关）

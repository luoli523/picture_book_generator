"""绘本生成器核心逻辑"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..services.content_adapter import ContentAdapterService
from ..services.knowledge_search import KnowledgeSearchService
from ..utils.config import Language, Settings
from .models import BookConfig, Chapter, PictureBook

console = Console()


class PictureBookGenerator:
    """儿童绘本生成器

    工作流程:
    1. 根据主题搜索相关知识
    2. 将知识适配为儿童可读内容
    3. 生成绘本结构和内容
    4. 可选: 上传到NotebookLM生成最终产品
    """

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.content_adapter = ContentAdapterService(self.settings)

    def _build_customization_context(self, config: BookConfig) -> str:
        """构建个性化生成上下文，注入到LLM提示词"""
        interest_text = ", ".join(config.interests) if config.interests else "none"
        return (
            "Customization requirements:\n"
            f"- Child gender: {config.child_gender}\n"
            f"- Reading level: {config.reading_level}\n"
            f"- Interests: {interest_text}\n"
            f"- Style theme: {config.style_theme}\n"
            f"- Narration tone: {config.narration_tone}\n"
            f"- Education goal: {config.education_goal}\n"
            f"- Chapter length preference: {config.chapter_length}\n"
            "- Prioritize a warm, age-appropriate, parent-friendly storytelling style.\n"
        )

    async def _collect_knowledge(self, config: BookConfig) -> dict:
        """按来源模式收集知识内容"""
        parent_story = config.parent_story.strip()
        topic_with_interest = config.topic
        if config.interests:
            topic_with_interest = f"{config.topic} {' '.join(config.interests)}"

        # 仅使用家长故事
        if config.source_mode == "parent_story" and parent_story:
            return {
                "topic": config.topic,
                "content": [parent_story],
                "sources": ["Parent provided story"],
            }

        # 主题搜索（默认）
        async with KnowledgeSearchService(self.settings) as knowledge_service:
            knowledge = await knowledge_service.search(topic_with_interest)

        # 混合模式：搜索 + 家长故事
        if config.source_mode == "hybrid" and parent_story:
            knowledge["content"].append(f"[Parent Story]\n{parent_story}")
            knowledge["sources"].append("Parent provided story")

        return knowledge

    async def generate(self, config: BookConfig) -> PictureBook:
        """生成绘本

        Args:
            config: 绘本配置

        Returns:
            生成的绘本对象
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # 步骤1: 搜索知识
            task = progress.add_task(f"正在准备关于「{config.topic}」的素材...", total=None)
            knowledge = await self._collect_knowledge(config)
            progress.update(task, completed=True)

            # 步骤2: 适配内容
            task = progress.add_task("正在将内容适配为儿童可读形式...", total=None)
            adapted_content = await self.content_adapter.adapt(
                knowledge=knowledge,
                age_range=config.age_range,
                language=config.language,
                extra_context=self._build_customization_context(config),
            )
            progress.update(task, completed=True)

            # 步骤3: 生成绘本结构
            task = progress.add_task("正在生成绘本结构...", total=None)
            book = await self._create_book_structure(config, adapted_content)
            progress.update(task, completed=True)

            # 步骤4: 生成各章节内容
            task = progress.add_task("正在生成章节内容...", total=None)
            book = await self._generate_chapters(book, config, adapted_content)
            progress.update(task, completed=True)

        console.print(f"\n[green]绘本《{book.title}》生成完成![/green]")
        return book

    async def _create_book_structure(
        self, config: BookConfig, adapted_content: dict
    ) -> PictureBook:
        """创建绘本基础结构

        一次LLM调用生成:
        1. 绘本标题
        2. 绘本简介
        3. 章节大纲
        """
        # 一次调用生成标题、简介、章节大纲
        structure = await self.content_adapter.generate_book_structure(
            topic=config.topic,
            language=config.language,
            age_range=config.age_range,
            chapter_count=config.chapter_count,
            adapted_content=adapted_content.get("summary", ""),
            extra_context=self._build_customization_context(config),
        )

        chapter_titles = structure.get("chapters", [])

        # 根据语言设置年龄格式和默认标题
        age_formats = {
            Language.ENGLISH: f"Ages {config.age_range[0]}-{config.age_range[1]}",
            Language.CHINESE: f"{config.age_range[0]}-{config.age_range[1]}岁",
            Language.JAPANESE: f"{config.age_range[0]}-{config.age_range[1]}歳",
            Language.KOREAN: f"{config.age_range[0]}-{config.age_range[1]}세",
        }
        default_titles = {
            Language.ENGLISH: f"Exploring the World of {config.topic}",
            Language.CHINESE: f"探索{config.topic}的奇妙世界",
            Language.JAPANESE: f"{config.topic}の不思議な世界",
            Language.KOREAN: f"{config.topic}의 신비로운 세계",
        }

        # 创建绘本对象（章节内容在Step 4中填充）
        return PictureBook(
            title=structure.get("title", default_titles.get(config.language, default_titles[Language.ENGLISH])),
            topic=config.topic,
            language=config.language,
            target_age=age_formats.get(config.language, age_formats[Language.ENGLISH]),
            summary=structure.get("summary", ""),
            chapters=[
                Chapter(
                    number=i + 1,
                    title=chapter_titles[i] if i < len(chapter_titles) else f"Chapter {i+1}",
                    content="",
                    knowledge_points=[],
                )
                for i in range(config.chapter_count)
            ],
            sources=adapted_content.get("sources", []),
        )

    async def _generate_chapters(
        self, book: PictureBook, config: BookConfig, adapted_content: dict
    ) -> PictureBook:
        """生成各章节详细内容

        一次LLM调用生成所有章节:
        1. 故事性内容（200-400字）
        2. 知识要点
        3. 插图描述（可选）
        """
        # 收集章节标题
        chapter_titles = [ch.title for ch in book.chapters]

        # 一次调用生成所有章节内容
        chapters_data = await self.content_adapter.generate_all_chapters(
            topic=config.topic,
            chapter_titles=chapter_titles,
            language=config.language,
            age_range=config.age_range,
            adapted_content=adapted_content.get("summary", ""),
            include_illustration=config.include_illustrations,
            extra_context=self._build_customization_context(config),
        )

        # 更新章节内容
        for i, chapter in enumerate(book.chapters):
            if i < len(chapters_data):
                chapter_data = chapters_data[i]
                chapter.content = chapter_data.get("content", "")
                chapter.knowledge_points = chapter_data.get("knowledge_points", [])
                if config.include_illustrations:
                    chapter.illustration_prompt = chapter_data.get("illustration_prompt")

        return book

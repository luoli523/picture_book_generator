"""绘本生成器核心逻辑"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..services.content_adapter import ContentAdapterService
from ..services.knowledge_search import KnowledgeSearchService
from ..services.notebooklm import NotebookLMService
from ..utils.config import Settings
from .models import BookConfig, PictureBook

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
        self.knowledge_service = KnowledgeSearchService(self.settings)
        self.content_adapter = ContentAdapterService(self.settings)
        self.notebooklm_service = NotebookLMService(self.settings)

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
            task = progress.add_task(f"正在搜索关于「{config.topic}」的知识...", total=None)
            knowledge = await self.knowledge_service.search(config.topic)
            progress.update(task, completed=True)

            # 步骤2: 适配内容
            task = progress.add_task("正在将内容适配为儿童可读形式...", total=None)
            adapted_content = await self.content_adapter.adapt(
                knowledge=knowledge,
                age_range=config.age_range,
                language=config.language,
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
        """创建绘本基础结构"""
        # TODO: 使用LLM生成绘本标题和结构
        return PictureBook(
            title=f"探索{config.topic}的奇妙世界",
            topic=config.topic,
            language=config.language,
            target_age=f"{config.age_range[0]}-{config.age_range[1]}岁",
            summary=adapted_content.get("summary", ""),
            sources=adapted_content.get("sources", []),
        )

    async def _generate_chapters(
        self, book: PictureBook, config: BookConfig, adapted_content: dict
    ) -> PictureBook:
        """生成各章节内容"""
        # TODO: 使用LLM为每个章节生成详细内容
        return book

    async def upload_to_notebooklm(self, book: PictureBook) -> str:
        """上传绘本到NotebookLM

        Args:
            book: 绘本对象

        Returns:
            NotebookLM链接
        """
        markdown_content = book.to_markdown()
        return await self.notebooklm_service.upload(markdown_content)

"""数据模型定义"""

from typing import Optional

from pydantic import BaseModel, Field

from ..utils.config import Language


class BookConfig(BaseModel):
    """绘本配置"""

    topic: str = Field(..., description="绘本主题")
    language: Language = Field(default=Language.CHINESE, description="目标语言")
    age_range: tuple[int, int] = Field(default=(7, 10), description="目标年龄范围")
    chapter_count: int = Field(default=5, ge=3, le=10, description="章节数量")
    include_illustrations: bool = Field(default=True, description="是否包含插图描述")


class Chapter(BaseModel):
    """绘本章节"""

    number: int = Field(..., description="章节编号")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    illustration_prompt: Optional[str] = Field(None, description="插图生成提示词")
    knowledge_points: list[str] = Field(default_factory=list, description="知识要点")


class PictureBook(BaseModel):
    """绘本成品"""

    title: str = Field(..., description="绘本标题")
    topic: str = Field(..., description="主题")
    language: Language = Field(..., description="语言")
    target_age: str = Field(..., description="目标年龄")
    summary: str = Field(..., description="内容简介")
    chapters: list[Chapter] = Field(default_factory=list, description="章节列表")
    sources: list[str] = Field(default_factory=list, description="知识来源")

    def to_markdown(self) -> str:
        """导出为Markdown格式"""
        lines = [
            f"# {self.title}",
            "",
            f"**主题**: {self.topic}",
            f"**适合年龄**: {self.target_age}",
            f"**语言**: {self.language.value}",
            "",
            "## 简介",
            self.summary,
            "",
        ]

        for chapter in self.chapters:
            lines.extend(
                [
                    f"## 第{chapter.number}章: {chapter.title}",
                    "",
                    chapter.content,
                    "",
                ]
            )
            if chapter.illustration_prompt:
                lines.extend(
                    [
                        f"*插图描述: {chapter.illustration_prompt}*",
                        "",
                    ]
                )
            if chapter.knowledge_points:
                lines.append("**知识要点:**")
                for point in chapter.knowledge_points:
                    lines.append(f"- {point}")
                lines.append("")

        if self.sources:
            lines.extend(["## 参考来源", ""])
            for source in self.sources:
                lines.append(f"- {source}")

        return "\n".join(lines)

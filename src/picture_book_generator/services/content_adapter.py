"""内容适配服务 - 将知识内容转化为适合儿童阅读的形式"""

from anthropic import AsyncAnthropic

from ..core.models import Language
from ..utils.config import Settings


class ContentAdapterService:
    """内容适配服务

    负责将搜索到的知识内容转化为适合目标年龄段儿童阅读的形式。
    主要功能:
    - 简化语言复杂度
    - 添加趣味性元素
    - 结构化内容
    - 生成配图描述
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def adapt(
        self,
        knowledge: dict,
        age_range: tuple[int, int],
        language: Language,
    ) -> dict:
        """将知识适配为儿童可读内容

        Args:
            knowledge: 原始知识内容
            age_range: 目标年龄范围
            language: 目标语言

        Returns:
            适配后的内容
        """
        topic = knowledge.get("topic", "")
        raw_content = "\n\n".join(knowledge.get("content", []))

        if not raw_content:
            # 如果没有搜索到内容，使用LLM直接生成
            return await self._generate_content_from_scratch(topic, age_range, language)

        # 使用LLM适配内容
        prompt = self._build_adaptation_prompt(topic, raw_content, age_range, language)

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        adapted_text = response.content[0].text

        return {
            "summary": adapted_text,
            "sources": knowledge.get("sources", []),
            "original_content": raw_content,
        }

    async def _generate_content_from_scratch(
        self,
        topic: str,
        age_range: tuple[int, int],
        language: Language,
    ) -> dict:
        """从零开始生成内容"""
        language_name = {
            Language.CHINESE: "中文",
            Language.ENGLISH: "English",
            Language.JAPANESE: "日本語",
            Language.KOREAN: "한국어",
        }.get(language, "中文")

        prompt = f"""你是一位专业的儿童教育内容创作者。请为{age_range[0]}-{age_range[1]}岁的儿童创作关于「{topic}」的教育内容。

要求:
1. 使用{language_name}撰写
2. 语言简单易懂，适合目标年龄段
3. 内容有趣生动，能吸引儿童注意力
4. 包含科学准确的知识点
5. 适合制作成绘本的形式

请生成:
1. 主题简介 (2-3句话)
2. 5-8个有趣的知识要点
3. 建议的故事线或章节结构
"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        return {
            "summary": response.content[0].text,
            "sources": ["AI生成内容"],
            "original_content": "",
        }

    def _build_adaptation_prompt(
        self,
        topic: str,
        raw_content: str,
        age_range: tuple[int, int],
        language: Language,
    ) -> str:
        """构建内容适配提示词"""
        language_name = {
            Language.CHINESE: "中文",
            Language.ENGLISH: "English",
            Language.JAPANESE: "日本語",
            Language.KOREAN: "한국어",
        }.get(language, "中文")

        return f"""你是一位专业的儿童教育内容创作者。请将以下关于「{topic}」的内容改写为适合{age_range[0]}-{age_range[1]}岁儿童阅读的版本。

原始内容:
{raw_content}

要求:
1. 使用{language_name}撰写
2. 语言简单易懂，避免专业术语
3. 添加趣味性元素，如比喻、拟人等
4. 保持科学准确性
5. 适合制作成绘本的形式
6. 提炼出5-8个核心知识要点

请输出:
1. 适合儿童的内容概述
2. 关键知识要点列表
3. 建议的章节结构
"""

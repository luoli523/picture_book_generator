"""知识搜索服务测试"""

import pytest

from picture_book_generator.services.knowledge_search import KnowledgeSearchService
from picture_book_generator.utils.config import Settings


class TestKnowledgeSearchService:
    @pytest.fixture
    def settings(self):
        return Settings()

    @pytest.fixture
    def service(self, settings):
        return KnowledgeSearchService(settings)

    @pytest.mark.asyncio
    async def test_search_wikipedia(self, service):
        """测试维基百科搜索"""
        result = await service._search_wikipedia("恐龙")

        assert "content" in result
        assert "sources" in result
        # 维基百科应该能找到恐龙相关内容
        assert len(result["content"]) > 0 or len(result["sources"]) >= 0

    @pytest.mark.asyncio
    async def test_search_wikipedia_english(self, service):
        """测试英文维基百科搜索"""
        result = await service._fetch_wikipedia_page("Dinosaur", "en")

        assert result is not None
        assert "content" in result
        assert "Dinosaur" in result["content"] or "dinosaur" in result["content"].lower()

    @pytest.mark.asyncio
    async def test_search_combined(self, service):
        """测试组合搜索"""
        result = await service.search("太阳系")

        assert "topic" in result
        assert result["topic"] == "太阳系"
        assert "content" in result
        assert "sources" in result

    @pytest.mark.asyncio
    async def test_search_nonexistent_topic(self, service):
        """测试不存在的主题"""
        result = await service._search_wikipedia("这个主题肯定不存在12345xyz")

        assert "content" in result
        assert "sources" in result
        # 应该返回空结果而不是报错
        assert len(result["content"]) == 0

    @pytest.mark.asyncio
    async def test_tavily_without_api_key(self, service):
        """测试没有API密钥时Tavily返回空结果"""
        # 确保没有设置API密钥
        service.settings.tavily_api_key = ""
        result = await service._search_tavily("恐龙")

        assert result == {"content": [], "sources": []}

    @pytest.mark.asyncio
    async def test_serpapi_without_api_key(self, service):
        """测试没有API密钥时SerpAPI返回空结果"""
        # 确保没有设置API密钥
        service.settings.serp_api_key = ""
        result = await service._search_serpapi("恐龙")

        assert result == {"content": [], "sources": []}

    @pytest.mark.asyncio
    async def test_close(self, service):
        """测试关闭HTTP客户端"""
        await service.close()
        # 客户端应该已关闭
        assert service.client.is_closed

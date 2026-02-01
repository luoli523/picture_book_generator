"""NotebookLM服务 - 集成Google NotebookLM生成最终绘本"""

import tempfile
from pathlib import Path

from ..utils.config import Settings

# Playwright 是可选依赖
try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class NotebookLMService:
    """NotebookLM服务

    负责将生成的绘本内容上传到Google NotebookLM，
    利用其功能生成:
    - 音频播客版本
    - 思维导图
    - 互动问答

    使用前需要:
    1. pip install picture-book-generator[notebooklm]
    2. playwright install chromium
    3. 手动登录Google账号并保存浏览器状态
    """

    NOTEBOOKLM_URL = "https://notebooklm.google.com"

    def __init__(self, settings: Settings, user_data_dir: str | None = None):
        self.settings = settings
        self.user_data_dir = user_data_dir or str(Path.home() / ".picture-book" / "chrome-data")

    def _check_playwright(self):
        """检查Playwright是否可用"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright未安装。请运行:\n"
                "  pip install picture-book-generator[notebooklm]\n"
                "  playwright install chromium"
            )

    async def login(self) -> None:
        """手动登录Google账号

        会打开浏览器让用户登录，登录后浏览器状态会被保存
        """
        self._check_playwright()

        Path(self.user_data_dir).mkdir(parents=True, exist_ok=True)

        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = await browser.new_page()
            await page.goto(self.NOTEBOOKLM_URL)

            print("请在浏览器中登录Google账号，完成后按Enter继续...")
            input()

            await browser.close()
            print("登录状态已保存")

    async def upload(self, content: str, title: str = "儿童绘本") -> str:
        """上传内容到NotebookLM

        Args:
            content: Markdown格式的绘本内容
            title: 笔记本标题

        Returns:
            NotebookLM笔记本链接
        """
        self._check_playwright()

        # 创建临时Markdown文件
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_file = f.name

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch_persistent_context(
                    self.user_data_dir,
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"],
                )
                page = await browser.new_page()
                await page.goto(self.NOTEBOOKLM_URL)

                # 等待页面加载
                await page.wait_for_load_state("networkidle")

                # 点击"新建笔记本"按钮
                # 注意: 选择器可能需要根据实际页面调整
                new_notebook_btn = page.locator('button:has-text("New notebook")')
                if await new_notebook_btn.count() > 0:
                    await new_notebook_btn.click()
                else:
                    # 尝试中文版
                    new_notebook_btn = page.locator('button:has-text("新建笔记本")')
                    if await new_notebook_btn.count() > 0:
                        await new_notebook_btn.click()

                # 上传文件
                file_input = page.locator('input[type="file"]')
                await file_input.set_input_files(temp_file)

                # 等待上传完成
                await page.wait_for_timeout(3000)

                # 获取当前URL作为笔记本链接
                notebook_url = page.url

                await browser.close()

                return notebook_url

        finally:
            Path(temp_file).unlink(missing_ok=True)

    async def generate_podcast(self, notebook_url: str) -> str:
        """生成播客版本

        Args:
            notebook_url: NotebookLM笔记本URL

        Returns:
            播客音频链接
        """
        self._check_playwright()

        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = await browser.new_page()
            await page.goto(notebook_url)
            await page.wait_for_load_state("networkidle")

            # 点击"Audio Overview"按钮生成播客
            # 注意: 选择器可能需要根据实际页面调整
            audio_btn = page.locator('button:has-text("Audio Overview")')
            if await audio_btn.count() > 0:
                await audio_btn.click()

            # 等待生成完成 (可能需要较长时间)
            print("正在生成播客，请稍候...")
            await page.wait_for_timeout(60000)  # 等待60秒

            # TODO: 获取播客链接
            await browser.close()

            return "播客生成中，请在NotebookLM中查看"

    async def generate_slides(self, notebook_url: str, download_dir: str | None = None) -> str:
        """生成Slides并下载

        Args:
            notebook_url: NotebookLM笔记本URL
            download_dir: 下载目录，默认为当前目录

        Returns:
            下载的文件路径
        """
        self._check_playwright()

        download_path = Path(download_dir) if download_dir else Path.cwd()
        download_path.mkdir(parents=True, exist_ok=True)

        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                accept_downloads=True,
            )
            page = await browser.new_page()
            await page.goto(notebook_url)
            await page.wait_for_load_state("networkidle")

            print("正在生成Slides...")

            # 点击"Notebook guide"或展开面板
            # NotebookLM的UI: 右侧有 Audio Overview, Briefing Doc, Study Guide, Timeline 等选项
            # Slides/演示文稿选项通常在这个区域

            # 等待页面完全加载
            await page.wait_for_timeout(3000)

            # 尝试找到并点击 Slides/演示文稿 按钮
            slides_selectors = [
                'button:has-text("Slides")',
                'button:has-text("演示文稿")',
                'button:has-text("Presentation")',
                '[aria-label*="Slides"]',
                '[aria-label*="slides"]',
            ]

            clicked = False
            for selector in slides_selectors:
                btn = page.locator(selector)
                if await btn.count() > 0:
                    await btn.first.click()
                    clicked = True
                    print(f"点击了: {selector}")
                    break

            if not clicked:
                # 如果没找到直接的按钮，可能需要先展开菜单
                # 尝试点击 "Create" 或 "+" 按钮
                create_selectors = [
                    'button:has-text("Create")',
                    'button:has-text("创建")',
                    'button[aria-label*="Create"]',
                    'button:has-text("Generate")',
                ]
                for selector in create_selectors:
                    btn = page.locator(selector)
                    if await btn.count() > 0:
                        await btn.first.click()
                        await page.wait_for_timeout(1000)
                        # 再次尝试点击 Slides
                        for slides_selector in slides_selectors:
                            slides_btn = page.locator(slides_selector)
                            if await slides_btn.count() > 0:
                                await slides_btn.first.click()
                                clicked = True
                                break
                        if clicked:
                            break

            if not clicked:
                print("未找到Slides按钮，请手动操作浏览器生成Slides")
                print("完成后按Enter继续...")
                input()

            # 等待生成完成
            print("等待Slides生成...")
            await page.wait_for_timeout(10000)

            # 尝试下载
            download_selectors = [
                'button:has-text("Download")',
                'button:has-text("下载")',
                'button:has-text("Export")',
                'button:has-text("导出")',
                '[aria-label*="Download"]',
                '[aria-label*="download"]',
            ]

            downloaded_file = None
            for selector in download_selectors:
                btn = page.locator(selector)
                if await btn.count() > 0:
                    # 等待下载
                    async with page.expect_download() as download_info:
                        await btn.first.click()
                    download = await download_info.value
                    downloaded_file = download_path / download.suggested_filename
                    await download.save_as(str(downloaded_file))
                    print(f"已下载: {downloaded_file}")
                    break

            if not downloaded_file:
                print("未能自动下载，请手动下载文件")
                print("完成后按Enter继续...")
                input()

            await browser.close()

            return str(downloaded_file) if downloaded_file else "请手动在NotebookLM中下载"

    async def generate_mindmap(self, notebook_url: str) -> str:
        """生成思维导图

        Args:
            notebook_url: NotebookLM笔记本URL

        Returns:
            思维导图链接
        """
        # NotebookLM目前不直接支持思维导图导出
        raise NotImplementedError(
            "NotebookLM不直接支持思维导图。"
            "建议使用NotebookLM的摘要功能，然后用其他工具生成思维导图。"
        )

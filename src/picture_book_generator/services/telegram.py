"""Telegram服务 - 发送绘本图片和社交媒体文案到Telegram"""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from ..utils.config import Settings


class TelegramService:
    """通过Telegram Bot API发送绘本图片和双语文案"""

    API_BASE = "https://api.telegram.org/bot{token}"

    def __init__(self, settings: Settings):
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        if not self.token or not self.chat_id:
            raise ValueError(
                "Telegram 未配置。请在 .env 中设置:\n"
                "  TELEGRAM_BOT_TOKEN=your_bot_token\n"
                "  TELEGRAM_CHAT_ID=your_chat_id"
            )
        self.base_url = self.API_BASE.format(token=self.token)

    async def send_message(self, text: str, parse_mode: str = "HTML") -> dict:
        """发送文本消息"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/sendMessage",
                data={"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode},
            )
            resp.raise_for_status()
            return resp.json()

    async def send_photo(
        self, photo_path: str, caption: str = "", parse_mode: str = "HTML"
    ) -> dict:
        """发送单张图片"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(photo_path, "rb") as f:
                resp = await client.post(
                    f"{self.base_url}/sendPhoto",
                    data={
                        "chat_id": self.chat_id,
                        "caption": caption,
                        "parse_mode": parse_mode,
                    },
                    files={"photo": (Path(photo_path).name, f, "image/png")},
                )
            resp.raise_for_status()
            return resp.json()

    async def send_media_group(
        self, photo_paths: list[str], caption: str = "", parse_mode: str = "HTML"
    ) -> dict:
        """发送图片组（最多10张）

        Telegram sendMediaGroup 仅支持第一张图片带 caption。
        """
        import json

        media = []
        for i, path in enumerate(photo_paths[:10]):
            item = {"type": "photo", "media": f"attach://photo_{i}"}
            if i == 0 and caption:
                item["caption"] = caption
                item["parse_mode"] = parse_mode
            media.append(item)

        files = {}
        file_handles = []
        for i, path in enumerate(photo_paths[:10]):
            fh = open(path, "rb")
            file_handles.append(fh)
            files[f"photo_{i}"] = (Path(path).name, fh, "image/png")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{self.base_url}/sendMediaGroup",
                    data={"chat_id": self.chat_id, "media": json.dumps(media)},
                    files=files,
                )
                resp.raise_for_status()
                return resp.json()
        finally:
            for fh in file_handles:
                fh.close()

    async def send_book_slides(
        self,
        image_paths: list[str],
        book_title: str,
        summary_zh: str,
        summary_en: str,
        topic: str,
    ) -> None:
        """发送绘本slides图片 + 双语社交媒体文案

        流程:
        1. 分批发送图片（每批最多10张）
        2. 发送中文社交媒体文案
        3. 发送英文社交媒体文案

        Args:
            image_paths: slides图片路径列表
            book_title: 绘本标题
            summary_zh: 中文内容摘要
            summary_en: 英文内容摘要
            topic: 绘本主题
        """
        # 1. 分批发送图片
        batch_size = 10
        total = len(image_paths)
        for start in range(0, total, batch_size):
            batch = image_paths[start : start + batch_size]
            batch_num = start // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size

            caption = ""
            if start == 0:
                caption = f"📚 <b>{book_title}</b>"

            if len(batch) == 1:
                await self.send_photo(batch[0], caption=caption)
            else:
                await self.send_media_group(batch, caption=caption)

            if total_batches > 1:
                print(f"  已发送第 {batch_num}/{total_batches} 批图片")
            await asyncio.sleep(1)

        # 2. 发送中文文案
        zh_post = self._format_zh_post(book_title, summary_zh, topic)
        await self.send_message(zh_post)
        await asyncio.sleep(0.5)

        # 3. 发送英文文案
        en_post = self._format_en_post(book_title, summary_en, topic)
        await self.send_message(en_post)

    def _format_zh_post(self, title: str, summary: str, topic: str) -> str:
        return (
            f"📖 <b>{title}</b>\n\n"
            f"{summary}\n\n"
            f"#儿童绘本 #{topic} #亲子阅读 #科普 #教育"
        )

    def _format_en_post(self, title: str, summary: str, topic: str) -> str:
        return (
            f"📖 <b>{title}</b>\n\n"
            f"{summary}\n\n"
            f"#PictureBook #{topic} #KidsEducation #STEM #ParentingTips"
        )

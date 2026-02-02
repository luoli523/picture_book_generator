#!/usr/bin/env python3
"""手动下载NotebookLM中的Slides

这是一个独立的备用工具，用于：
1. 列出所有 NotebookLM 笔记本
2. 手动下载已生成的 Slides
3. 当主流程失败时作为备用方案

使用方法：
    python3 download_slides.py list                    # 列出所有笔记本
    python3 download_slides.py <notebook_id>          # 下载指定笔记本的 Slides
    python3 download_slides.py                        # 交互式选择
"""

import asyncio
import sys
from pathlib import Path

from notebooklm import NotebookLMClient


async def list_notebooks():
    """列出所有笔记本"""
    async with await NotebookLMClient.from_storage() as client:
        notebooks = await client.notebooks.list()

        print("\n=== 你的 NotebookLM 笔记本 ===\n")
        for i, nb in enumerate(notebooks, 1):
            print(f"{i}. {nb.title}")
            print(f"   ID: {nb.id}")
            print(f"   URL: https://notebooklm.google.com/notebook/{nb.id}")

            # 列出该 notebook 中的 sources
            try:
                sources = await client.sources.list(nb.id)
                if sources:
                    print(f"   Sources ({len(sources)}):")
                    for src in sources[:3]:  # 只显示前3个
                        print(f"     - {src.title}")
                    if len(sources) > 3:
                        print(f"     ... 还有 {len(sources) - 3} 个")
            except Exception:
                pass

            print()

        return notebooks


async def download_slides(notebook_id: str, output_dir: str = "output"):
    """下载指定笔记本的Slides"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    async with await NotebookLMClient.from_storage() as client:
        # 检查是否有可下载的 slides
        try:
            output_file = output_path / f"{notebook_id}_slides.pdf"
            print(f"正在下载 Slides 到: {output_file}")
            
            await client.artifacts.download_slide_deck(notebook_id, str(output_file))
            print(f"✓ 下载成功: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"✗ 下载失败: {e}")
            print("\n可能的原因:")
            print("1. 该笔记本还没有生成 Slides")
            print("2. Notebook ID 不正确")
            print(f"3. 错误详情: {e}")
            return None


async def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  1. 列出所有笔记本:")
        print("     python download_slides.py list")
        print()
        print("  2. 下载指定笔记本的Slides:")
        print("     python download_slides.py <notebook_id>")
        print()
        
        # 自动列出笔记本
        notebooks = await list_notebooks()
        
        if notebooks:
            print("请输入要下载的笔记本编号或ID:")
            try:
                choice = input("> ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(notebooks):
                        notebook_id = notebooks[idx].id
                    else:
                        print("无效的编号")
                        return
                else:
                    notebook_id = choice
                
                await download_slides(notebook_id)
            except KeyboardInterrupt:
                print("\n已取消")
        
        return
    
    command = sys.argv[1]
    
    if command == "list":
        await list_notebooks()
    else:
        notebook_id = command
        await download_slides(notebook_id)


if __name__ == "__main__":
    asyncio.run(main())

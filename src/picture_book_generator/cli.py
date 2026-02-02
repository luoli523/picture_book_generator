"""命令行接口"""

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from .core.generator import PictureBookGenerator
from .core.models import BookConfig, Language
from .utils.config import get_settings

app = typer.Typer(
    name="picture-book",
    help="""儿童绘本自动生成工具 - 根据主题自动搜索知识并生成适合7-10岁儿童的绘本

快速开始:
  picture-book generate ocean                    # 生成英文绘本
  picture-book generate 恐龙 --lang zh           # 生成中文绘本
  picture-book generate dinosaur --nlm-slides   # 生成绘本 + NotebookLM Slides
  
更多示例:
  picture-book generate --help                   # 查看所有参数
  picture-book languages                         # 查看支持的语言
""",
)
console = Console()


@app.command()
def generate(
    topic: str = typer.Argument(..., help="绘本主题，如：恐龙、太空、海洋生物"),
    language: str = typer.Option(
        "en",
        "--lang",
        "-l",
        help="目标语言: en(英文), zh(中文), ja(日文), ko(韩文)",
    ),
    chapters: int = typer.Option(
        5,
        "--chapters",
        "-c",
        help="章节数量 (3-10)",
        min=3,
        max=10,
    ),
    min_age: int = typer.Option(7, "--min-age", help="最小目标年龄"),
    max_age: int = typer.Option(10, "--max-age", help="最大目标年龄"),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="输出文件路径 (默认: ./output/<topic>.md)",
    ),
    nlm_slides: bool = typer.Option(
        False,
        "--nlm-slides",
        help="生成NotebookLM Slides: 检查是否存在绘本文件，不存在则生成，然后上传到NotebookLM并生成Slides PDF",
    ),
    nlm_instructions: str = typer.Option(
        None,
        "--nlm-instructions",
        help="NotebookLM Slides 自定义指令 (如: '创建动画风格的儿童演示文稿')",
    ),
    nlm_format: str = typer.Option(
        None,
        "--nlm-format",
        help="Slides 格式: detailed(详细) 或 presenter(演讲者)",
    ),
    nlm_length: str = typer.Option(
        None,
        "--nlm-length",
        help="Slides 长度: short(短) 或 default(默认)",
    ),
):
    """根据主题生成儿童绘本

    示例:
        # 基础用法
        picture-book generate ocean
        
        # 中文绘本
        picture-book generate 恐龙 --lang zh
        
        # 自定义章节和年龄
        picture-book generate space --lang en --chapters 8 --min-age 8 --max-age 12
        
        # 生成绘本并创建 NotebookLM Slides
        picture-book generate dinosaur --nlm-slides
        
        # 完整参数示例（所有选项）
        picture-book generate ocean \\
            --lang en \\
            --chapters 6 \\
            --min-age 7 \\
            --max-age 10 \\
            --output ./my_books/ocean_adventure.md \\
            --nlm-slides \\
            --nlm-instructions "创建色彩鲜艳的卡通风格演示文稿，适合小学生课堂展示" \\
            --nlm-format detailed \\
            --nlm-length default
    """
    # 解析语言
    try:
        lang = Language(language)
    except ValueError:
        console.print(f"[red]不支持的语言: {language}[/red]")
        console.print("支持的语言: zh, en, ja, ko")
        raise typer.Exit(1)

    # 创建配置
    config = BookConfig(
        topic=topic,
        language=lang,
        age_range=(min_age, max_age),
        chapter_count=chapters,
    )

    console.print(
        Panel(
            f"[bold]主题:[/bold] {topic}\n"
            f"[bold]语言:[/bold] {lang.value}\n"
            f"[bold]目标年龄:[/bold] {min_age}-{max_age}岁\n"
            f"[bold]章节数:[/bold] {chapters}",
            title="绘本生成配置",
            border_style="blue",
        )
    )

    settings = get_settings()

    # 确定输出路径
    if output is None:
        output_dir = Path(settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{topic}.md"
    else:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # NotebookLM Slides 模式：检查文件是否存在，不存在则生成
    if nlm_slides:
        from .services.notebooklm import NotebookLMService

        # 检查绘本文件是否存在
        if output_path.exists():
            console.print(f"[cyan]找到已存在的绘本: {output_path}[/cyan]")
            markdown_content = output_path.read_text(encoding="utf-8")
            book_title = topic  # 从文件名提取标题
        else:
            # 文件不存在，生成绘本
            console.print(f"[cyan]绘本不存在，开始生成...[/cyan]")
            generator = PictureBookGenerator(settings)
            try:
                book = asyncio.run(generator.generate(config))
            except Exception as e:
                console.print(f"[red]生成失败: {e}[/red]")
                raise typer.Exit(1)

            # 保存绘本
            markdown_content = book.to_markdown()
            output_path.write_text(markdown_content, encoding="utf-8")
            console.print(f"[green]绘本已保存到: {output_path}[/green]")
            book_title = book.title

        # 上传到 NotebookLM 并生成 Slides
        notebooklm_service = NotebookLMService(settings)

        try:
            # 准备语言参数
            slides_language = "zh" if lang == Language.CHINESE else lang.value

            # 一键上传并生成 Slides
            slides_path = asyncio.run(
                notebooklm_service.upload_and_generate_slides(
                    markdown_content,
                    title=book_title,
                    download_dir=str(output_path.parent),
                    instructions=nlm_instructions,
                    language=slides_language,
                    slide_format=nlm_format,
                    slide_length=nlm_length,
                )
            )
            console.print(f"\n[green]✓ Slides已保存到: {slides_path}[/green]")

        except ImportError as e:
            console.print(f"\n[red]{e}[/red]")
        except Exception as e:
            console.print(f"\n[red]NotebookLM操作失败: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise typer.Exit(1)

    else:
        # 正常模式：生成绘本
        generator = PictureBookGenerator(settings)
        try:
            book = asyncio.run(generator.generate(config))
        except Exception as e:
            console.print(f"[red]生成失败: {e}[/red]")
            raise typer.Exit(1)

        # 保存输出
        output_path.write_text(book.to_markdown(), encoding="utf-8")
        console.print(f"\n[green]绘本已保存到: {output_path}[/green]")


@app.command()
def languages():
    """列出支持的语言"""
    console.print("\n[bold]支持的语言:[/bold]\n")
    for lang in Language:
        names = {
            "zh": "中文 (Chinese)",
            "en": "英文 (English)",
            "ja": "日文 (Japanese)",
            "ko": "韩文 (Korean)",
        }
        console.print(f"  {lang.value}: {names.get(lang.value, lang.value)}")
    console.print()


@app.command()
def version():
    """显示版本信息"""
    from . import __version__

    console.print(f"picture-book-generator v{__version__}")


@app.command()
def notebooklm_login():
    """登录NotebookLM (首次使用前需要执行)

    使用说明:
        1. pip install picture-book-generator[notebooklm]
        2. notebooklm login  # 在终端中运行此命令

    登录会打开浏览器完成Google授权。
    """
    from .services.notebooklm import NotebookLMService

    settings = get_settings()
    service = NotebookLMService(settings)

    try:
        asyncio.run(service.login())
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]操作失败: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def upload_to_notebooklm(
    file_path: str = typer.Argument(..., help="要上传的Markdown文件路径"),
):
    """上传绘本到NotebookLM

    示例:
        picture-book upload-to-notebooklm ./output/恐龙.md
    """
    from .services.notebooklm import NotebookLMService

    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]文件不存在: {file_path}[/red]")
        raise typer.Exit(1)

    content = path.read_text(encoding="utf-8")
    settings = get_settings()
    service = NotebookLMService(settings)

    try:
        console.print("正在上传到NotebookLM...")
        notebook_id, source_id, source_title = asyncio.run(
            service.upload(content, title=path.stem)
        )
        console.print(f"[green]上传成功![/green]")
        console.print(f"Notebook: 儿童绘本 (ID: {notebook_id})")
        console.print(f"Source: {source_title} (ID: {source_id})")
        console.print(f"访问: https://notebooklm.google.com/notebook/{notebook_id}")
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]上传失败: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def generate_slides(
    notebook_url: str = typer.Argument(..., help="NotebookLM笔记本URL或ID"),
    output_dir: str = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Slides下载目录 (默认: 当前目录)",
    ),
):
    """从NotebookLM笔记本生成Slides

    示例:
        picture-book generate-slides https://notebooklm.google.com/notebook/xxx
        picture-book generate-slides notebook-id-xxx -o ./slides
    """
    from .services.notebooklm import NotebookLMService

    settings = get_settings()
    service = NotebookLMService(settings)

    # 从URL中提取notebook_id（如果是URL的话）
    notebook_id = notebook_url
    if "notebooklm.google.com/notebook/" in notebook_url:
        notebook_id = notebook_url.split("/notebook/")[-1].split("?")[0]

    try:
        console.print("[blue]正在生成Slides...[/blue]")
        slides_path = asyncio.run(service.generate_slides(notebook_id, output_dir))
        console.print(f"[green]Slides已保存到: {slides_path}[/green]")
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]生成Slides失败: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

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
    help="儿童绘本自动生成工具 - 根据主题自动搜索知识并生成适合7-10岁儿童的绘本",
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
):
    """根据主题生成儿童绘本

    示例:
        picture-book generate 恐龙
        picture-book generate "太空探险" --lang en --chapters 8
        picture-book generate 海洋生物 -l zh -c 6 -o my_book.md
        picture-book generate 恐龙 --nlm-slides  # 生成绘本并创建NotebookLM Slides
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
        console.print("\n[blue]正在上传到NotebookLM...[/blue]")
        notebooklm_service = NotebookLMService(settings)

        try:
            notebook_url = asyncio.run(
                notebooklm_service.upload(markdown_content, title=book_title)
            )
            console.print(f"[green]已上传到NotebookLM: {notebook_url}[/green]")

            # 生成 Slides
            console.print("\n[blue]正在生成Slides...[/blue]")
            slides_path = asyncio.run(
                notebooklm_service.generate_slides(
                    notebook_url, download_dir=str(output_path.parent)
                )
            )
            console.print(f"[green]Slides已保存到: {slides_path}[/green]")

        except ImportError as e:
            console.print(f"[red]{e}[/red]")
            console.print("请先安装NotebookLM依赖:")
            console.print("  pip install picture-book-generator[notebooklm]")
            console.print("  playwright install chromium")
        except Exception as e:
            console.print(f"[red]NotebookLM操作失败: {e}[/red]")
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

    会打开浏览器让你登录Google账号，登录状态会被保存用于后续上传。

    使用前请确保已安装依赖:
        pip install picture-book-generator[notebooklm]
        playwright install chromium
    """
    from .services.notebooklm import NotebookLMService

    settings = get_settings()
    service = NotebookLMService(settings)

    try:
        asyncio.run(service.login())
        console.print("[green]登录成功![/green]")
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]登录失败: {e}[/red]")
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
        url = asyncio.run(service.upload(content, title=path.stem))
        console.print(f"[green]上传成功![/green]")
        console.print(f"笔记本链接: {url}")
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]上传失败: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def generate_slides(
    notebook_url: str = typer.Argument(..., help="NotebookLM笔记本URL"),
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
        picture-book generate-slides https://notebooklm.google.com/notebook/xxx -o ./slides
    """
    from .services.notebooklm import NotebookLMService

    settings = get_settings()
    service = NotebookLMService(settings)

    try:
        console.print("[blue]正在生成Slides...[/blue]")
        slides_path = asyncio.run(service.generate_slides(notebook_url, output_dir))
        console.print(f"[green]Slides已保存到: {slides_path}[/green]")
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]生成Slides失败: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

"""Gradio Web 应用 - 儿童绘本生成器"""

import asyncio
import os
from pathlib import Path
from datetime import datetime

import gradio as gr

from src.picture_book_generator.core.generator import PictureBookGenerator
from src.picture_book_generator.core.models import BookConfig, Language
from src.picture_book_generator.services.notebooklm import NotebookLMService
from src.picture_book_generator.utils.config import get_settings


def generate_picture_book(
    topic: str,
    language: str,
    chapters: int,
    min_age: int,
    max_age: int,
    generate_slides: bool,
    nlm_instructions: str | None,
    nlm_format: str,
    nlm_length: str,
    progress=gr.Progress(),
) -> tuple[str | None, str | None, str]:
    """生成儿童绘本
    
    Returns:
        (markdown_file_path, pdf_file_path, status_message)
    """
    try:
        # 验证输入
        if not topic or not topic.strip():
            return None, None, "❌ 请输入主题"
        
        progress(0.1, desc="初始化...")
        
        # 创建配置
        lang = Language(language)
        config = BookConfig(
            topic=topic.strip(),
            language=lang,
            age_range=(min_age, max_age),
            chapter_count=chapters,
        )
        
        settings = get_settings()
        
        # 确保输出目录存在
        output_dir = Path(settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
        markdown_filename = f"{safe_topic}_{timestamp}.md"
        markdown_path = output_dir / markdown_filename
        
        # 生成绘本
        progress(0.2, desc="搜索知识...")
        generator = PictureBookGenerator(settings)
        
        progress(0.4, desc="生成绘本内容...")
        book = asyncio.run(generator.generate(config))
        
        # 保存 Markdown
        progress(0.7, desc="保存绘本...")
        markdown_content = book.to_markdown()
        markdown_path.write_text(markdown_content, encoding="utf-8")
        
        pdf_path = None
        status_msg = f"✅ 绘本生成成功！\n\n📖 主题: {topic}\n📝 语言: {language}\n📚 章节: {chapters}"
        
        # 生成 NotebookLM Slides（可选）
        if generate_slides:
            try:
                progress(0.75, desc="上传到 NotebookLM...")
                notebooklm_service = NotebookLMService(settings)
                
                # 准备语言参数
                slides_language = "zh" if lang == Language.CHINESE else lang.value
                
                # 上传并生成 Slides
                progress(0.8, desc="生成 Slides（可能需要 2-5 分钟）...")
                slides_file = asyncio.run(
                    notebooklm_service.upload_and_generate_slides(
                        markdown_content,
                        title=markdown_filename,
                        download_dir=str(output_dir),
                        instructions=nlm_instructions if nlm_instructions else None,
                        language=slides_language,
                        slide_format=nlm_format if nlm_format != "默认" else None,
                        slide_length=nlm_length if nlm_length != "默认" else None,
                    )
                )
                
                pdf_path = slides_file
                status_msg += f"\n🎨 Slides: 已生成"
                
            except ImportError:
                status_msg += "\n\n⚠️ NotebookLM 功能未安装\n提示: 运行 'pip install -e \".[notebooklm]\"'"
            except Exception as e:
                status_msg += f"\n\n⚠️ Slides 生成失败: {str(e)}\n绘本已成功保存"
        
        progress(1.0, desc="完成！")
        return str(markdown_path), pdf_path, status_msg
        
    except Exception as e:
        import traceback
        error_msg = f"❌ 生成失败\n\n错误: {str(e)}\n\n{traceback.format_exc()}"
        return None, None, error_msg


# 创建 Gradio 界面
with gr.Blocks(
    title="儿童绘本生成器",
    theme=gr.themes.Soft(),
    css="""
        .gradio-container {max-width: 900px !important}
        .output-markdown {font-family: monospace; font-size: 14px;}
    """
) as demo:
    gr.Markdown(
        """
        # 📚 儿童绘本自动生成器
        
        根据主题自动搜索知识并生成适合 7-10 岁儿童阅读的绘本，支持生成 NotebookLM Slides。
        
        ⚡ **快速开始**: 输入主题（如 "ocean"、"恐龙"）→ 点击生成 → 下载绘本和 Slides
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            # 基础参数
            gr.Markdown("## 📝 基础设置")
            topic = gr.Textbox(
                label="主题",
                placeholder="例如: ocean, 恐龙, 太空, 海洋生物...",
                info="绘本的主题内容",
            )
            
            with gr.Row():
                language = gr.Dropdown(
                    choices=["en", "zh", "ja", "ko"],
                    value="en",
                    label="语言",
                    info="绘本语言",
                )
                chapters = gr.Slider(
                    minimum=3,
                    maximum=10,
                    value=5,
                    step=1,
                    label="章节数",
                    info="绘本章节数量",
                )
            
            with gr.Row():
                min_age = gr.Slider(
                    minimum=3,
                    maximum=12,
                    value=7,
                    step=1,
                    label="最小年龄",
                )
                max_age = gr.Slider(
                    minimum=5,
                    maximum=15,
                    value=10,
                    step=1,
                    label="最大年龄",
                )
            
            # NotebookLM Slides 设置
            gr.Markdown("## 🎨 NotebookLM Slides 设置")
            generate_slides = gr.Checkbox(
                label="生成 Slides PDF",
                value=True,
                info="自动生成演示文稿（需要 2-5 分钟）",
            )
            
            with gr.Column(visible=True) as slides_options:
                nlm_instructions = gr.Textbox(
                    label="自定义指令（可选）",
                    placeholder="例如: 创建色彩鲜艳的卡通风格演示文稿...",
                    lines=2,
                    info="留空使用默认指令",
                )
                
                with gr.Row():
                    nlm_format = gr.Radio(
                        choices=["默认", "detailed", "presenter"],
                        value="默认",
                        label="格式",
                        info="detailed=详细版, presenter=演讲版",
                    )
                    nlm_length = gr.Radio(
                        choices=["默认", "default", "short"],
                        value="默认",
                        label="长度",
                        info="default=标准, short=简短",
                    )
            
            # 切换 Slides 选项可见性
            generate_slides.change(
                fn=lambda x: gr.update(visible=x),
                inputs=[generate_slides],
                outputs=[slides_options],
            )
            
            # 生成按钮
            generate_btn = gr.Button(
                "🚀 开始生成",
                variant="primary",
                size="lg",
            )
        
        with gr.Column(scale=1):
            # 输出结果
            gr.Markdown("## 📥 下载")
            status_output = gr.Textbox(
                label="状态",
                lines=8,
                interactive=False,
                show_copy_button=True,
            )
            
            markdown_output = gr.File(
                label="📖 绘本 Markdown",
                file_types=[".md"],
            )
            
            pdf_output = gr.File(
                label="🎨 Slides PDF",
                file_types=[".pdf"],
            )
    
    # 绑定生成函数
    generate_btn.click(
        fn=generate_picture_book,
        inputs=[
            topic,
            language,
            chapters,
            min_age,
            max_age,
            generate_slides,
            nlm_instructions,
            nlm_format,
            nlm_length,
        ],
        outputs=[markdown_output, pdf_output, status_output],
    )
    
    # 示例
    gr.Markdown("## 💡 示例")
    gr.Examples(
        examples=[
            ["ocean", "en", 5, 7, 10, True, "", "默认", "默认"],
            ["恐龙", "zh", 6, 7, 10, True, "创建适合儿童的卡通风格", "detailed", "默认"],
            ["space exploration", "en", 8, 8, 12, False, "", "默认", "默认"],
        ],
        inputs=[
            topic,
            language,
            chapters,
            min_age,
            max_age,
            generate_slides,
            nlm_instructions,
            nlm_format,
            nlm_length,
        ],
    )
    
    # 页脚
    gr.Markdown(
        """
        ---
        
        ### ⚙️ 使用说明
        
        1. **首次使用**: 需要先登录 NotebookLM（在终端运行 `notebooklm login`）
        2. **配置 API**: 需要在 `.env` 文件中配置 LLM API Key
        3. **生成时间**: 绘本约 1-2 分钟，Slides 额外需要 2-5 分钟
        4. **失败处理**: Slides 失败不影响绘本生成
        
        💡 **提示**: 建议使用具体的主题（如 "ocean"）而非抽象概念
        
        📖 [查看项目文档](https://github.com/luoli523/picture_book_generator) | 
        🐛 [报告问题](https://github.com/luoli523/picture_book_generator/issues)
        """
    )


if __name__ == "__main__":
    # 检查环境配置
    try:
        settings = get_settings()
        print("✅ 配置加载成功")
    except Exception as e:
        print(f"⚠️  警告: 配置加载失败 - {e}")
        print("请确保 .env 文件已正确配置")
    
    # 启动应用
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # 设置为 True 可生成公开分享链接
        show_error=True,
    )

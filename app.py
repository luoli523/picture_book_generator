"""Gradio Web 应用 - 儿童绘本生成器（Ocean Pop 版本）"""

import asyncio
from datetime import datetime
from pathlib import Path

import gradio as gr

from src.picture_book_generator.core.generator import PictureBookGenerator
from src.picture_book_generator.core.models import BookConfig, Language
from src.picture_book_generator.services.notebooklm import NotebookLMService
from src.picture_book_generator.utils.config import get_settings

AGE_GROUP_RANGES = {
    "3-5 岁": (3, 5),
    "6-8 岁": (6, 8),
    "9-12 岁": (9, 12),
}

SOURCE_MODE_MAP = {
    "主题生成": "topic",
    "家长故事改写": "parent_story",
    "主题 + 家长故事": "hybrid",
}

STYLE_THEME_MAP = {
    "Ocean Pop（海洋活力）": "ocean_pop",
    "Sunny Story（暖阳纸本）": "sunny_story",
    "Forest Sketch（森林手绘）": "forest_sketch",
    "Space Quest（太空冒险）": "space_quest",
}

TONE_MAP = {
    "冒险探索": "exploratory",
    "温柔陪伴": "gentle",
    "幽默搞笑": "playful",
    "科普严谨": "informative",
}

GOAL_MAP = {
    "科学知识": "science",
    "行为习惯": "habits",
    "情绪认知": "emotion",
    "睡前安抚": "bedtime",
}

GENDER_MAP = {
    "不限定": "unspecified",
    "女孩": "girl",
    "男孩": "boy",
}

READING_LEVEL_MAP = {
    "启蒙": "beginner",
    "基础": "basic",
    "进阶": "advanced",
}

CHAPTER_LENGTH_MAP = {
    "短（更快读完）": "short",
    "中（推荐）": "medium",
    "长（更丰富）": "long",
}

STYLE_SLIDE_INSTRUCTIONS = {
    "ocean_pop": "使用 Ocean Pop 风格：明快海洋配色、卡通插图、适合亲子共读",
    "sunny_story": "使用暖阳纸本风格：温暖柔和、睡前阅读友好、画面有手账感",
    "forest_sketch": "使用森林手绘风格：自然配色、安静舒缓、强调观察与想象",
    "space_quest": "使用太空冒险风格：高对比色彩、探索感强、激发科学兴趣",
}

OCEAN_POP_CSS = """
:root {
  --ocean-navy: #0e3558;
  --ocean-cyan: #00a9c8;
  --ocean-aqua: #a8ecf4;
  --ocean-coral: #ff7f5a;
  --ocean-foam: #f3fbff;
  --ocean-card: #ffffff;
  --ocean-ink: #16324a;
}

.gradio-container {
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  background:
    radial-gradient(circle at 8% 0%, rgba(168, 236, 244, 0.45) 0%, rgba(168, 236, 244, 0) 36%),
    radial-gradient(circle at 92% 6%, rgba(0, 169, 200, 0.2) 0%, rgba(0, 169, 200, 0) 34%),
    linear-gradient(180deg, #f5fdff 0%, #ecf8ff 55%, #f7fcff 100%);
}

.app-hero {
  border-radius: 28px;
  padding: 28px 30px;
  margin-bottom: 18px;
  color: white;
  background:
    linear-gradient(130deg, rgba(10, 62, 102, 0.97), rgba(0, 126, 165, 0.92)),
    radial-gradient(circle at 80% 30%, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0) 55%);
  box-shadow: 0 18px 48px rgba(9, 63, 100, 0.28);
}

.app-hero h1 {
  margin: 0;
  font-size: 34px;
  letter-spacing: 0.2px;
}

.app-hero p {
  margin: 10px 0 0;
  opacity: 0.95;
  line-height: 1.65;
}

.main-shell {
  gap: 16px;
}

.step-card,
.result-card {
  background: var(--ocean-card);
  border-radius: 22px;
  padding: 16px;
  border: 1px solid rgba(13, 72, 109, 0.08);
  box-shadow: 0 10px 30px rgba(6, 64, 104, 0.08);
  margin-bottom: 12px;
}

.step-title {
  color: var(--ocean-navy);
  font-weight: 700;
  margin: 2px 0 10px;
}

#generate-btn {
  background: linear-gradient(130deg, var(--ocean-coral), #ff9867) !important;
  border: none !important;
  color: white !important;
  font-weight: 700 !important;
  border-radius: 14px !important;
  min-height: 46px !important;
  box-shadow: 0 8px 20px rgba(255, 127, 90, 0.35);
}

#generate-btn:hover {
  filter: brightness(1.04);
  transform: translateY(-1px);
}

.ocean-tip {
  background: rgba(168, 236, 244, 0.35);
  border: 1px solid rgba(0, 130, 163, 0.25);
  color: var(--ocean-ink);
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 14px;
}

@media (max-width: 768px) {
  .app-hero h1 {
    font-size: 28px;
  }

  .app-hero {
    padding: 22px;
    border-radius: 22px;
  }
}
"""


def _sync_age_range(age_group: str) -> tuple[gr.update, gr.update]:
    """根据年龄段快捷填充最小/最大年龄"""
    min_age, max_age = AGE_GROUP_RANGES.get(age_group, (7, 10))
    return gr.update(value=min_age), gr.update(value=max_age)


def _resolve_topic(topic: str, parent_story: str) -> str:
    """在仅提供家长故事时自动推断主题名"""
    clean_topic = (topic or "").strip()
    if clean_topic:
        return clean_topic

    seed = "".join(c for c in (parent_story or "")[:24] if c.isalnum() or c in (" ", "-", "_"))
    seed = seed.strip().replace(" ", "_")
    return seed or "family_story"


def generate_picture_book(
    age_group: str,
    child_gender_label: str,
    reading_level_label: str,
    interests: list[str],
    source_mode_label: str,
    topic: str,
    parent_story: str,
    style_theme_label: str,
    narration_tone_label: str,
    education_goal_label: str,
    language: str,
    chapters: int,
    chapter_length_label: str,
    min_age: int,
    max_age: int,
    generate_slides: bool,
    nlm_instructions: str | None,
    nlm_format: str,
    nlm_length: str,
    progress=gr.Progress(),
) -> tuple[str | None, str | None, str]:
    """生成儿童绘本并可选导出 NotebookLM Slides"""
    try:
        source_mode = SOURCE_MODE_MAP.get(source_mode_label, "topic")
        parent_story = (parent_story or "").strip()
        topic = (topic or "").strip()

        if source_mode in ("topic", "hybrid") and not topic:
            return None, None, "❌ 请选择“主题生成”时必须输入主题"

        if source_mode in ("parent_story", "hybrid") and not parent_story:
            return None, None, "❌ 请选择“家长故事改写/混合模式”时请提供故事草稿"

        progress(0.08, desc="初始化参数...")

        target_topic = _resolve_topic(topic, parent_story)
        lang = Language(language)

        if min_age > max_age:
            return None, None, "❌ 年龄范围无效：最小年龄不能大于最大年龄"

        config = BookConfig(
            topic=target_topic,
            language=lang,
            age_range=(min_age, max_age),
            chapter_count=chapters,
            child_gender=GENDER_MAP.get(child_gender_label, "unspecified"),
            reading_level=READING_LEVEL_MAP.get(reading_level_label, "basic"),
            interests=interests or [],
            source_mode=source_mode,
            parent_story=parent_story,
            style_theme=STYLE_THEME_MAP.get(style_theme_label, "ocean_pop"),
            narration_tone=TONE_MAP.get(narration_tone_label, "exploratory"),
            education_goal=GOAL_MAP.get(education_goal_label, "science"),
            chapter_length=CHAPTER_LENGTH_MAP.get(chapter_length_label, "medium"),
        )

        settings = get_settings()
        output_dir = Path(settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in target_topic if c.isalnum() or c in (" ", "-", "_"))
        safe_topic = safe_topic.strip().replace(" ", "_") or "picture_book"
        markdown_filename = f"{safe_topic}_{timestamp}.md"
        markdown_path = output_dir / markdown_filename

        progress(0.2, desc="检索与整理知识...")
        generator = PictureBookGenerator(settings)

        progress(0.42, desc="生成绘本结构与章节...")
        book = asyncio.run(generator.generate(config))

        progress(0.68, desc="保存绘本文件...")
        markdown_content = book.to_markdown()
        markdown_path.write_text(markdown_content, encoding="utf-8")

        pdf_path = None
        status_msg = (
            "✅ 绘本生成成功！\n\n"
            f"📖 主题: {target_topic}\n"
            f"👧 孩子年龄段: {age_group} ({min_age}-{max_age}岁)\n"
            f"🎯 教育目标: {education_goal_label}\n"
            f"🎨 风格: {style_theme_label}\n"
            f"📝 语言: {language}\n"
            f"📚 章节: {chapters}\n"
            f"📂 来源模式: {source_mode_label}"
        )

        if generate_slides:
            try:
                progress(0.76, desc="上传到 NotebookLM...")
                notebooklm_service = NotebookLMService(settings)
                slides_language = "zh" if lang == Language.CHINESE else lang.value

                style_theme_id = STYLE_THEME_MAP.get(style_theme_label, "ocean_pop")
                final_instructions = (nlm_instructions or "").strip() or STYLE_SLIDE_INSTRUCTIONS.get(
                    style_theme_id
                )

                progress(0.82, desc="生成 Slides（约 2-5 分钟）...")
                slides_file = asyncio.run(
                    notebooklm_service.upload_and_generate_slides(
                        markdown_content,
                        title=markdown_filename,
                        download_dir=str(output_dir),
                        instructions=final_instructions,
                        language=slides_language,
                        slide_format=None if nlm_format == "auto" else nlm_format,
                        slide_length=None if nlm_length == "auto" else nlm_length,
                    )
                )
                pdf_path = slides_file
                status_msg += "\n🎬 Slides: 已生成"
            except ImportError:
                status_msg += "\n\n⚠️ NotebookLM 功能未安装\n提示: 运行 'pip install -e \".[notebooklm]\"'"
            except Exception as e:
                status_msg += f"\n\n⚠️ Slides 生成失败: {e}\n绘本已成功保存"

        progress(1.0, desc="完成")
        return str(markdown_path), pdf_path, status_msg

    except Exception as e:
        import traceback

        error_msg = f"❌ 生成失败\n\n错误: {e}\n\n{traceback.format_exc()}"
        return None, None, error_msg


with gr.Blocks(title="Picture Book Generator", css=OCEAN_POP_CSS) as demo:
    gr.HTML(
        """
        <section class="app-hero">
          <h1>Picture Book Studio · Ocean Pop</h1>
          <p>为你家孩子定制专属绘本：按年龄、性别、主题或家长故事草稿，快速生成可阅读、可下载、可分享的儿童绘本与 Slides。</p>
        </section>
        """
    )

    with gr.Row(elem_classes=["main-shell"]):
        with gr.Column(scale=3):
            with gr.Group(elem_classes=["step-card"]):
                gr.Markdown("<div class='step-title'>1) 孩子画像</div>")
                with gr.Row():
                    age_group = gr.Dropdown(
                        choices=list(AGE_GROUP_RANGES.keys()),
                        value="6-8 岁",
                        label="年龄段",
                    )
                    child_gender = gr.Radio(
                        choices=list(GENDER_MAP.keys()),
                        value="不限定",
                        label="性别",
                    )
                    reading_level = gr.Radio(
                        choices=list(READING_LEVEL_MAP.keys()),
                        value="基础",
                        label="阅读能力",
                    )

                interests = gr.CheckboxGroup(
                    choices=[
                        "恐龙",
                        "太空",
                        "海洋",
                        "昆虫",
                        "植物",
                        "公主",
                        "工程车",
                        "情绪管理",
                        "行为习惯",
                    ],
                    label="兴趣标签（可多选）",
                    value=["海洋"],
                )

            with gr.Group(elem_classes=["step-card"]):
                gr.Markdown("<div class='step-title'>2) 故事来源</div>")
                source_mode = gr.Radio(
                    choices=list(SOURCE_MODE_MAP.keys()),
                    value="主题生成",
                    label="来源模式",
                )
                topic = gr.Textbox(
                    label="主题",
                    placeholder="例如：海洋探险、恐龙世界、月球旅行...",
                )
                parent_story = gr.Textbox(
                    label="家长故事草稿（可选）",
                    placeholder="你可以写孩子最近的经历、想讲的故事片段，系统会改写成绘本结构",
                    lines=5,
                )

            with gr.Group(elem_classes=["step-card"]):
                gr.Markdown("<div class='step-title'>3) 风格与目标</div>")
                style_theme = gr.Radio(
                    choices=list(STYLE_THEME_MAP.keys()),
                    value="Ocean Pop（海洋活力）",
                    label="绘本风格",
                )
                with gr.Row():
                    narration_tone = gr.Dropdown(
                        choices=list(TONE_MAP.keys()),
                        value="冒险探索",
                        label="叙事语气",
                    )
                    education_goal = gr.Dropdown(
                        choices=list(GOAL_MAP.keys()),
                        value="科学知识",
                        label="教育目标",
                    )

            with gr.Group(elem_classes=["step-card"]):
                gr.Markdown("<div class='step-title'>4) 生成参数</div>")
                with gr.Row():
                    language = gr.Dropdown(
                        choices=["zh", "en", "ja", "ko"],
                        value="zh",
                        label="输出语言",
                    )
                    chapters = gr.Slider(minimum=3, maximum=10, value=6, step=1, label="章节数")
                    chapter_length = gr.Radio(
                        choices=list(CHAPTER_LENGTH_MAP.keys()),
                        value="中（推荐）",
                        label="章节长度",
                    )

                with gr.Row():
                    min_age = gr.Slider(minimum=3, maximum=12, value=6, step=1, label="最小年龄")
                    max_age = gr.Slider(minimum=5, maximum=15, value=8, step=1, label="最大年龄")

                generate_slides = gr.Checkbox(
                    label="默认生成 NotebookLM Slides（推荐）",
                    value=True,
                    info="已按你的要求设为默认开启",
                )

                with gr.Column(visible=True) as slides_options:
                    nlm_instructions = gr.Textbox(
                        label="Slides 自定义指令（可选）",
                        placeholder="留空将自动使用 Ocean Pop 风格指令",
                        lines=2,
                    )
                    with gr.Row():
                        nlm_format = gr.Radio(
                            choices=["auto", "detailed", "presenter"],
                            value="auto",
                            label="Slides 格式",
                        )
                        nlm_length = gr.Radio(
                            choices=["auto", "default", "short"],
                            value="auto",
                            label="Slides 长度",
                        )

                gr.HTML(
                    "<div class='ocean-tip'>建议先用 6 章 + 中等长度，预览效果后再加长内容。</div>"
                )

            generate_btn = gr.Button("生成专属绘本", elem_id="generate-btn")

        with gr.Column(scale=2):
            with gr.Group(elem_classes=["result-card"]):
                gr.Markdown("### 生成结果")
                status_output = gr.Textbox(label="状态", lines=12, interactive=False)
                markdown_output = gr.File(label="绘本 Markdown", file_types=[".md"])
                pdf_output = gr.File(label="Slides PDF", file_types=[".pdf"])

            with gr.Group(elem_classes=["result-card"]):
                gr.Markdown(
                    """
                    ### 使用提示
                    1. 首次使用 Slides：终端执行 `notebooklm login`
                    2. 家长故事改写建议输入 150-600 字
                    3. 若生成失败，参数会保留，调整后可直接重试
                    """
                )

    age_group.change(fn=_sync_age_range, inputs=[age_group], outputs=[min_age, max_age])

    generate_slides.change(
        fn=lambda x: gr.update(visible=x),
        inputs=[generate_slides],
        outputs=[slides_options],
    )

    all_inputs = [
        age_group,
        child_gender,
        reading_level,
        interests,
        source_mode,
        topic,
        parent_story,
        style_theme,
        narration_tone,
        education_goal,
        language,
        chapters,
        chapter_length,
        min_age,
        max_age,
        generate_slides,
        nlm_instructions,
        nlm_format,
        nlm_length,
    ]

    generate_btn.click(
        fn=generate_picture_book,
        inputs=all_inputs,
        outputs=[markdown_output, pdf_output, status_output],
    )

    gr.Examples(
        label="快速模板",
        examples=[
            [
                "6-8 岁",
                "不限定",
                "基础",
                ["海洋", "植物"],
                "主题生成",
                "珊瑚礁探险",
                "",
                "Ocean Pop（海洋活力）",
                "冒险探索",
                "科学知识",
                "zh",
                6,
                "中（推荐）",
                6,
                8,
                True,
                "",
                "auto",
                "auto",
            ],
            [
                "3-5 岁",
                "女孩",
                "启蒙",
                ["情绪管理"],
                "家长故事改写",
                "",
                "孩子今天第一次去幼儿园，刚开始有点紧张，后来在老师帮助下和新朋友一起画画，回家后很自豪。",
                "Sunny Story（暖阳纸本）",
                "温柔陪伴",
                "情绪认知",
                "zh",
                5,
                "短（更快读完）",
                3,
                5,
                True,
                "",
                "auto",
                "short",
            ],
        ],
        inputs=all_inputs,
    )


if __name__ == "__main__":
    try:
        settings = get_settings()
        print("✅ 配置加载成功")
    except Exception as e:
        print(f"⚠️  警告: 配置加载失败 - {e}")
        print("请确保 .env 文件已正确配置")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )

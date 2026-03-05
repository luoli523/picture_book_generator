"""API 请求/响应模型"""

from enum import Enum

from pydantic import BaseModel, Field, model_validator

# === 枚举 ===


class Language(str, Enum):
    ZH = "zh"
    EN = "en"


class Gender(str, Enum):
    BOY = "boy"
    GIRL = "girl"
    UNSPECIFIED = "unspecified"


class ContentMode(str, Enum):
    """内容来源模式"""

    TOPIC = "topic"  # 热门主题 / 自由输入主题
    STORY = "story"  # 用户提供故事原文


class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    GROK = "grok"


# --- NotebookLM 产品类型 ---


class ProductType(str, Enum):
    SLIDES = "slides"
    VIDEO = "video"
    AUDIO = "audio"
    INFOGRAPHIC = "infographic"
    QUIZ = "quiz"
    FLASHCARDS = "flashcards"
    MIND_MAP = "mind_map"


# --- 产品选项枚举 ---


class SlidesFormat(str, Enum):
    DETAILED = "detailed"
    PRESENTER = "presenter"


class SlidesLength(str, Enum):
    DEFAULT = "default"
    SHORT = "short"


class VideoStyle(str, Enum):
    AUTO = "auto"
    CLASSIC = "classic"
    WHITEBOARD = "whiteboard"
    KAWAII = "kawaii"
    ANIME = "anime"
    WATERCOLOR = "watercolor"
    RETRO_PRINT = "retro_print"
    HERITAGE = "heritage"
    PAPER_CRAFT = "paper_craft"


class VideoFormat(str, Enum):
    EXPLAINER = "explainer"
    BRIEF = "brief"


class AudioFormat(str, Enum):
    DEEP_DIVE = "deep_dive"
    BRIEF = "brief"
    CRITIQUE = "critique"
    DEBATE = "debate"


class AudioLength(str, Enum):
    SHORT = "short"
    DEFAULT = "default"
    LONG = "long"


class InfographicOrientation(str, Enum):
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"


class InfographicDetail(str, Enum):
    CONCISE = "concise"
    STANDARD = "standard"
    DETAILED = "detailed"


class QuizDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizQuantity(str, Enum):
    FEWER = "fewer"
    STANDARD = "standard"


# === 请求模型 ===


class GenerateRequest(BaseModel):
    """绘本生成请求"""

    # 孩子信息
    child_name: str = Field(default="", description="孩子昵称（可选，可融入故事）")
    child_gender: Gender = Field(default=Gender.UNSPECIFIED)
    age_min: int = Field(default=7, ge=3, le=12)
    age_max: int = Field(default=10, ge=3, le=12)
    language: Language = Field(default=Language.EN)

    # 内容
    content_mode: ContentMode = Field(default=ContentMode.TOPIC)
    topic: str = Field(default="", description="主题（content_mode=topic 时使用）")
    story_text: str = Field(default="", description="用户故事原文（content_mode=story 时使用）")
    chapters: int = Field(default=5, ge=3, le=10)

    # 高级
    llm_provider: LLMProvider | None = Field(
        default=None, description="LLM 提供商，None 使用系统默认"
    )
    custom_instructions: str = Field(
        default="", description="传给 NotebookLM 的自定义指令"
    )

    # 要生成的产品列表
    products: list[ProductType] = Field(
        default=[ProductType.SLIDES], description="要生成的 NotebookLM 产品"
    )

    @model_validator(mode="after")
    def validate_content(self):
        if self.age_min > self.age_max:
            raise ValueError("age_min must be <= age_max")
        if self.content_mode == ContentMode.TOPIC and not self.topic.strip():
            raise ValueError("topic is required when content_mode is 'topic'")
        if self.content_mode == ContentMode.STORY and not self.story_text.strip():
            raise ValueError("story_text is required when content_mode is 'story'")
        return self


class SlidesOptions(BaseModel):
    slide_format: SlidesFormat = SlidesFormat.DETAILED
    slide_length: SlidesLength = SlidesLength.DEFAULT


class VideoOptions(BaseModel):
    video_style: VideoStyle = VideoStyle.KAWAII
    video_format: VideoFormat = VideoFormat.EXPLAINER


class AudioOptions(BaseModel):
    audio_format: AudioFormat = AudioFormat.DEEP_DIVE
    audio_length: AudioLength = AudioLength.DEFAULT


class InfographicOptions(BaseModel):
    orientation: InfographicOrientation = InfographicOrientation.LANDSCAPE
    detail_level: InfographicDetail = InfographicDetail.STANDARD


class QuizOptions(BaseModel):
    difficulty: QuizDifficulty = QuizDifficulty.EASY
    quantity: QuizQuantity = QuizQuantity.STANDARD


class ProductOptions(BaseModel):
    """各产品类型的可选参数，按需填写对应字段"""

    slides: SlidesOptions = Field(default_factory=SlidesOptions)
    video: VideoOptions = Field(default_factory=VideoOptions)
    audio: AudioOptions = Field(default_factory=AudioOptions)
    infographic: InfographicOptions = Field(default_factory=InfographicOptions)
    quiz: QuizOptions = Field(default_factory=QuizOptions)


class GenerateFullRequest(BaseModel):
    """完整生成请求 = 绘本配置 + 产品选项"""

    book: GenerateRequest
    product_options: ProductOptions = Field(default_factory=ProductOptions)


# === 响应模型 ===


class GenerateResponse(BaseModel):
    """生成任务创建响应"""

    job_id: str
    status: str = "started"


class BookResult(BaseModel):
    """绘本生成结果"""

    title: str
    topic: str
    language: str
    markdown_path: str
    markdown_content: str


class ProductResult(BaseModel):
    """单个产品生成结果"""

    product_type: ProductType
    status: str  # "pending" | "generating" | "completed" | "failed"
    file_path: str | None = None
    error: str | None = None


class JobStatus(BaseModel):
    """任务状态查询响应"""

    job_id: str
    status: str  # "generating_book" | "generating_products" | "completed" | "failed"
    book: BookResult | None = None
    products: list[ProductResult] = Field(default_factory=list)
    error: str | None = None

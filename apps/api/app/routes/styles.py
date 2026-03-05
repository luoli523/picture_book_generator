"""Style preset API routes."""

from fastapi import APIRouter

from ..schemas import StylePresetResponse

router = APIRouter(prefix="/api/v1/styles", tags=["styles"])

STYLE_PRESETS = [
    StylePresetResponse(
        id="ocean_pop",
        name="Ocean Pop",
        tagline="明快海洋配色，科学探索感",
        default_instructions="使用 Ocean Pop 风格：明快海洋配色、卡通插图、适合亲子共读",
    ),
    StylePresetResponse(
        id="sunny_story",
        name="Sunny Story",
        tagline="温暖柔和，适合睡前共读",
        default_instructions="使用暖阳纸本风格：温暖柔和、睡前阅读友好、画面有手账感",
    ),
    StylePresetResponse(
        id="forest_sketch",
        name="Forest Sketch",
        tagline="自然手绘，安静舒缓",
        default_instructions="使用森林手绘风格：自然配色、安静舒缓、强调观察与想象",
    ),
    StylePresetResponse(
        id="space_quest",
        name="Space Quest",
        tagline="太空冒险，激发想象力",
        default_instructions="使用太空冒险风格：高对比色彩、探索感强、激发科学兴趣",
    ),
]


@router.get("", response_model=list[StylePresetResponse])
async def list_styles() -> list[StylePresetResponse]:
    return STYLE_PRESETS


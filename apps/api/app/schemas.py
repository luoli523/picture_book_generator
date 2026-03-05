"""Pydantic schemas for Web API contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AgeGroup = Literal["3-5", "6-8", "9-12"]
Gender = Literal["unspecified", "girl", "boy"]
ReadingLevel = Literal["beginner", "basic", "advanced"]
SourceMode = Literal["topic", "parent_story", "hybrid"]
ThemeId = Literal["ocean_pop", "sunny_story", "forest_sketch", "space_quest"]
Tone = Literal["exploratory", "gentle", "playful", "informative"]
EducationGoal = Literal["science", "habits", "emotion", "bedtime"]
LanguageCode = Literal["zh", "en", "ja", "ko"]
ChapterLength = Literal["short", "medium", "long"]
TaskStatus = Literal["queued", "running", "succeeded", "failed"]
TaskStage = Literal[
    "prepare_context",
    "search_knowledge",
    "adapt_content",
    "generate_structure",
    "generate_chapters",
    "export_markdown",
    "generate_slides",
    "finalize",
    "completed",
    "failed",
]


class ChildProfile(BaseModel):
    age_group: AgeGroup = "6-8"
    gender: Gender = "unspecified"
    reading_level: ReadingLevel = "basic"
    interests: list[str] = Field(default_factory=list)


class ContentSource(BaseModel):
    mode: SourceMode = "topic"
    topic: str = ""
    parent_story: str = ""


class StyleConfig(BaseModel):
    theme_id: ThemeId = "ocean_pop"
    tone: Tone = "exploratory"
    education_goal: EducationGoal = "science"


class GenerationConfig(BaseModel):
    language: LanguageCode = "zh"
    chapters: int = Field(default=6, ge=3, le=10)
    chapter_length: ChapterLength = "medium"
    include_illustrations: bool = True
    generate_slides: bool = True


class CreateBookRequest(BaseModel):
    child_profile: ChildProfile
    content_source: ContentSource
    style: StyleConfig
    book_config: GenerationConfig


class CreateBookResponse(BaseModel):
    task_id: str
    book_id: str
    status: TaskStatus


class TaskResponse(BaseModel):
    task_id: str
    book_id: str
    status: TaskStatus
    stage: TaskStage
    progress: int = Field(ge=0, le=100)
    message: str
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class BookResponse(BaseModel):
    book_id: str
    title: str
    topic: str
    language: LanguageCode
    age_group: AgeGroup
    style_theme: ThemeId
    markdown_path: str | None = None
    slides_pdf_path: str | None = None
    slides_error: str | None = None
    created_at: datetime


class StylePresetResponse(BaseModel):
    id: ThemeId
    name: str
    tagline: str
    default_instructions: str


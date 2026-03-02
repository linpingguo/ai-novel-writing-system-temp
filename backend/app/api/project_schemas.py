from pydantic import BaseModel, Field
from typing import Optional, List


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    genre: str = Field(..., regex="^(玄幻|都市|言情|悬疑)$")
    target_word_count: int = Field(80000, gt=0)


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    genre: Optional[str] = Field(None, regex="^(玄幻|都市|言情|悬疑)$")
    target_word_count: Optional[int] = Field(None, gt=0)


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    genre: str
    target_word_count: int
    current_word_count: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ChapterExport(BaseModel):
    title: str
    content: str
    order: int


class ExportResponse(BaseModel):
    filename: str
    chapters: List[ChapterExport]
    total_word_count: int

from pydantic import BaseModel, Field
from typing import Optional, List


class ChapterCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    outline_node_id: Optional[str] = None
    content_format: str = Field("markdown", regex="^(markdown|rich_text)$")


class ChapterUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None)
    status: Optional[str] = Field(None, regex="^(draft|completed|published)$")


class AIGenerateRequest(BaseModel):
    style_hints: Optional[List[str]] = None
    reduce_ai_flavor: bool = True
    versions: int = Field(3, ge=1, le=5)


class AIPolishRequest(BaseModel):
    suggestions: Optional[List[str]] = None


class DialogueGenerateRequest(BaseModel):
    characters: List[str]
    scene: str
    context: str


class DialogueTurn(BaseModel):
    character_id: str
    content: str


class ChapterResponse(BaseModel):
    id: str
    project_id: str
    outline_node_id: Optional[str]
    title: str
    content: str
    content_format: str
    word_count: int
    status: str
    ai_generated_ratio: float
    style_score: Optional[float] = None
    ai_flavor_score: Optional[float] = None
    created_at: str
    updated_at: str


class AutosaveResponse(BaseModel):
    message: str
    saved_at: str


class AIVersion(BaseModel):
    version: int
    content: str


class AIPolishSuggestion(BaseModel):
    original_text: str
    suggested_text: str
    change_type: str
    reason: str

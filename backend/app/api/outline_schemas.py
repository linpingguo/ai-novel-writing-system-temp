from pydantic import BaseModel, Field
from typing import Optional, List


class OutlineNodeCreate(BaseModel):
    parent_id: Optional[str] = None
    node_type: str = Field(..., regex="^(volume|chapter|section)$")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    order_num: int = Field(..., gt=0)
    word_count_estimate: int = Field(0, ge=0)
    involved_characters: Optional[List[str]] = None
    viral_node_id: Optional[str] = None


class OutlineNodeUpdate(BaseModel):
    parent_id: Optional[str] = None
    node_type: Optional[str] = Field(None, regex="^(volume|chapter|section)$")
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    order_num: Optional[int] = Field(None, gt=0)
    word_count_estimate: Optional[int] = Field(None, ge=0)
    involved_characters: Optional[List[str]] = None
    viral_node_id: Optional[str] = None


class OutlineNodeResponse(BaseModel):
    id: str
    project_id: str
    parent_id: Optional[str]
    node_type: str
    title: str
    description: Optional[str]
    order_num: int
    word_count_estimate: int
    involved_characters: Optional[List[str]]
    viral_node_id: Optional[str]
    created_at: str


class OutlineConflict(BaseModel):
    node_id: str
    conflict_type: str
    description: str
    severity: str


class OutlineConflictReport(BaseModel):
    project_id: str
    conflicts: List[OutlineConflict]
    total_count: int


class AIGenerateOutline(BaseModel):
    genre: str
    target_word_count: int
    structure_preference: Optional[str] = None


class AIGenerateOutlineResponse(BaseModel):
    suggested_outline: List[dict]
    outline_description: str
    estimated_chapters: int

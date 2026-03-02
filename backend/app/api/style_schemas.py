from pydantic import BaseModel, Field
from typing import Optional, List


class StyleBaselineCreate(BaseModel):
    sentence_patterns: Optional[List[str]] = None
    vocabulary_profile: Optional[dict] = None
    tone_markers: Optional[List[str]] = None
    perspective: Optional[str] = Field(None, regex="^(第一人称|第三人称)$")


class StyleCheckResponse(BaseModel):
    chapter_id: str
    consistency_score: float = Field(..., ge=0, le=100)
    deviations: List[dict]
    suggestions: List[str]


class StyleBaselineResponse(BaseModel):
    id: str
    project_id: str
    sentence_patterns: List[str]
    vocabulary_profile: dict
    tone_markers: List[str]
    perspective: str
    created_at: str


class StyleReportResponse(BaseModel):
    project_id: str
    style_history: List[dict]
    overall_score: float
    suggestions: List[str]


class AIFlavorCheckResponse(BaseModel):
    text: str
    ai_flavor_score: float = Field(..., ge=0, le=100)
    issues: List[dict]
    suggestions: List[str]


class AIFlavorReductionRequest(BaseModel):
    intensity: int = Field(1, ge=1, le=10)
    keep_core_meaning: bool = True
    preserve_character_voice: bool = True


class AIFlavorReductionResponse(BaseModel):
    original_text: str
    reduced_text: str
    improvement_percentage: float

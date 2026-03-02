from pydantic import BaseModel, Field
from typing import Optional, List


class CharacterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=200)
    personality: Optional[List[str]] = None
    appearance: Optional[str] = Field(None, max_length=1000)
    background: Optional[str] = Field(None, max_length=2000)
    traits: Optional[dict] = None


class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=200)
    personality: Optional[List[str]] = None
    appearance: Optional[str] = Field(None, max_length=1000)
    background: Optional[str] = Field(None, max_length=2000)
    traits: Optional[dict] = None


class CharacterResponse(BaseModel):
    id: str
    project_id: str
    name: str
    age: Optional[int]
    personality: Optional[List[str]]
    appearance: Optional[str]
    background: Optional[str]
    traits: Optional[dict]
    created_at: Optional[str] = None


class CharacterRelationCreate(BaseModel):
    target_char_id: str
    relation_type: str = Field(..., regex="^(friend|enemy|lover|family)$")
    description: Optional[str] = Field(None, max_length=500)


class CharacterRelationResponse(BaseModel):
    id: str
    source_char_id: str
    target_char_id: str
    relation_type: str
    description: Optional[str]
    created_at: Optional[str] = None


class CharacterGraphData(BaseModel):
    nodes: List[dict]
    links: List[dict]

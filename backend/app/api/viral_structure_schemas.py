"""爆款结构服务Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ViralStructureTemplateResponse(BaseModel):
    id: str
    name: str
    genre: str
    description: str
    key_nodes: List[dict]
    success_cases: List[dict]


class StructureNodeSchema(BaseModel):
    node_id: str
    name: str
    description: str
    position_percentage: float
    writing_guidelines: List[str]
    is_critical: bool


class ViralStructureCreate(BaseModel):
    template_id: str
    custom_nodes: Optional[List[StructureNodeSchema]] = None


class ViralStructureUpdate(BaseModel):
    custom_nodes: Optional[List[StructureNodeSchema]] = None


class ProjectViralStructureResponse(BaseModel):
    id: str
    project_id: str
    template_id: str
    custom_nodes: List[StructureNodeSchema]
    current_node: Optional[str] = None
    completion_score: float


class ViralStructureReportResponse(BaseModel):
    project_id: str
    total_nodes: int
    critical_nodes_completed: int
    completion_score: float
    suggestions: List[str]


class SuccessCaseAnalysisResponse(BaseModel):
    template_id: str
    success_cases: List[dict]

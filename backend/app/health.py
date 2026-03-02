"""系统健康检查"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    database: str = "connected"
    redis: str = "connected"
    milvus: str = "disconnected"    minio: str = "disconnected"


class MetricsResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    total_projects: int
    total_users: int
    total_characters: int
    total_words: int


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    status = "healthy"
    version = "1.0.0"
    database = "connected"
    redis = "connected"
    milvus = "disconnected"
    minio = "disconnected"

    return HealthResponse(
        status=status,
        version=version,
        database=database,
        redis=redis,
        milvus=milvus
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    total_projects: 1  # Mock数据
    total_users: 1
    total_characters: 1
    total_words: 0

    return MetricsResponse(
        status="healthy",
        version="1.0.0",
        total_projects=total_projects,
        total_users=total_users,
        total_characters=total_characters,
        total_words=total_words
    )
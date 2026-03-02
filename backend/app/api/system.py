"""系统监控"""
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime

from app.database import get_db
from app.services.redis_client import redis_client
from app.api.errors import ErrorResponse


router = APIRouter(prefix="/system")


class SystemInfo(BaseModel):
    version: str = "1.0.0"
    project_count: int
    user_count: int
    total_words: int
    today_visitors: int


class ProjectStatistics(BaseModel):
    project_id: str
    total_chapters: int
    total_words: int
    completed_chapters: int
    completion_rate: float
    last_updated: Optional[str] = None


class SystemOverviewResponse(BaseModel):
    system_info: SystemInfo
    statistics: ProjectStatistics
    recent_activities: List[dict]


@router.get("/info", response_model=SystemOverviewResponse)
async def get_system_overview() -> SystemOverviewResponse:
    total_projects = 0
    total_users = 0

    result = await db.execute(
        select(func.count(Project.id)).where(Project.created_at >= datetime.now() - timedelta(days=30)
    )
    total_projects = result.scalar() or 0

    result = await db.execute(
        select(func.count(User.id))
    )
    total_users = result.scalar() or 0

    result = await db.execute(
        select(func.sum(Chapter.word_count))
        .join(Chapter, Project)
        .where(Chapter.created_at >= datetime.now() - timedelta(days=7))
    )
    total_words = result.scalar() or 0

    today_visitors = await get_today_visitors()

    return SystemOverviewResponse(
        system_info=SystemInfo(
            version="1.0.0",
            project_count=total_projects,
            user_count=total_users,
            total_words=total_words,
            today_visitors=today_visitors
        ),
        statistics=ProjectStatistics(
            project_id="system",
            total_chapters=0,
            total_words=0,
            completed_chapters=0,
            completion_rate=0.0,
            last_updated=None
        ),
        recent_activities=[
            {"action": "system initialized", "timestamp": datetime.now().isoformat()}
        ]
    )


async def get_today_visitors() -> int:
    cache_key = f"system:daily_visitors:{datetime.now().strftime('%Y-%m-%d')}"
    cached = await redis_client.get(cache_key)

    if cached:
        return int(cached["visitors"] or 0)

    visitors = await redis_client.get("system:daily_visitors") or {"visitors": 0}

    await redis_client.set(cache_key, {"visitors": visitors + 1}, expire=86400)

    return visitors


@router.get("/statistics")
async def get_project_statistics() -> List[ProjectStatistics]:
    result = await db.execute(
        select(Project)
        .order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    statistics = []
    for project in projects:
        result = await db.execute(
            select(func.count(Chapter.id))
            .where(Chapter.project_id == project.id)
        )
        total_chapters = result.scalar() or 0

        result = await db.execute(
            func.sum(Chapter.word_count)
            .where(Chapter.project_id == project.id)
        )
        total_words = result.scalar() or 0

        completion_rate = float(total_words / project.target_word_count) if project.target_word_count > 0 else 0.0

        result = await db.execute(
            func.max(Chapter.updated_at)
            .where(Chapter.project_id == project.id)
        )
        last_updated = result.scalar_one_or_none()

        statistics.append(ProjectStatistics(
            project_id=str(project.id),
            total_chapters=total_chapters,
            total_words=total_words,
            completed_chapters=completed_chapters,
            completion_rate=round(completion_rate, 2),
            last_updated=last_updated.isoformat() if last_updated else None
        )

    return statistics


@router.get("/health", response_model=SystemInfo)
async def check_system_health() -> SystemInfo:
    try:
        db_status = "connected" if await db.execute(select(1)) else "disconnected"
        redis_status = "connected" if await redis_client.client.ping() else "disconnected"
    milvus_status = "connected"

        status = "healthy"
        version = "1.0.0"

        if db_status == "disconnected":
            status = "degraded"

        return SystemInfo(
            status=status,
            version=version
        )

    except Exception as e:
        status = "unhealthy"
        return SystemInfo(
            status=status,
            version=version
        )
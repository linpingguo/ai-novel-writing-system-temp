from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models.models import Project, Chapter
from app.api.project_schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ExportResponse, ChapterExport
from app.services.auth_service import decode_access_token

router = APIRouter()


async def get_current_user_id(token: str = None) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    payload = decode_access_token(token)
    return payload.get("sub")


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user_id(token)

    db_project = Project(
        user_id=user_id,
        title=project.title,
        genre=project.genre,
        target_word_count=project.target_word_count,
        current_word_count=0
    )

    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)

    return ProjectResponse(
        id=str(db_project.id),
        user_id=str(db_project.user_id),
        title=db_project.title,
        genre=db_project.genre,
        target_word_count=db_project.target_word_count,
        current_word_count=db_project.current_word_count
    )


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user_id(token)

    result = await db.execute(
        select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    return [
        ProjectResponse(
            id=str(p.id),
            user_id=str(p.user_id),
            title=p.title,
            genre=p.genre,
            target_word_count=p.target_word_count,
            current_word_count=p.current_word_count
        )
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user_id(token)

    result = await db.execute(
        select(Project).where(
            (Project.id == project_id) & (Project.user_id == user_id)
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return ProjectResponse(
        id=str(project.id),
        user_id=str(project.user_id),
        title=project.title,
        genre=project.genre,
        target_word_count=project.target_word_count,
        current_word_count=project.current_word_count
    )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user_id(token)

    result = await db.execute(
        select(Project).where(
            (Project.id == project_id) & (Project.user_id == user_id)
        )
    )
    db_project = result.scalar_one_or_none()

    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    if project_update.title is not None:
        db_project.title = project_update.title
    if project_update.genre is not None:
        db_project.genre = project_update.genre
    if project_update.target_word_count is not None:
        db_project.target_word_count = project_update.target_word_count

    await db.commit()
    await db.refresh(db_project)

    return ProjectResponse(
        id=str(db_project.id),
        user_id=str(db_project.user_id),
        title=db_project.title,
        genre=db_project.genre,
        target_word_count=db_project.target_word_count,
        current_word_count=db_project.current_word_count
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user_id(token)

    result = await db.execute(
        select(Project).where(
            (Project.id == project_id) & (Project.user_id == user_id)
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    await db.delete(project)
    await db.commit()

    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/export", response_model=ExportResponse)
async def export_project(
    project_id: str,
    format: str = "markdown",
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user_id(token)

    result = await db.execute(
        select(Project).where(
            (Project.id == project_id) & (Project.user_id == user_id)
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    chapters_result = await db.execute(
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.created_at)
    )
    chapters = chapters_result.scalars().all()

    total_word_count = sum(c.word_count for c in chapters)

    chapter_exports = [
        ChapterExport(
            title=c.title,
            content=c.content,
            order=i
        )
        for i, c in enumerate(chapters, 1)
    ]

    filename = f"{project.title}_export.md"

    return ExportResponse(
        filename=filename,
        chapters=chapter_exports,
        total_word_count=total_word_count
    )

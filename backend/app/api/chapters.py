from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.sql.expression import case
from typing import List

from app.database import get_db
from app.models.models import Chapter, OutlineNode, Project
from app.services.auth_service import decode_access_token
from app.api.chaper_schemas import (
    ChapterCreate, ChapterUpdate, ChapterResponse,
    AIGenerateRequest, AIPolishRequest, DialogueGenerateRequest,
    AutosaveResponse, AIVersion, AIPolishSuggestion
)
from app.services.redis_client import redis_client


router = APIRouter()


async def verify_project_access(project_id: str, token: str, db: AsyncSession) -> None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@router.post("/", response_model=ChapterResponse)
async def create_chapter(
    project_id: str,
    chapter: ChapterCreate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    user_id = await decode_access_token(token).get("sub")

    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project or project.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )

    db_chapter = Chapter(
        project_id=project_id,
        title=chapter.title,
        content='',
        content_format=chapter.content_format,
        word_count=0,
        status='draft',
        ai_generated_ratio=0
    )

    db.add(db_chapter)
    await db.commit()
    await db.refresh(db_chapter)

    await update_project_word_count(db, project_id)

    return ChapterResponse(
        id=str(db_chapter.id),
        project_id=str(db_chapter.project_id),
        outline_node_id=db_chapter.outline_node_id,
        title=db_chapter.title,
        content=db_chapter.content,
        content_format=db_chapter.content_format,
        word_count=db_chapter.word_count,
        status=db_chapter.status,
        ai_generated_ratio=db_chapter.ai_generated_ratio,
        created_at=db_chapter.created_at.isoformat(),
        updated_at=db_chapter.updated_at.isoformat()
    )


@router.get("/", response_model=List[ChapterResponse])
async def get_chapters(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.created_at.desc())
    )
    chapters = result.scalars().all()

    return [
        ChapterResponse(
            id=str(c.id),
            project_id=str(c.project_id),
            outline_node_id=str(c.outline_node_id) if c.outline_node_id else None,
            title=c.title,
            content=c.content,
            content_format=c.content_format,
            word_count=c.word_count,
            status=c.status,
            ai_generated_ratio=c.ai_generated_ratio,
            style_score=c.style_score,
            ai_flavor_score=c.ai_flavor_score,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat()
        )
        for c in chapters
    ]


@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    project_id: str,
    chapter_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Chapter).where(
            (Chapter.id == chapter_id) & (Chapter.project_id == project_id)
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )

    return ChapterResponse(
        id=str(chapter.id),
        project_id=str(chapter.project_id),
        outline_node_id=str(chapter.outline_node_id) if chapter.outline_node_id else None,
        title=chapter.title,
        content=chapter.content,
        content_format=chapter.content_format,
        word_count=chapter.word_count,
        status=chapter.status,
        ai_generated_ratio=chapter.ai_generated_ratio,
        style_score=chapter.style_score,
        ai_flavor_score=chapter.ai_flavor_score,
        created_at=chapter.created_at.isoformat(),
        updated_at=chapter.updated_at.isoformat()
    )


@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    project_id: str,
    chapter_id: str,
    chapter_update: ChapterUpdate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Chapter).where(
            (Chapter.id == chapter_id) & (Chapter.project_id == project_id)
        )
    )
    db_chapter = result.scalar_one_or_none()

    if not db_chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )

    if chapter_update.title is not None:
        db_chapter.title = chapter_update.title
    if chapter_update.content is not None:
        db_chapter.content = chapter_update.content
    if chapter_update.status is not None:
        db_chapter.status = chapter_update.status

    await db.commit()
    await db.refresh(db_chapter)

    new_word_count = len(db_chapter.content) if db_chapter.content else 0
    await db.execute(
        text("UPDATE chapters SET word_count = :word_count WHERE id = :id"),
        {"word_count": new_word_count, "id": db_chapter.id}
        .execution_options(synchronize_session="fetch")
    )

    await update_project_word_count(db, project_id)

    return ChapterResponse(
        id=str(db_chapter.id),
        project_id=str(db_chapter.project_id),
        outline_node_id=str(db_chapter.outline_node_id) if db_chapter.outline_node_id else None,
        title=db_chapter.title,
        content=db_chapter.content,
        content_format=db_chapter.content_format,
        word_count=new_word_count,
        status=db_chapter.status,
        ai_generated_ratio=db_chapter.ai_generated_ratio,
        style_score=db_chapter.style_score,
        ai_flavor_score=db_chapter.ai_flavor_score,
        created_at=db_chapter.created_at.isoformat(),
        updated_at=db_chapter.updated_at.isoformat()
    )


@router.delete("/{chapter_id}")
async def delete_chapter(
    project_id: str,
    chapter_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Chapter).where(
            (Chapter.id == chapter_id) & (Chapter.project_id == project_id)
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )

    old_word_count = chapter.word_count
    await db.delete(chapter)
    await db.commit()

    await update_project_word_count(db, project_id)

    return {"message": "Chapter deleted successfully"}


async def update_project_word_count(db: AsyncSession, project_id: str) -> None:
    result = await db.execute(
        select(func.sum(Chapter.word_count))
        .where(Chapter.project_id == project_id)
    )
    total = result.scalar() or 0

    await db.execute(
        text("UPDATE projects SET current_word_count = :word_count WHERE id = :id"),
        {"current_word_count": total, "id": project_id}
    )


@router.post("/{chapter_id}/generate", response_model=List[AIVersion])
async def ai_generate_chapter(
    project_id: str,
    chapter_id: str,
    request: AIGenerateRequest,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Chapter).where(
            (Chapter.id == chapter_id) & (Chapter.project_id == project_id)
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )

    context_prompt = f"Context: Previous chapters and outline information. Current chapter: {chapter.title}."
    style_prompt = f"Style: Maintain consistency with previous chapters."

    versions = []

    for i in range(request.versions):
        generated_content = await mock_ai_generate(
            f"{context_prompt}\n\nGenerate chapter content (500-2000 words) for {chapter.title}",
            style_prompt,
            reduce_ai_flavor=request.reduce_ai_flavor
        )

        versions.append(AIVersion(
            version=i + 1,
            content=generated_content
        ))

    return versions


@router.post("/{chapter_id}/polish", response_model=AIPolishSuggestion)
async def ai_polish_chapter(
    project_id: str,
    chapter_id: str,
    request: AIPolishRequest,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Chapter).where(
            (Chapter.id == chapter_id) & (Chapter.project_id == project_id)
        )
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )

    polished_content = await mock_ai_generate(
            f"Polish the following chapter content to improve clarity and style:\n\n{chapter.content}",
            "Maintain the writing style",
            reduce_ai_flavor=True
        )

    return AIPolishSuggestion(
            original_text=chapter.content,
            suggested_text=polished_content,
            change_type="style_improvement",
            reason="Enhanced clarity and consistency"
        )


@router.post("/{chapter_id}/dialogue")
async def ai_generate_dialogue(
    project_id: str,
    chapter_id: str,
    request: DialogueGenerateRequest,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    from app.models.models import Character
    char_result = await db.execute(
        select(Character).where(Character.id.in_(request.characters))
    )
    characters = char_result.scalars().all()

    character_map = {str(c.id): c for c in characters}

    dialogue_prompt = f"Generate natural dialogue between the following characters in the scene: {request.scene}\n\n"
    for char_id, char_name in request.characters:
        char = character_map.get(char_id)
        if char:
            dialogue_prompt += f"- {char_name}: {char.name} (Age: {char.age}, Personality: {char.personality})\n"

    dialogue_prompt += "Make the dialogue natural and fitting for each character's personality."

    dialogue_content = await mock_ai_generate(dialogue_prompt, "Generate dialogue with character voices", True)

    dialogue_turns = []
    for line in dialogue_content.split('\n'):
        parts = line.split(':', 1)
        if len(parts) == 2:
            char_id_match = next((cid for cid, name in request.characters if cid in parts[0]), None)
            if char_id_match:
                character = character_map.get(char_id_match)
                dialogue_turns.append(DialogueTurn(
                    character_id=char_id_match,
                    content=parts[1].strip()
                ))

    return dialogue_turns


@router.post("/autosave", response_model=AutosaveResponse)
async def autosave_chapter(
    project_id: str,
    chapter_id: str,
    content: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    cache_key = f"project:{project_id}:chapter:{chapter_id}:draft"
    await redis_client.set(cache_key, {
        "content": content,
        "saved_at": func.now().isoformat()
    }, expire=300)

    return AutosaveResponse(
        message="Auto-saved successfully",
        saved_at=func.now().isoformat()
    )


async def mock_ai_generate(prompt: str, system_instruction: str = "", reduce_flavor: bool = False) -> str:
    return f"[MOCK AI RESPONSE] {prompt}\n\nThis is a simulated response for development purposes."


@router.get("/history/{chapter_id}")
async def get_generation_history(
    project_id: str,
    chapter_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    cache_key = f"project:{project_id}:generation:history"
    history = await redis_client.get(cache_key) or []

    return {"history": history}

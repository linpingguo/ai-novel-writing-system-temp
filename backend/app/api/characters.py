from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.models import Character, CharacterRelation, Project
from app.services.auth_service import decode_access_token
from app.api.character_schemas import (
    CharacterCreate, CharacterUpdate, CharacterResponse,
    CharacterRelationCreate, CharacterRelationResponse, CharacterGraphData
)

router = APIRouter()


async def verify_project_access(project_id: str, token: str, db: AsyncSession) -> None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@router.post("/", response_model=CharacterResponse)
async def create_character(
    project_id: str,
    character: CharacterCreate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    username = decode_access_token(token).get("sub")

    await verify_project_access(project_id, token, db)

    db_character = Character(
        project_id=project_id,
        name=character.name,
        age=character.age,
        personality=character.personality or [],
        appearance=character.appearance,
        background=character.background,
        traits=character.traits or {}
    )

    db.add(db_character)
    await db.commit()
    await db.refresh(db_character)

    return CharacterResponse(
        id=str(db_character.id),
        project_id=str(db_character.project_id),
        name=db_character.name,
        age=db_character.age,
        personality=db_character.personality,
        appearance=db_character.appearance,
        background=db_character.background,
        traits=db_character.traits
    )


@router.get("/", response_model=List[CharacterResponse])
async def get_characters(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Character)
        .where(Character.project_id == project_id)
        .order_by(Character.created_at.desc())
    )
    characters = result.scalars().all()

    return [
        CharacterResponse(
            id=str(c.id),
            project_id=str(c.project_id),
            name=c.name,
            age=c.age,
            personality=c.personality,
            appearance=c.appearance,
            background=c.background,
            traits=c.traits
        )
        for c in characters
    ]


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    project_id: str,
    character_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Character).where(
            (Character.id == character_id) & (Character.project_id == project_id)
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    return CharacterResponse(
        id=str(character.id),
        project_id=str(character.project_id),
        name=character.name,
        age=character.age,
        personality=character.personality,
        appearance=character.appearance,
        background=character.background,
        traits=character.traits
    )


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    project_id: str,
    character_id: str,
    character_update: CharacterUpdate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Character).where(
            (Character.id == character_id) & (Character.project_id == project_id)
        )
    )
    db_character = result.scalar_one_or_none()

    if not db_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    if character_update.name is not None:
        db_character.name = character_update.name
    if character_update.age is not None:
        db_character.age = character_update.age
    if character_update.personality is not None:
        db_character.personality = character_update.personality
    if character_update.appearance is not None:
        db_character.appearance = character_update.appearance
    if character_update.background is not None:
        db_character.background = character_update.background
    if character_update.traits is not None:
        db_character.traits = character_update.traits

    await db.commit()
    await db.refresh(db_character)

    return CharacterResponse(
        id=str(db_character.id),
        project_id=str(db_character.project_id),
        name=db_character.name,
        age=db_character.age,
        personality=db_character.personality,
        appearance=db_character.appearance,
        background=db_character.background,
        traits=db_character.traits
    )


@router.delete("/{character_id}")
async def delete_character(
    project_id: str,
    character_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Character).where(
            (Character.id == character_id) & (Character.project_id == project_id)
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    await db.delete(character)
    await db.commit()

    return {"message": "Character deleted successfully"}


@router.post("/{character_id}/relations", response_model=CharacterRelationResponse)
async def create_relation(
    project_id: str,
    character_id: str,
    relation: CharacterRelationCreate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(CharacterRelation).where(
            (CharacterRelation.source_char_id == character_id) &
            (CharacterRelation.target_char_id == relation.target_char_id)
        )
    )
    existing_relation = result.scalar_one_or_none()

    if existing_relation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Relation already exists between these characters"
        )

    db_relation = CharacterRelation(
        source_char_id=character_id,
        target_char_id=relation.target_char_id,
        relation_type=relation.relation_type,
        description=relation.description
    )

    db.add(db_relation)
    await db.commit()
    await db.refresh(db_relation)

    return CharacterRelationResponse(
        id=str(db_relation.id),
        source_char_id=str(db_relation.source_char_id),
        target_char_id=str(db_relation.target_char_id),
        relation_type=db_relation.relation_type,
        description=db_relation.description
    )


@router.get("/graph", response_model=CharacterGraphData)
async def get_character_graph(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Character).where(Character.project_id == project_id)
    )
    characters = result.scalars().all()

    result = await db.execute(
        select(CharacterRelation).where(
            CharacterRelation.source_char_id.in_([c.id for c in characters])
        )
    )
    relations = result.scalars().all()

    nodes = [
        {
            "id": str(c.id),
            "label": c.name,
            "group": "characters"
        }
        for c in characters
    ]

    links = [
        {
            "source": str(r.source_char_id),
            "target": str(r.target_char_id),
            "label": r.relation_type
        }
        for r in relations
    ]

    return CharacterGraphData(nodes=nodes, links=links)

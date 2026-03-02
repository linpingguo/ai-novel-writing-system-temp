from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import json

from app.database import get_db
from app.models.models import OutlineNode, Project, Chapter
from app.services.auth_service import decode_access_token
from app.api.outline_schemas import (
    OutlineNodeCreate, OutlineNodeUpdate, OutlineNodeResponse,
    OutlineConflict, OutlineConflictReport,
    AIGenerateOutline, AIGenerateOutlineResponse
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


def build_outline_tree(nodes: List[OutlineNode]) -> List[OutlineNodeResponse]:
    node_map = {str(node.id): node for node in nodes}
    root_nodes = [node for node in nodes if node.parent_id is None]

    def to_response(node: OutlineNode) -> OutlineNodeResponse:
        return OutlineNodeResponse(
            id=str(node.id),
            project_id=str(node.project_id),
            parent_id=str(node.parent_id) if node.parent_id else None,
            node_type=node.node_type,
            title=node.title,
            description=node.description,
            order_num=node.order_num,
            word_count_estimate=node.word_count_estimate,
            involved_characters=json.loads(node.involved_characters) if node.involved_characters else None,
            viral_node_id=node.viral_node_id,
            created_at=node.created_at.isoformat() if node.created_at else None
        )

    tree = []
    for root in root_nodes:
        stack = [root]
        while stack:
            current = stack.pop()
            tree.append(to_response(current))
            children = [node for node in nodes if node.parent_id == str(current.id)]
            for child in sorted(children, key=lambda x: x.order_num):
                stack.append(child)

    return tree


@router.post("/", response_model=OutlineNodeResponse)
async def create_node(
    project_id: str,
    node: OutlineNodeCreate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    if node.parent_id:
        result = await db.execute(
            select(OutlineNode).where(OutlineNode.id == node.parent_id)
        )
        parent = result.scalar_one_or_none()
        if not parent or parent.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent node not found or does not belong to this project"
            )

    max_order_result = await db.execute(
        select(func.max(OutlineNode.order_num))
        .where(OutlineNode.project_id == project_id)
        .where(
            (OutlineNode.parent_id == node.parent_id) if node.parent_id else (OutlineNode.parent_id.is_(None))
        )
    )
    max_order = max_order_result.scalar() or 0

    db_node = OutlineNode(
        project_id=project_id,
        parent_id=node.parent_id,
        node_type=node.node_type,
        title=node.title,
        description=node.description,
        order_num=max_order + 1,
        word_count_estimate=node.word_count_estimate,
        involved_characters=json.dumps(node.involved_characters) if node.involved_characters else None,
        viral_node_id=node.viral_node_id
    )

    db.add(db_node)
    await db.commit()
    await db.refresh(db_node)

    return to_response(db_node)


@router.get("/", response_model=List[OutlineNodeResponse])
async def get_outline_tree(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(OutlineNode).where(OutlineNode.project_id == project_id).order_by(OutlineNode.order_num)
    )
    nodes = result.scalars().all()

    return build_outline_tree(nodes)


@router.get("/{node_id}", response_model=OutlineNodeResponse)
async def get_node(
    project_id: str,
    node_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(OutlineNode).where(
            (OutlineNode.id == node_id) & (OutlineNode.project_id == project_id)
        )
    )
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outline node not found"
        )

    return to_response(node)


@router.put("/{node_id}", response_model=OutlineNodeResponse)
async def update_node(
    project_id: str,
    node_id: str,
    node_update: OutlineNodeUpdate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(OutlineNode).where(
            (OutlineNode.id == node_id) & (OutlineNode.project_id == project_id)
        )
    )
    db_node = result.scalar_one_or_none()

    if not db_node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outline node not found"
        )

    if node_update.parent_id is not None:
        result = await db.execute(
            select(OutlineNode).where(OutlineNode.id == node_update.parent_id)
        )
        parent = result.scalar_one_or_none()
        if not parent or parent.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New parent not found or does not belong to this project"
            )

    if node_update.title is not None:
        db_node.title = node_update.title
    if node_update.description is not None:
        db_node.description = node_update.description
    if node_update.word_count_estimate is not None:
        db_node.word_count_estimate = node_update.word_count_estimate
    if node_update.involved_characters is not None:
        db_node.involved_characters = json.dumps(node_update.involved_characters)
    if node_update.viral_node_id is not None:
        db_node.viral_node_id = node_update.viral_node_id

    await db.commit()
    await db.refresh(db_node)

    return to_response(db_node)


@router.delete("/{node_id}")
async def delete_node(
    project_id: str,
    node_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(OutlineNode).where(
            (OutlineNode.id == node_id) & (OutlineNode.project_id == project_id)
        )
    )
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outline node not found"
        )

    await db.delete(node)
    await db.commit()

    return {"message": "Outline node deleted successfully"}


@router.post("/reorder")
async def reorder_nodes(
    project_id: str,
    node_orders: List[dict],
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    for node_order in node_orders:
        node_id = node_order.get("node_id")
        new_order = node_order.get("order_num")

        if not node_id or not new_order:
            continue

        result = await db.execute(
            select(OutlineNode).where(
                (OutlineNode.id == node_id) & (OutlineNode.project_id == project_id)
            )
        )
        db_node = result.scalar_one_or_none()

        if db_node:
            db_node.order_num = new_order

    await db.commit()

    return {"message": "Outline nodes reordered successfully"}


@router.get("/conflicts", response_model=OutlineConflictReport)
async def check_conflicts(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(OutlineNode).where(OutlineNode.project_id == project_id)
    )
    nodes = result.scalars().all()

    conflicts = []

    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes[i + 1:], i + 1):
            if node1.description and node2.description:
                similarity = len(set(node1.description.split()) & set(node2.description.split())) / len(set(node1.description.split() | set(node2.description.split()))
                if similarity > 0.8:
                    conflicts.append(OutlineConflict(
                        node_id=str(node2.id),
                        conflict_type="description_similarity",
                        description=f"Node {node1.title} and {node2.title} have similar descriptions",
                        severity="medium"
                    ))

    return OutlineConflictReport(
        project_id=project_id,
        conflicts=conflicts,
        total_count=len(conflicts)
    )


@router.post("/ai-generate", response_model=AIGenerateOutlineResponse)
async def ai_generate_outline(
    project_id: str,
    request: AIGenerateOutline,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    prompt = f"""
    Generate a detailed outline for a {request.genre} novel of {request.target_word_count} words.

    Requirements:
    1. Create a three-tier structure (volume/chapter/section)
    2. Each chapter should be 2000-3000 words
    3. Total chapters: ~{request.target_word_count // 2500}

    Format:
    Return a JSON array of outline nodes with structure:
    {{
        "outline": [
            {{
                "node_type": "volume",
                "title": "Volume 1",
                "description": "Introduction and setup",
                "children": [
                    {{
                        "node_type": "chapter",
                        "title": "Chapter 1",
                        "description": "Protagonist introduction",
                        "word_count_estimate": 2500
                    }},
                    {{
                        "node_type": "chapter",
                        "title": "Chapter 2",
                        "description": "Inciting incident",
                        "word_count_estimate": 2500
                    }}
                ]
            }}
        ]
    }}

    Style guidelines:
    - Engaging and fast-paced
    - Clear character motivations
    - Strong plot progression
    - Satisfying climax
    """

    try:
        response = await call_openai_api(prompt)
        outline_data = json.loads(response)

        suggested_outline = []
        for volume in outline_data.get("outline", []):
            def process_nodes(items):
                return [{
                    "node_type": item["node_type"],
                    "title": item["title"],
                    "description": item["description"],
                    "order": idx + 1,
                    "word_count_estimate": item.get("word_count_estimate", 2500),
                    "children": process_nodes(item.get("children", []))
                } for idx, item in enumerate(items)]

            suggested_outline.extend(process_nodes([volume]))

        return AIGenerateOutlineResponse(
            suggested_outline=suggested_outline,
            outline_description="Generated outline structure for your novel",
            estimated_chapters=len(suggested_outline)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate outline: {str(e)}"
        )


async def call_openai_api(prompt: str) -> str:
    from app.config import settings
    import openai

    client = openai.OpenAI(api_key=settings.openai_api_key if settings.openai_api_key else "dummy_key")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise e

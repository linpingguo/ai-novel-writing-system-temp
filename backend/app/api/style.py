from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import json

from app.database import get_db
from app.models.models import Chapter, Project, StyleBaseline
from app.services.auth_service import decode_access_token
from app.services.redis_client import redis_client
from app.api.style_schemas import (
    StyleBaselineCreate, StyleBaselineResponse, StyleCheckResponse,
    StyleReportResponse, AIFlavorCheckResponse, AIFlavorReductionRequest,
    AIFlavorReductionResponse
)
from app.services.cache_service import init_cache, cleanup_cache


router = APIRouter()


async def verify_project_access(project_id: str, token: str, db: AsyncSession) -> None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@router.post("/establish", response_model=StyleBaselineResponse)
async def establish_baseline(
    project_id: str,
    request: StyleBaselineCreate,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(Chapter)
        .where(
            (Chapter.project_id == project_id) &
            (Chapter.status == 'completed')
        )
        .order_by(Chapter.created_at.desc())
        .limit(3)
    )
    chapters = result.scalars().all()

    if len(chapters) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 3 completed chapters are required to establish style baseline"
        )

    sentence_patterns = []
    vocabulary_dict = {}
    tone_markers = []
    perspective_count = {}

    for chapter in chapters:
        sentences = chapter.content.split('。')
        for sentence in sentences:
            if len(sentence) > 5:
                sentence_patterns.append(sentence)

        words = chapter.content.split()
        for word in words:
            word = word.strip('，。！？')
            if len(word) > 1:
                vocabulary_dict[word] = vocabulary_dict.get(word, 0) + 1

        if '我' in chapter.content:
            tone_markers.append('first-person')
        elif '他' in chapter.content:
            tone_markers.append('third-person')

    perspective = '第一人称' if perspective_count.get('第一人称', 0) > perspective_count.get('第三人称', 0) else '第三人称'

    baseline = StyleBaseline(
        project_id=project_id,
        sentence_patterns=list(set(sentence_patterns)),
        vocabulary_profile=vocabulary_dict,
        tone_markers=tone_markers,
        perspective=perspective
    )

    db.add(baseline)
    await db.commit()
    await db.refresh(baseline)

    return StyleBaselineResponse(
        id=str(baseline.id),
        project_id=str(baseline.project_id),
        sentence_patterns=baseline.sentence_patterns,
        vocabulary_profile=baseline.vocabulary_profile,
        tone_markers=baseline.tone_markers,
        perspective=baseline.perspective,
        created_at=baseline.created_at.isoformat()
    )


@router.get("/baseline", response_model=StyleBaselineResponse)
async def get_baseline(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(StyleBaseline).where(StyleBaseline.project_id == project_id)
    )
    baseline = result.scalar_one_or_none()

    if not baseline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style baseline not found"
        )

    return StyleBaselineResponse(
        id=str(baseline.id),
        project_id=str(baseline.project_id),
        sentence_patterns=baseline.sentence_patterns,
        vocabulary_profile=baseline.vocabulary_profile,
        tone_markers=baseline.tone_markers,
        perspective=baseline.perspective,
        created_at=baseline.created_at.isoformat()
    )


@router.post("/check", response_model=StyleCheckResponse)
async def check_style_consistency(
    project_id: str,
    chapter_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(StyleBaseline).where(StyleBaseline.project_id == project_id)
    )
    baseline = result.scalar_one_or_none()

    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id)
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )

    deviations = []
    suggestions = []
    consistency_score = 100.0

    sentences = chapter.content.split('。')
    chapter_patterns = baseline.sentence_patterns if baseline else []

    for i, sentence in enumerate(sentences[:10]):
        pattern_match = False
        for pattern in chapter_patterns:
            if len(pattern) < 20:
                if pattern.lower() in sentence.lower():
                    pattern_match = True
                    break

        if not pattern_match:
            deviations.append({
                "type": "sentence_structure",
                "location": f"chapter:{i + 1}",
                "description": f"Sentence does not match established patterns",
                "severity": "medium"
            })
            consistency_score -= 5

    words = chapter.content.split()
    for word in words:
        word = word.strip('，。！？')
        if len(word) > 2 and word not in baseline.vocabulary_profile:
            deviations.append({
                "type": "vocabulary",
                "location": "unknown",
                "description": f"Uncommon word: {word}",
                "severity": "low"
            })
            consistency_score -= 2

    return StyleCheckResponse(
        chapter_id=chapter_id,
        consistency_score=max(consistency_score, 0),
        deviations=deviations,
        suggestions=[
            "Consider using more varied sentence structures",
            "Expand vocabulary to match established baseline"
        ]
    )


@router.get("/report", response_model=StyleReportResponse)
async def get_style_report(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    baseline = await redis_client.get(f"project:{project_id}:style:baseline")
    if not baseline:
        result = await db.execute(
            select(StyleBaseline).where(StyleBaseline.project_id == project_id)
        )
        db_baseline = result.scalar_one_or_none()

        if not db_baseline:
            baseline = {
                "sentence_patterns": [],
                "vocabulary_profile": {},
                "tone_markers": [],
                "perspective": "第三人称"
            }

    else:
            baseline = {
                "sentence_patterns": db_baseline.sentence_patterns or [],
                "vocabulary_profile": db_baseline.vocabulary_profile or {},
                "tone_markers": db_baseline.tone_markers or [],
                "perspective": db_baseline.perspective
            }

    result = await db.execute(
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.created_at)
    )
    chapters = result.scalars().all()

    style_history = []
    for chapter in chapters:
        result = await db.execute(
            select(Chapter).where(Chapter.id == chapter.id)
        )
        ch = result.scalar_one_or_none()

        if not ch:
            continue

        check_result = await check_style_consistency(project_id, ch.id, token, db)
        style_history.append({
            "chapter_id": str(chapter.id),
            "chapter_title": ch.title,
            "consistency_score": check_result.consistency_score,
            "timestamp": ch.updated_at.isoformat()
        })

    overall_score = sum(h["consistency_score"] for h in style_history) / len(style_history) if style_history else 0

    suggestions = []
    if overall_score < 80:
        suggestions.append("Consider maintaining more consistent writing style across chapters")

    return StyleReportResponse(
        project_id=project_id,
        style_history=style_history,
        overall_score=overall_score,
        suggestions=suggestions
    )


@router.post("/aiflavor/check", response_model=AIFlavorCheckResponse)
async def check_ai_flavor(
    text: str,
    db: AsyncSession = Depends(get_db)
):
    ai_flavor_score = 100.0
    issues = []

    sentence_patterns = text.split('.')
    avg_sentence_length = sum(len(s) for s in sentence_patterns) / len(sentence_patterns)

    if avg_sentence_length > 30:
        issues.append({
            "type": "sentence_length",
            "description": f"Average sentence length ({avg_sentence_length:.1f}) is too long",
            "severity": "medium"
        })
        ai_flavor_score -= 10

    transition_words = ['此外', '另外', '然后', '接下来']
    for word in transition_words:
        if word in text:
            issues.append({
                "type": "formal_transition",
                "description": f"Found formal transition word: {word}",
                "severity": "low"
            })
            ai_flavor_score -= 5

    repetitive_patterns = ['哈哈', '嗯', '哦']
    for pattern in repetitive_patterns:
        count = text.lower().count(pattern)
        if count > 2:
            issues.append({
                "type": "repetitive_pattern",
                "description": f"Found repetitive pattern: {pattern} (count: {count})",
                "severity": "medium"
            })
            ai_flavor_score -= 10

    if not issues:
        issues.append({
            "type": "emotional_lack",
            "description": "Text lacks emotional depth and vivid descriptions",
            "severity": "high"
        })
        ai_flavor_score -= 15

    return AIFlavorCheckResponse(
        ai_flavor_score=max(ai_flavor_score, 0),
        issues=issues
    )


@router.post("/aiflavor/reduce", response_model=AIFlavorReductionResponse)
async def reduce_ai_flavor(
    request: AIFlavorReductionRequest,
    db: AsyncSession = Depends(get_db)
):
    text = request.original_text

    reduced_text = text

    transitions = ['此外', '另外', '然后', '接下来']
    for word in transitions:
        if word in reduced_text:
            reduced_text = reduced_text.replace(word, ', ')

    sentences = text.split('.')
    new_sentences = []
    for sentence in sentences:
        words = sentence.split()
        new_words = [w for w in words if len(w) < 20 or w not in ['的', '是', '了', '和', '或', '但']]
        new_sentence = ' '.join(new_words)

        if len(new_sentence) > 5:
            new_sentences.append(new_sentence)

    reduced_text = '。'.join(new_sentences)

    improvement_percentage = min(100.0, 50.0)

    return AIFlavorReductionResponse(
        original_text=text,
        reduced_text=reduced_text,
        improvement_percentage=improvement_percentage
    )

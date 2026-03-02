"""爆款结构服务"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Optional

from app.database import get_db
from app.models.models import Project, ProjectViralStructure
from app.api.viral_structure_schemas import (
    ViralStructureTemplate, ProjectViralStructure,
    StructureNodeSchema, StructureNodeCreate, StructureNodeUpdate
    ViralStructureCreate, ViralStructureUpdate,
    ProjectViralStructureResponse, ViralStructureReportResponse,
    SuccessCaseAnalysisResponse
)
from app.services.auth_service import decode_access_token


router = APIRouter()


async def verify_project_access(project_id: str, token: str, db: AsyncSession) -> None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@router.get("/templates", response_model=List[ViralStructureTemplate])
async def get_templates(
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    username = decode_access_token(token).get("sub")

    result = await db.execute(
        select(ViralStructureTemplate).where(ViralStructureTemplate.is_active == True)
        .order_by(ViralStructureTemplate.created_at.desc())
    )
    templates = result.scalars().all()

    return templates


@router.get("/templates/{template_id}", response_model=ViralStructureTemplate)
async def get_template(
    template_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ViralStructureTemplate).where(ViralStructureTemplate.id == template_id)
        )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return template


@router.get("/templates/{template_id}/analysis", response_model=SuccessCaseAnalysisResponse)
async def get_template_analysis(
    template_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
    result = await db.execute(
        select(ViralStructureTemplate).where(ViralStructureTemplate.id == template_id)
        )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return {
        "template_id": template.id,
        "template_name": template.name,
        "genre": template.genre,
        "description": template.description,
        "success_cases": template.success_cases or []
    }


@router.post("/projects/{project_id}/viral-structure", response_model=ProjectViralStructure)
async def apply_template(
    project_id: str,
    template_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Dep埃nds(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(ViralStructureTemplate).where(ViralStructureTemplate.id == template_id)
        )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    result = await db.execute(
            select(ProjectViralStructure).where(ProjectViralStructure.project_id == project_id)
        )
    existing_structure = result.scalar_one_or_none()

    if existing_structure:
        await db.execute(
            delete(ProjectViralStructure).where(ProjectViralStructure.project_id == project_id)
        )

    db_structure = ProjectViralStructure(
        project_id=project_id,
        template_id=template_id,
        template_id=template_id,
        custom_nodes=[],
        current_node=None,
        completion_score=0.0
    )

    db.add(db_structure)
    await db.commit()
    await db.refresh(db_structure)

    return ProjectViralStructureResponse(
        id=str(db_structure.id),
        project_id=str(project_id),
        template_id=str(db_structure.template_id),
        custom_nodes=db_structure.custom_nodes,
        current_node=db_structure.current_node,
        completion_score=db_structure.completion_score
    )


@router.get("/current", response_model=Dict)
async def get_current_node(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(ProjectViralStructure).where(ProjectViralStructure.project_id == project_id)
        )
    structure = result.scalar_one_or_none()

    if not structure:
        return {"current_node": None}

    return {
        "project_id": project_id,
        "current_node": structure.current_node,
        "completion_score": structure.completion_score if structure else 0
    }


@router.post("/customize", response_model=ProjectViralStructureResponse)
async def customize_structure(
    project_id: str,
    request: Dict,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(ProjectViralStructure).where(ProjectViralStructure.project_id == project_id)
        )
    structure = result.scalar_one_or_none()

    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No viral structure found for this project"
        )

    if "custom_nodes" in request:
        db_structure.custom_nodes = request["custom_nodes"]

    await db.commit()
    await db.refresh(db_structure)

    return ProjectViralStructureResponse(
        id=str(structure.id),
        project_id=str(structure.project_id),
        template_id=str(structure.template_id),
        custom_nodes=db_structure.custom_nodes,
        current_node=db_structure.current_node,
        completion_score=db_structure.completion_score
    )


@router.get("/report", response_model=ViralStructureReportResponse)
async def get_structure_report(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(ProjectViralStructure).where(ProjectViralStructure.project_id == project_id)
        )
    structure = result.scalar_one_or_none()

    if not structure:
        return {
            "project_id": project_id,
            "total_nodes": 0,
            "critical_nodes_completed": 0,
            "completion_score": 0.0,
            "suggestions": []
        }

    result = await db.execute(
        select(OutlineNode).where(
            (OutlineNode.project_id == project_id) &
            (OutlineNode.viral_node_id != None)
        )
    )
    outline_nodes = result.scalars().all()

    total_nodes = len(outline_nodes)
    critical_nodes_completed = sum(1 for node in outline_nodes if node.viral_node_id and node.viral_node_id != "" and node.viral_node_id in [n.viral_node_id for n in outline_nodes])

    completion_score = (critical_nodes_completed / total_nodes) * 100 if total_nodes > 0 else 0

    suggestions = []

    if completion_score < 50:
        suggestions.append("建议:考虑添加更多关键节点以提升作品质量")

    return {
        "project_id": project_id,
        "total_nodes": total_nodes,
        "critical_nodes_completed": critical_nodes_completed,
        "completion_score": completion_score,
        "suggestions": suggestions
    }


@router.delete("/", response_model=Dict)
async def delete_structure(
    project_id: str,
    token: str = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    await verify_project_access(project_id, token, db)

    result = await db.execute(
        select(ProjectViralStructure).where(ProjectViralStructure.project_id == project_id)
        )
    structure = result.scalar_one_or_none()

    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No viral structure found"
        )

    await db.delete(structure)
    await db.commit()

    return {"message": "Viral structure deleted successfully"}


@router.get("/templates")
async def get_template_info():
    template_data = {
        "玄幻": {
            "name": "玄幻爆款结构",
            "description": "适用于玄幻小说的经典结构",
            "key_nodes": [
                {
                    "node_id": "volume1",
                    "name": "开篇世界",
                    "description": "介绍世界观、力量体系和主角背景",
                    "position_percentage": 5,
                    "writing_guidelines": [
                        "建立完整的世界观和力量体系",
                        "展示主角的核心特征和能力",
                        "引出主线冲突和核心设定"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter1",
                    "name": "黄金三章",
                    "description": "三章节奏紧凑,快速抓住读者眼球",
                    "position_percentage": 15,
                    "writing_guidelines": [
                        "第一章必须有强烈的冲突或悬念",
                        "第三章解决开篇提出的冲突",
                        "建立主角的核心动机和目标",
                        "完成第一个小高潮"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter10",
                    "name": "小高潮1",
                    "description": "每5-10章出现一次小高潮",
                    "position_percentage": 25,
                    "writing_guidelines": [
                        "冲突升级或情节转折",
                        "推动故事进入新阶段",
                        "提高紧张感"
                    ],
                    "is_critical": False
                },
                {
                    "node_id": "chapter20",
                    "name": "大高潮",
                    "description": "全书最高潮部分,情感爆发",
                    "position_percentage": 50,
                    "writing_guidelines": [
                        "情感爆发和人物成长",
                        "升华主题和人物关系",
                        "所有伏笔收回",
                        "为结局做铺垫"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter40",
                    "name": "结局",
                    "description": "收束全书伏笔,解决所有主线",
                    "position_percentage": 90,
                    "writing_guidelines": [
                        "情感爆发和人物弧光",
                        "主角完成成长",
                        "伏笔回扣解释所有疑问",
                        "留下深刻印象"
                    ],
                    "is_critical": True
                }
            ]
        },
        "都市": {
            "name": "都市爆款结构",
            "description": "适用于都市言情小说的结构",
            "key_nodes": [
                {
                    "node_id": "volume1",
                    "name": "开篇相遇",
                    "description": "男女主相遇,建立人物关系",
                    "position_percentage": 5,
                    "writing_guidelines": [
                        "制造浪漫邂逅或冲突",
                        "展现主角的性格和魅力",
                        "引出情感线索"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter5",
                    "name": "情感升温",
                    "description": "感情线升温,推进关系发展",
                    "position_percentage": 15,
                    "writing_guidelines": [
                        "加深情感冲突",
                        "制造第一次亲密度/接吻等情节",
                        "强化人物化学反应"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter10",
                    "name": "小高潮1",
                    "description": "关系转折或情感爆发",
                    "position_percentage": 25,
                    "writing_guidelines": [
                        "情感线重大转折",
                        "推进到冲突或解决",
                        "制造第一次矛盾"
                    ],
                    "is_critical": False
                },
                {
                    "node_id": "chapter20",
                    "name": "冲突解决",
                    "description": "前10章冲突的结果",
                    "position_percentage": 40,
                    "writing_guidelines":
                        "揭示真相,解除误会",
                        "重新调整人物关系",
                        "为后续情节做铺垫"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter40",
                    "name": "情感爆发",
                    "description": "情感达到顶点,人物完成成长",
                    "position_percentage": 50,
                    "writing_guidelines":
                        "情感线高潮点",
                        "人物关系升华",
                        "为结局情感爆发做铺垫"
                    ],
                    "is_critical": False
                }
            ]
        },
        "言情": {
            "name": "言情爆款结构",
            "description": "适用于言情小说的经典结构",
            "key_nodes": [
                {
                    "node_id": "volume1",
                    "name": "开篇背景",
                    "description": "铺垫女主背景和情感基调",
                    "position_percentage": 5,
                    "writing_guidelines": [
                        "引入女主的身世和性格",
                        "建立与男主的初步关系",
                        "营造浪漫氛围"
                    ],
                    "is_critical": False
                },
                {
                    "node_id": "chapter5",
                    "name": "初遇心动",
                    "description": "男女初遇,感情萌芽",
                    "position_percentage": 15,
                    "writing_guidelines":
                        "创造心动时刻",
                        "描写细腻的心理活动",
                        "避免俗套桥段"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter15",
                    "name": "感情升温",
                    "description": "感情线升温",
                    "position_percentage": 25,
                    "writing_guidelines":
                        "加深情感交流",
                        "推进关系发展",
                        "强化化学反应"
                    ],
                    "is_critical": False
                },
                {
                    "node_id": "chapter20",
                    "name": "第一次冲突",
                    "description: "出现情感误会或外部障碍",
                    "position_percentage": 40,
                    "writing_guidelines":
                        "制造第一次情感冲突",
                        "建立剧情冲突",
                        "强化戏剧张力"
                    ],
                    "is_critical": False
                },
                {
                    "node_id": "chapter30",
                    "name": "冲突解决",
                    "description": "前10章冲突的结果",
                    "position_percentage": 60,
                    "writing_guidelines": [
                        "消除误会并和解",
                        "加深感情连结"
                        "为感情升温做铺垫"
                    ],
                    "is_critical": False
                },
                {
                    "node_id": "chapter40",
                    "name": "大结局",
                    "description": 情感爆发,关系升华",
                    "position_percentage": 80,
                    "writing_guidelines": [
                        "情感线高潮点",
                        "人物弧光圆满",
                        "留下深刻印象",
                        "为系列结局做铺垫"
                    ],
                    "is_critical": True
                }
            ]
        },
        "悬疑": {
            "name": "悬疑爆款结构",
            "description": "适用于悬疑小说的紧凑节奏和反转",
            "key_nodes": [
                {
                    "node_id": "volume1",
                    "name": "开篇悬念",
                    "description": "设置核心悬念和世界观",
                    "position_percentage": 5,
                    "writing_guidelines":
                        "引入神秘事件",
                        "建立未知威胁",
                        "保持信息保密"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter5",
                    "name": "线索铺垫",
                    "description": "埋设伏笔和线索",
                    "position_percentage": 10,
                    "writing_guidelines": [
                        "为后续反转做铺垫",
                        "隐藏真实答案",
                        "保持神秘氛围"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter10",
                    "name": "第一次反转",
                    "description": "揭示部分真相",
                    "position_percentage": 25,
                    "writing_guidelines":
                        "制造第一次小反转",
                        "推进剧情发展",
                        "保持逻辑自洽"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter20",
                    "name": "高潮",
                    "description: "揭示核心真相,达到情绪顶点",
                    "position_percentage": 50,
                    "writing_guidelines:
                        "情感爆发和危机升级",
                        "推进到危机顶点",
                        "增加紧张感"
                    ],
                    "is_critical": True
                },
                {
                    "node_id": "chapter30",
                    "name": "降低紧张",
                    "description": "缓解紧张感,调整节奏",
                    "position_percentage": 70,
                    "writing_guidelines":
                        "为后续小高潮做铺垫",
                        "保持悬疑氛围"
                    ],
                    "is_critical": False
                },
                {
                    "node_id": "chapter40",
                    "name": "最终反转",
                    "description": "揭示全部真相,解决核心冲突",
                    "position_percentage": 90,
                    "writing_guidelines":
                        "逻辑自洽地完成",
                        "收束所有伏笔"
                        "为结局做铺垫"
                    ],
                    "is_critical": True
                }
            ]
        }
    }
}


router.include_router(router, prefix="/api/viral-structures", tags=["Viral Structures"])
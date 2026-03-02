"""测试章节API"""
import pytest
import json
from httpx import AsyncClient, ASGITransport, status
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models.models import Chapter, Project


@pytest.fixture
async def db_session():
    """数据库会话fixture"""
    engine = create_async_engine("sqlite+aios:///:memory:")
    Base.metadata.create_all(bind=engine)
    async_session_maker = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

    async for session in async_session_maker():
        yield session


@pytest.mark.asyncio
async def test_create_chapter_success(db_session):
    async with db_session() as db:
        project = Project(
            id="test-project-id",
            user_id="test-user-id",
            title="Test Chapter",
            genre="玄幻",
            target_word_count=80000,
            current_word_count=0
        )
        db.add(project)
        await db.commit()

        response = await client.post(
            "http://localhost:8000/api/projects/test-project-id/chapters",
            json={
                "title": "Test Chapter",
                "outline_node_id": "test-node-id",
                "content": "This is test content"
            }
        )

    assert response.status_code == 200
    data = response.json()
        assert data["id"] == "test-chapter-id"
        assert data["title"] == "Test Chapter"
        assert data["status"] == "draft"
        assert data["word_count"] == len("This is test content")

        await db.delete(project)


@pytest.mark.asyncio
async def test_get_chapters(db_session):
    async with db_session() as db:
        project = Project(
            id="test-project-id",
            user_id="test-user-id",
            title="Test Novel",
            genre="玄幻",
            target_word_count=80000,
            current_word_count=0
        )
        db.add(project)

        chapter1 = Chapter(
            id="test-chapter-1",
            project_id="test-project-id",
            title="Chapter 1",
            content="Content 1",
            word_count=2000,
            status="draft"
        )
        chapter2 = Chapter(
            id="test-chapter-2",
            project_id="test-project-id",
            title="Chapter 2",
            content="Content 2",
            word_count=3000,
            status="completed"
        )
        db.add(chapter1)
        db.add(chapter2)
        await db.commit()

        response = await client.get("http://localhost:8000/api/projects/test-project-id/chapters")
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        assert data[0]["id"] == "test-chapter-1"
        assert data[1]["id"] == "test-chapter-2"


@pytest.mark.asyncio
async def test_update_chapter(db_session):
    async with db_session() as db:
        project = Project(
            id="test-project-id",
            user_id="test-user-id",
            title="Test Novel",
            genre="玄幻",
            target_word_count=80000,
            current_word_count=0
        )
        db.add(project)

        chapter = Chapter(
            id="test-chapter-1",
            project_id="test-project-id",
            title="Chapter 1",
            content="Content 1",
            word_count=2000,
            status="draft"
        )
        db.add(chapter)
        await db.commit()

        response = await client.put(
            f"http://localhost:8000/api/projects/test-project-id/chapters/test-chapter-1",
            json={
                "title": "Updated Chapter 1"
            }
        )

        assert response.status_code == 200
    data = response.json()
        assert data["title"] == "Updated Chapter 1"
        await db.delete(project)


@pytest.mark.asyncio
async def test_delete_chapter(db_session):
    async with db_session() as db:
        project = Project(
            id="test-project-id",
            user_id="test-user-id",
            title="Test Novel",
            genre="玄幻",
            target_word_count=80000,
            current_word_count=0
        )
        db.add(project)

        chapter = Chapter(
            id="test-chapter-1",
            project_id="test-project-id",
            title="Chapter 1",
            content="Content 1",
            word_count=2000,
            status="draft"
        )
        db.add(chapter)
        await db.commit()

        response = await client.delete(
            f"http://localhost:8000/api/projects/test-project-id/chapters/test-chapter-1"
        )

    assert response.status_code == 200
    await db.delete(project)


@pytest.mark.asyncio
async def test_ai_generate_chapter(db_session):
    async with db_session() as db:
        project = Project(
            id="test-project-id",
            user_id="test-user-id",
            title="Test Novel",
            genre="玄幻",
            target_word_count=80000,
            current_word_count=0
        )
        db.add(project)

        chapter = Chapter(
            id="test-chapter-1",
            project_id="test-project-id",
            title="Chapter 1",
            content="Content 1",
            word_count=2000,
            status="draft"
        )
        db.add(chapter)
        await db.commit()

        response = await client.post(
            f"http://localhost:8000/api/projects/test-project-id/chapters/test-chapter-1/generate",
            json={
                "style_hints": ["epic", "engaging"],
                "reduce_ai_flavor": True,
                "versions": 3
            }
        )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    assert all("version" in v for v in data)
    assert len(data[0]["content"]) > 0


@pytest.mark.asyncio
async def test_autosave_chapter(db_session):
    async with db_session() as db:
        project = Project(
            id="test-project-id",
            user_id="test-user-id",
            title="Test Novel",
            genre="玄幻",
            target_word_count=80000,
            current_word_count=0
        )
        db.add(project)

        chapter = Chapter(
            id="test-chapter-1",
            project_id="test-project-id",
            title="Chapter 1",
            content="Content 1",
            word_count=2000,
            status="draft"
        )
        db.add(chapter)
        await db.commit()

        response = await client.post(
            f"http://localhost:8000/api/projects/test-project-id/chapters/autosave",
            json={
                "content": "Auto-saved content"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Auto-saved successfully"

"""测试认证API"""
import pytest
import json
from httpx import AsyncClient, ASGITransport, status
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models.models import User


@pytest.mark.asyncio
async def test_register_success(db_session):
    async with db_session() as db:
        response = await client.post(
            "http://localhost:8000/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data
        assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session):
    async with db_session() as db:
        await client.post(
            "http://localhost:8000/api/auth/register",
            json={
                "username": "testuser2",
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_login_success(db_session):
    async with db_session() as db:
        response = await client.post(
            "http://localhost:8000/api/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(db_session):
    async with db_session() as db:
        response = await client.post(
            "http://localhost:8000/api/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpass"
            }
        )
        assert response.status_code == 401


@pytest.fixture
async def client():
    base_url = "http://localhost:8000"
    transport = ASGITransport(app=AsyncClient, client=base_url)
    return AsyncClient(transport=transport)


@pytest.mark.asyncio
async def test_project_crud_operations(client, db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        created_at="2026-01-01T00:00:00"
    )
    db.add(user)

    await db.commit()

    project = Project(
        user_id=user.id,
        title="Test Novel",
        genre="玄幻",
        target_word_count=80000,
        current_word_count=0
    )
    db.add(project)

    await db.commit()

    project_id = str(project.id)

    response = await client.post(
        f"http://localhost:8000/api/projects",
        json={
            "title": "Test Novel",
            "genre": "玄幻",
            "target_word_count": 80000
        },
        headers={"Authorization": f"Bearer fake_token_for_{user.username}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Novel"
    await db.delete(project)
    await db.commit()


@pytest.mark.asyncio
async def test_api_not_found(client):
    response = await client.get("http://localhost:8000/api/projects/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_character_operations(client, db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        created_at="2026-01-01T00:00:00"
    )
    db.add(user)
    await db.commit()

    project = Project(
        user_id=user.id,
        title="Test Novel",
        genre="玄幻",
        target_word_count=80000,
        current_word_count=0
    )
    db.add(project)
    await db.commit()

    project_id = str(project.id)

    character = Character(
        project_id=project_id,
        name="Test Hero",
        age=25,
        personality=["勇敢", "正义"],
        appearance="英俊的青年男子",
        background="出身平凡,自幼习武艺"
    )
    db.add(character)
    await db.commit()

    response = await client.post(
        f"http://localhost:8000/api/projects/{project_id}/characters",
        json={
            "name": "Test Hero"
        "age": 25,
            "personality": ["勇敢", "正义"]
        },
        headers={"Authorization": f"Bearer fake_token_for_{user.username}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Hero"

    await db.delete(character)
    await db.commit()

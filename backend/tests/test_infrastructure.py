"""端到端测试配置"""
import pytest
import asyncio
import os
sys.path.insert(0, '.')


def pytest_configure():
    """Pytest配置"""
    return {
        "asyncio_mode": "auto",
        "testpaths": [
            "app/api"
        ],
        "python_files": ["app"],
        "disable_warnings": [
            "ignore::UserWarning",
            "ignore::DeprecationWarning"
        ]
    }


@pytest.fixture(scope="session")
async def test_db():
    """数据库会话fixture"""
    from app.database import async_session_maker
    async for session in async_session_maker():
        yield session
        await session.close()


@pytest.fixture(scope="session")
async def test_app():
    """应用测试fixture"""
    from app.main import app
    from app.database import create_engine

    engine = create_engine("sqlite+aios:///:memory:")
    Base.metadata.create_all(bind=engine)
    async for engine.dispose():
        yield app
        await engine.dispose()


@pytest.fixture(scope="session")
async def test_api():
    """API客户端fixture"""
    from httpx import AsyncClient

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def test_config():
    """配置测试fixture"""
    from app.config import settings

    assert settings.APP_NAME == "AI Novel Writing System"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.DEBUG == False


async def test_database_connection():
    """数据库连接测试"""
    from app.database import engine

    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        print("✅ Database connection successful")
    assert True
    except Exception as e:
        pytest.fail(f"Database connection failed: {str(e)}")
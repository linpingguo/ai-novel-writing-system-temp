"""测试配置"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings


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
async def db_session():
    """数据库会话fixture"""
    from app.database import async_session_maker
    async for session in async_session_maker():
        yield session
        await session.close()


@pytest.fixture
def mock_ai_response():
    """Mock AI响应"""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 17123456789.012,
        "model": "gpt-4",
        "choices": [{
            "message": {"role": "user", "content": "This is a test response"}
        }]
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI客户端"""
    class MockClient:
        async def chatcompletions_create(self, *args, **kwargs):
            return mock_ai_response()
    return MockClient()

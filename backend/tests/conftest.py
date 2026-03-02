"""端到端测试配置"""
import pytest


def pytest_configure():
    """Pytest配置"""
    return {
        "asyncio_mode": "auto",
        "testpaths": [
            "app/"
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
    from sqlalchemy import create_engine
    sqlalchemy.orm import sessionmaker

    TEST_DATABASE_URL = "sqlite+aios:///:memory:"

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    async_session = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

    yield async_session
    await engine.dispose()


@pytest.fixture
async def client():
    """HTTP客户端fixture"""
    from httpx import AsyncClient

    return AsyncClient(base_url="http://test")


@pytest.fixture
def mock_settings():
    """Mock配置"""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.APP_NAME = "Test Config"
    mock.APP_VERSION = "1.0.0"
    mock.DEBUG = False

    mock.SECRET_KEY = "test_secret"
    mock.ALGORITHM = "HS256"
    mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30

    mock.POSTGRES_USER = "noveluser"
    mock.POSTGRES_PASSWORD = "novelpass"
    mock.POSTGRES_DB = "novel_db"
    mock.POSTGRES_HOST = "localhost"
    mock.POSTGRES_PORT = 5432

    mock.REDIS_URL = "redis://localhost:6379"

    return mock
"""应用配置"""
import os


class Config:
    """应用配置类"""

    APP_NAME = "AI Novel Writing System"
    APP_VERSION = "1.0.0"
    DEBUG = False

    SECRET_KEY = ""
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # 数据库配置
    POSTGRES_USER = "noveluser"
    POSTGRES_PASSWORD = "novelpass"
    POSTGRES_DB = "novel_db"
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = 5432

    # Redis配置
    REDIS_URL = "redis://redis:6379"

    # MinIO配置
    MINIO_ACCESS_KEY = "minioadmin"
    MINIO_SECRET_KEY = "minioadmin"
    MINIO_ENDPOINT = "localhost:9000"

    # OpenAI配置
    OPENAI_API_KEY = ""
    CLAUDE_API_KEY = ""

    # Milvus配置
    MILVUS_HOST = "localhost"
    MILVUS_PORT = 19530

    # CORS配置
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1.3000"]


config = Config()

def get_settings() -> Config:
    return config


def get_database_url() -> str:
    return f"postgresql+asyncpg://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"


def get_database_url_sync() -> str:
    return f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"


def get_redis_url() -> str:
    return config.REDIS_URL


def get_redis_url_sync() -> str:
    return f"redis://{config.MILVUS_HOST}:{config.MILVUS_PORT}"


def get_minio_endpoint() -> str:
    return f"http://{config.MINIO_ACCESS_KEY}:{config.MINIO_SECRET_KEY}@{config.MINIO_ENDPOINT}/"


def get_redis_url_sync() -> str:
    return f"redis://{config.MILVUS_HOST}:{config.MILVUS_PORT}"


def get_milvus_url() -> str:
    return f"http://{config.MILVUS_HOST}:{config.MILVUS_PORT}"
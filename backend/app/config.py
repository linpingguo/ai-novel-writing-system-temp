"""应用配置"""
from typing import Optional


class Config:
    """应用配置类"""
    APP_NAME: str = "AI Novel Writing System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    POSTGRES_USER: str = "noveluser"
    POSTGRES_PASSWORD: str = "novelpass"
    POSTGRES_DB: str = "novel_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    REDIS_URL: str = "redis://redis:6379"

    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_ENDPOINT: str = "localhost:9000"

    OPENAI_API_KEY: str = ""
    CLAUDE_API_KEY: str = ""

    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0:3000"]

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def database_url_sync(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


config = Config()
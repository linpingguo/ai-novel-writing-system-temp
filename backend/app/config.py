"""应用配置"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='allow'
    )

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

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def database_url_sync(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def redis_url_sync(self) -> str:
        return f"redis://{self.MILVUS_HOST}:{self.MILVUS_PORT}"

    @property
    def minio_url(self) -> str:
        return f"http://{self.MINIO_ACCESS_KEY}:{self.MINIO_SECRET_KEY}@{self.MINIO_ENDPOINT}"

    @property
    def milvus_url(self) -> str:
        return f"http://{self.MILVUS_HOST}:{self.MILVUS_PORT}"


config = Config()

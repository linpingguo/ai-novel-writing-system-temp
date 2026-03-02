import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    app_name: str = "AI Novel Writing System"
    app_version: str = "1.0.0"
    debug: bool = True

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    redis_url: str = "redis://redis:6379"

    minio_access_key: str
    minio_secret_key: str
    minio_endpoint: str = "localhost:9000"

    openai_api_key: str = ""
    claude_api_key: str = ""

    milvus_host: str = "localhost"
    milvus_port: int = 19530

    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()

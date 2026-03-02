from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.database import Base
import asyncio


def run_migrations():
    from alembic import context

    DATABASE_URL = "postgresql://noveluser:novelpass@localhost:5432/novel_db"

    engine = create_async_engine(DATABASE_URL, echo=True)

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_db())


if __name__ == "__main__":
    run_migrations()

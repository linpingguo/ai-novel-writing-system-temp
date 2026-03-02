from app.services.redis_client import redis_client
from app.services.vector_db import vector_db_client


async def init_cache():
    try:
        await redis_client.client.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis connection failed: {e}")


async def init_vector_db():
    try:
        await vector_db_client.connect()

        await vector_db_client.create_collection("characters_collection", dimension=1536)
        await vector_db_client.create_collection("style_collection", dimension=1536)
        await vector_db_client.create_collection("viral_cases_collection", dimension=1536)

        print("Vector database initialized successfully")
    except Exception as e:
        print(f"Vector database initialization failed: {e}")


async def cleanup_cache():
    await redis_client.close()
    await vector_db_client.disconnect()
    print("Cache and vector database cleaned up")

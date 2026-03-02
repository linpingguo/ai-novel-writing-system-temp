import redis.asyncio as redis
from typing import Optional, Any
import json
from app.config import settings


class RedisClient:
    def __init__(self):
        self.client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def get(self, key: str) -> Optional[Any]:
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, expire: int = None):
        await self.client.set(key, json.dumps(value), ex=expire)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0

    async def close(self):
        await self.client.close()


redis_client = RedisClient()

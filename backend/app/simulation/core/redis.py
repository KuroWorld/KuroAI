"""Redis connection and utilities."""
import json
from typing import Optional, Any
import aioredis
from pydantic import BaseModel

# Redis connection instance
redis: Optional[aioredis.Redis] = None

async def init_redis(host: str = "redis", port: int = 6379) -> None:
    """Initialize Redis connection."""
    global redis
    if not redis:
        redis = aioredis.from_url(f"redis://{host}:{port}")
        
async def close_redis() -> None:
    """Close Redis connection."""
    global redis
    if redis:
        await redis.close()
        redis = None

async def get_redis() -> aioredis.Redis:
    """Get Redis connection."""
    if not redis:
        await init_redis()
    return redis

class RedisModel(BaseModel):
    """Base model for Redis-stored models."""
    
    @property
    def redis_key(self) -> str:
        """Get Redis key for this model instance."""
        raise NotImplementedError
        
    async def save(self) -> None:
        """Save model to Redis."""
        r = await get_redis()
        await r.set(self.redis_key, self.json())
        
    @classmethod
    async def get(cls, key: str) -> Optional['RedisModel']:
        """Get model from Redis."""
        r = await get_redis()
        data = await r.get(key)
        if data:
            return cls.parse_raw(data)
        return None

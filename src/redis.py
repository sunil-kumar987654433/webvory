
from src.config import Config
import redis.asyncio as aioredis


redis_client = aioredis.Redis(
    host=Config.REDIS_HOST, 
    port=Config.REDIS_PORT, 
    decode_responses=True,
    db=0,
    socket_connect_timeout=5,
    retry_on_timeout=True
    )
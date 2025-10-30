import redis
from core.settings import get_settings

settings = get_settings()

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
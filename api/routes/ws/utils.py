import os
import json
import redis.asyncio as redis
from fastapi import WebSocket
from typing import Dict, List
from core.settings import get_settings

settings = get_settings()

active_connections: Dict[int, List[WebSocket]] = {}
redis_client: redis.Redis | None = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_url = settings.redis_url
        redis_client = redis.from_url(redis_url, decode_responses=True)
    return redis_client


async def connect_job(websocket: WebSocket, job_id: int):
    await websocket.accept()
    active_connections.setdefault(job_id, []).append(websocket)


async def disconnect_job(websocket: WebSocket, job_id: int):
    active_connections[job_id].remove(websocket)
    if not active_connections[job_id]:
        del active_connections[job_id]


async def notify_job(job_id: int, message: dict):
    r = await get_redis()
    await r.publish("jobs_channel", json.dumps({"job_id": job_id, "message": message}))


async def broadcast_listener():
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe("jobs_channel")

    async for msg in pubsub.listen():
        if msg["type"] == "message":
            data = json.loads(msg["data"])
            job_id = data["job_id"]
            message = data["message"]
            for ws in active_connections.get(job_id, []):
                try:
                    await ws.send_json(message)
                except Exception:
                    await disconnect_job(ws, job_id)


from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from routes.ws.utils import (
    connect_job,
    disconnect_job,
)

router = APIRouter(tags=["ws"])

@router.websocket("/jobs/{job_id}")
async def job_updates(websocket: WebSocket, job_id: int):
    await connect_job(websocket, job_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await disconnect_job(websocket, job_id)
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import manager

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(ws: WebSocket, user_id: int):
    await manager.connect(user_id, ws)
    try:
        while True:
            await ws.receive_text() 
    except WebSocketDisconnect:
        manager.disconnect(user_id)
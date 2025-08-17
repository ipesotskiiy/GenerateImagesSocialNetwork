from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import manager

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def ws_endpoint(ws: WebSocket, user_id: int):
    await manager.connect(user_id, ws)
    await manager.send_to(user_id, {"type": "welcome", "user_id": user_id})
    try:
        while True:
            await ws.receive_text()  # или receive_json()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

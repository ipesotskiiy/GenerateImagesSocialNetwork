from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from .manager import manager
from .auth_ws import authenticate_ws

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def ws_endpoint(ws: WebSocket, user_id: int):
    if not await authenticate_ws(ws, user_id):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user_id, ws)
    await manager.send_to(user_id, {"type": "welcome", "user_id": user_id})

    try:
        while True:
            await ws.receive_text()  # или receive_json()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

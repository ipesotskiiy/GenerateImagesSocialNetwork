from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from main import app
from message.crud import create_message, update_message, delete_message
from settings import get_session

router = APIRouter()
active_connections: dict[int, WebSocket] = {}

@app.websocket("ws/{user_id}")
async def websocket_info(websocket: WebSocket, user_id: int, session: AsyncSession = Depends(get_session)):
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "send":
                recipient_id = data["recipient_id"]
                content = data["content"]

                message = await create_message(session, user_id, recipient_id, content)
                recipient_ws = active_connections.get(recipient_id)
                if recipient_ws:
                    await recipient_ws.send_json({
                        "type": "new",
                        "message": {
                            "id": message.id,
                            "sender_id": message.sender_id,
                            "recipient_id": message.recipient_id,
                            "content": message.content,
                            "timestamp": str(message.timestamp),
                        }
                    })


                elif action == "edit":
                    message_id = data["message_id"]
                    new_content = data["new_content"]

                    updated_message = await update_message(session, message_id, new_content)
                    if updated_message:
                        for uid in [updated_message.sender_id, updated_message.recipient_id]:
                            ws = active_connections.get(uid)
                            if ws:
                                await ws.send_json({
                                    "type": "edit",
                                    "message_id": message_id,
                                    "new_content": new_content
                                })

                elif action == "delete":
                    message_id = data["message_id"]
                    success = await delete_message(session, message_id)
                    if success:
                        for uid in [data["sender_id"], data["recipient_id"]]:
                            ws = active_connections.get(uid)
                            if ws:
                                await ws.send_json({
                                    "type": "delete",
                                    "message_id": message_id
                                })

    except WebSocketDisconnect:
        active_connections.pop(user_id, None)



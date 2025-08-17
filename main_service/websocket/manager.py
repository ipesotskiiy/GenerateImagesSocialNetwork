from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self) -> None:
        self.active: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active[user_id] = ws

    def disconnect(self, user_id: int):
        self.active.pop(user_id, None)

    async def send_to(self, user_id: int, payload: dict):
        ws = self.active.get(user_id)
        if ws:
            await ws.send_json(payload)

    async def send_many(self, user_ids: list[int], payload: dict):
        for uid in user_ids:
            await self.send_to(uid, payload)

manager = ConnectionManager()

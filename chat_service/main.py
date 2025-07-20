from fastapi import FastAPI

from message.router import router as message_router
from websocket.router import router as websocket_router

app = FastAPI(
    title="Team Social Network Chat Service"
)

app.include_router(message_router)
app.include(websocket_router)

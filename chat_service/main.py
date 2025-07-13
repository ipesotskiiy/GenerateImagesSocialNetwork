from fastapi import FastAPI

from message.router import router as message_router

app = FastAPI(
    title="Team Social Network Chat Service"
)

app.include_router(message_router)


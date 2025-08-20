import asyncio

from fastapi import FastAPI

from message.router import router as message_router
from publisher import broker
from rabbit_consumer import start_consumer
from websocket.router import router as websocket_router

app = FastAPI(
    title="Team Social Network Chat Service"
)

app.include_router(message_router)
app.include_router(websocket_router)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(start_consumer())

@app.on_event("startup")
async def startup():
    await broker.connect()   # одно подключение на всё приложение

@app.on_event("shutdown")
async def shutdown():
    await broker.close()

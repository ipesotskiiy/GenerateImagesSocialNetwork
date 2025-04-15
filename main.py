import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.auth import auth_backend
from auth.router import router as router_subscriptions
from auth.schemas import UserRead, UserCreate
from dependencies import fastapi_users
from logging_config import Logger
from posts.router import router as router_posts
from comments.router import router as router_comments
from settings import async_session_maker
from startup import create_seed_categories
from like_dislike.router import like_router as router_like, dislike_router as router_dislike
from communities.router import router as router_community

logger = Logger()

app = FastAPI(
    title="Team Social Network"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.register_global_exceprtion_handler(app)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth 🐺"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth 🐺"]
)

current_user = fastapi_users.current_user()

app.include_router(router_posts)
app.include_router(router_comments)
app.include_router(router_like)
app.include_router(router_dislike)
app.include_router(router_community)
app.include_router(router_subscriptions)

@app.on_event("startup")
async def on_startup():

    async with async_session_maker() as session:
        await create_seed_categories(session)


# TODO Перенести в settings.py
if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Имя модуля и объекта приложения
        host="127.0.0.1",  # Локальный хост
        port=8001,  # Порт
        log_level="debug",  # Уровень логирования
        reload=True
    )

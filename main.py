import uvicorn
from fastapi import FastAPI, Depends

from auth.auth import auth_backend
from auth.models import User
from auth.schemas import UserRead, UserCreate
from dependencies import fastapi_users
from logging_config import Logger
from posts.router import router as router_posts
from comments.router import router as router_comments
from settings import async_session_maker
from startup import create_seed_categories
from like_dislike.router import like_router as router_like, dislike_router as router_dislike

logger = Logger()

app = FastAPI(
    title="Team Social Network"
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


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.username}"


@app.on_event("startup")
async def on_startup():

    async with async_session_maker() as session:
        await create_seed_categories(session)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Имя модуля и объекта приложения
        host="127.0.0.1",  # Локальный хост
        port=8001,  # Порт
        log_level="debug",  # Уровень логирования
        reload=True
    )

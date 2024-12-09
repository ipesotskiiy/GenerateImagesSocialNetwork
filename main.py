import uvicorn
from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers

from auth.auth import auth_backend
from auth.manager import get_user_manager
from auth.models import User
from auth.schemas import UserRead, UserCreate
from dependencies import fastapi_users
from posts.router import router as router_posts
from logging_config import Logger

logger = Logger()

app = FastAPI(
    title="Team Social Network"
)

logger.register_global_exceprtion_handler(app)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

current_user = fastapi_users.current_user()

app.include_router(router_posts)


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.username}"


if __name__ == "__main__":
    uvicorn.run(
        "main:app",  # Имя модуля и объекта приложения
        host="127.0.0.1",  # Локальный хост
        port=8001,  # Порт
        log_level="debug",  # Уровень логирования
        reload=True  # Включение режима отладки с перезагрузкой
    )

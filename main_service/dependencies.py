from fastapi_users import FastAPIUsers

from auth.manager import get_user_manager
from auth.auth import auth_backend
from auth.models import User

# Создаем FastAPIUsers
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Зависимость для получения текущего пользователя
current_user = fastapi_users.current_user()

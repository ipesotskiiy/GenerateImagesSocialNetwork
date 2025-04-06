from typing import Optional

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.password import PasswordHelper

from auth.models import User
from auth.utils import get_user_db

SECRET = "SECRET"


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def __init__(self, user_db):
        super().__init__(user_db)
        self.password_helper = PasswordHelper()  # Создаем экземпляр PasswordHelper

    # Переопределяем authenticate, чтобы логиниться по username
    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> Optional[User]:
        user = await self.user_db.get_by_username(credentials.username)
        if user is None:
            return None

        # Проверяем пароль через метод verify_and_update
        is_valid_password, _ = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not is_valid_password:
            return None

        if not user.is_active:
            return None

        return user

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

from fastapi_users.authentication import AuthenticationBackend, JWTStrategy

from settings import get_settings, bearer_transport


def get_jwt_strategy() -> JWTStrategy:
    settings = get_settings()
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

#TODO добавить в settings.py
SECRET = "SECRET"

#TODO путь в settings.py
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

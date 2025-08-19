import os
from typing import Optional

from fastapi import WebSocket
from jose import jwt, ExpiredSignatureError, JWTError
from jose.exceptions import JWTClaimsError

def _get_secret() -> str:
    env_secret = os.getenv("JWT_SECRET") or os.getenv("SECRET")
    if env_secret:
        return env_secret

    try:
        from settings import get_settings
        s = get_settings()
        sec = getattr(s, "secret", None)
        # Pydantic SecretStr?
        if hasattr(sec, "get_secret_value"):
            return sec.get_secret_value()
        if sec is not None:
            return str(sec)
    except Exception:
        pass

    return "dev-secret"

SECRET = _get_secret()
ALG = "HS256"
AUD = "fastapi-users:auth"
ISS: Optional[str] = None

def _extract_token(ws: WebSocket) -> Optional[str]:
    token = ws.query_params.get("token")
    if token:
        return token

    auth = ws.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth[7:]

    cookiet_token = ws.cookies.get("fastapiusersauth")
    if cookiet_token:
        return cookiet_token
    return None

def validate_and_get_sub(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(
            token,
            SECRET,
            algorithms=[ALG],
            audience=AUD,
            issuer=ISS if ISS else None,
            options={"require_sub": True, "require_exp": True},
        )
        return int(payload["sub"])
    except (ExpiredSignatureError, JWTClaimsError, JWTError, KeyError, ValueError):
        return None


async def authenticate_ws(ws: WebSocket, expected_user_id: int) -> bool:
    token = _extract_token(ws)
    if not token:
        return False

    sub = validate_and_get_sub(token)
    if sub is None:
        return False

    return sub == int(expected_user_id)



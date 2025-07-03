import uuid
from datetime import datetime, timedelta, timezone
from typing import Union

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from app.config import settings
from app.schemas.auth import UserToken


# Кэш ключей — читаем один раз при импорте
_PRIVATE_KEY: str = settings.auth_jwt.private_key_path.read_text()
_PUBLIC_KEY: str = settings.auth_jwt.public_key_path.read_text()
_ALGORITHM: str = settings.auth_jwt.algorithm
_ACCESS_EXPIRE_MINUTES: int = settings.auth_jwt.access_token_expire_minutes


def encode_jwt(
    payload: dict,
    *,
    private_key: str = _PRIVATE_KEY,
    algorithm: str = _ALGORITHM,
    expire_minutes: int = _ACCESS_EXPIRE_MINUTES,
    expire_timedelta: Union[timedelta, None] = None,
) -> str:
    """
    Создаёт JWT‑токен. Обязательно наличие поля `sub` (ID пользователя).
    """
    if "sub" not in payload:
        raise ValueError("payload must contain 'sub' field")

    to_encode = payload.copy()
    to_encode["sub"] = str(to_encode["sub"])  # приводим к строке для совместимости

    now = datetime.now(timezone.utc)
    expire = now + (expire_timedelta or timedelta(minutes=expire_minutes))

    to_encode.update(exp=expire, iat=now)

    return jwt.encode(to_encode, private_key, algorithm=algorithm)


def decode_jwt(
    token: Union[str, bytes],
    *,
    public_key: str = _PUBLIC_KEY,
    algorithm: str = _ALGORITHM,
) -> dict:
    """
    Декодирует токен и верифицирует подпись и срок действия.
    """
    try:
        payload = jwt.decode(token, public_key, algorithms=[algorithm])
    except jwt.JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    if "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token: missing 'sub' claim")

    # гарантируем строковый тип sub
    payload["sub"] = str(payload["sub"])
    return payload


def hash_password(password: str, rounds: int = 12) -> str:
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_invite_token() -> str:
    return str(uuid.uuid4())


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> UserToken:
    """
    Декодирует токен из заголовка Authorization и возвращает модель UserToken.
    """
    payload = decode_jwt(credentials.credentials)

    is_active: bool = payload.get("is_active", True)
    if not is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    return UserToken(
        user_id=int(payload["sub"]),
        company_id=payload.get("company_id"),
        is_admin=payload.get("is_admin", False),
    )
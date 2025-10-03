from jose import jwt
from core.settings import get_settings
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

settings = get_settings()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = timedelta(minutes=settings.access_token_ttl_minutes),
):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    to_encode.update({
        "exp": expire,
        "iat": now,
    })

    return jwt.encode(
        claims=to_encode,
        key=settings.secret_key,
        algorithm=settings.auth_algorithm,
    )


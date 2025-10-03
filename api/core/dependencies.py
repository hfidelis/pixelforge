from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from core.db import get_db
from core.settings import get_settings

from models.user import User
from schemas.user import TokenData
from routes.auth import oauth2_scheme

settings = get_settings()


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token=token,
            key=settings.secret_key,
            algorithms=[settings.auth_algorithm]
        )

        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        token_data = TokenData(email=email)

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalars().one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from core.db import get_db
from core.settings import get_settings

from models.user import User
from schemas.user import UserCreate, UserRead, UserLogin, Token
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)

settings = get_settings()

router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/signin/form")


@router.post("/register", response_model=UserRead)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> UserRead:
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().one_or_none()

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email is already registered"
        )

    print("password type:", type(user.password))
    print("password repr:", repr(user.password))
    print("password bytes length:", len(user.password.encode("utf-8")))


    new_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> User | bool:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().one_or_none()

    if not user or not verify_password(password, user.password):
        return False

    return user


@router.post(
    "/signin",
    response_model=Token
)
async def signin(
    schema: UserLogin,
    db: Session = Depends(get_db)
):
    if not (user := await authenticate_user(db, schema.email, schema.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post(
    "/signin/form",
    response_model=Token,
)
async def signin_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print("form_data", form_data)
    if not (user := await authenticate_user(db, form_data.username, form_data.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


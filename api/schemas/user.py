from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"



class TokenData(BaseModel):
    email: str | None = None



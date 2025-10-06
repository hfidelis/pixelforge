from fastapi import Query
from pydantic import BaseModel
from typing import List, TypeVar, Generic

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Query(1, ge=1)
    size: int = Query(10, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    page: int
    size: int
    pages: int
    next_url: str | None
    prev_url: str | None
    results: List[T]
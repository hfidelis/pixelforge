from math import ceil
from fastapi import Request
from typing import TypeVar, Type
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.pagination import PaginatedResponse

T = TypeVar("T")


async def paginate(
    db: AsyncSession,
    model: Type[T],
    base_query=None,
    page: int = 1,
    size: int = 10,
    request: Request | None = None,
):
    if base_query is None:
        base_query = select(model)

    total = await db.scalar(
        select(func.count()).select_from(model).where(*base_query._where_criteria)
    )

    result = await db.execute(
        base_query.offset((page - 1) * size).limit(size)
    )

    pages = ceil(total / size) if total else 1

    items = result.scalars().all()

    next_url = None
    prev_url = None

    if request:
        if page < pages:
            next_url = str(request.url.include_query_params(page=page + 1, size=size))
        if page > 1:
            prev_url = str(request.url.include_query_params(page=page - 1, size=size))

    return PaginatedResponse(
        count=total,
        page=page,
        size=size,
        pages=pages,
        results=items,
        next_url=next_url,
        prev_url=prev_url,
    )


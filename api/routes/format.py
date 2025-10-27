from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from utils.dependencies import get_current_user

from schemas.job import (
    JobImageExtension,
)

router = APIRouter(tags=["format"])


@router.get(
    "/image",
    response_model=List[JobImageExtension],
)
async def get_image_formats(
    user=Depends(get_current_user),
) -> List[JobImageExtension]:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return JobImageExtension.list_values()


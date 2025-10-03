from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

from core.db import get_db
from core.dependencies import get_current_user

from schemas.user import UserRead

router = APIRouter(tags=["users"])


@router.get(
    "/me",
    response_model=UserRead,
)
async def get_own_profile(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> UserRead:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return user


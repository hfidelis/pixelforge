from typing import Optional
from datetime import datetime
from fastapi import UploadFile
from pydantic import BaseModel
from models.base import JobStatus


class JobCreate(BaseModel):
    file: UploadFile
    target_format: str


class JobRead(BaseModel):
    id: int
    filename: str
    input_path: str
    output_path: Optional[str]
    original_format: str
    target_format: str
    status: JobStatus
    created_at: datetime

    class Config:
        from_attributes = True


class JobStatusRead(BaseModel):
    id: int
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True


from enum import Enum
from fastapi import Form, File
from typing import Type
from typing import Optional
from datetime import datetime
from fastapi import UploadFile
from pydantic import BaseModel


class JobImageExtension(str, Enum):
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    BMP = "bmp"
    GIF = "gif"
    TIFF = "tiff"
    WEBP = "webp"


    @classmethod
    def has_value(cls, value: str) -> bool:
        return value.lower() in (fmt.value for fmt in cls)


    @classmethod
    def list_values(cls) -> list[str]:
        return [fmt.value for fmt in cls]


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class JobCreate(BaseModel):
    file: UploadFile
    target_format: JobImageExtension = Form(...)

    @classmethod
    def as_form(
        cls: Type["JobCreate"],
        file: UploadFile = File(...),
        target_format: JobImageExtension = Form(...),
    ) -> "JobCreate":
        return cls(file=file, target_format=target_format)


class JobRead(BaseModel):
    id: int
    filename: str
    input_path: str
    output_path: Optional[str]
    original_format: JobImageExtension
    target_format: JobImageExtension
    user_id: int
    status: JobStatus
    created_at: datetime

    class Config:
        from_attributes = True


class JobStatusRead(BaseModel):
    id: int
    status: JobStatus
    user_id: int
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True


class PresignedRedirectResponse(BaseModel):
    url: str
    filename: str


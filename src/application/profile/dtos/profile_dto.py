from datetime import datetime
from pydantic import BaseModel, Field


class CreateProfileDto(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, examples=["John"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["Doe"])


class UpdateProfileDto(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, examples=["John"])
    last_name: str = Field(..., min_length=1, max_length=100, examples=["Doe"])


class ProfileResponseDto(BaseModel):
    id: str
    first_name: str
    last_name: str
    creation_datetime: datetime
    modification_datetime: datetime | None = None

    class Config:
        from_attributes = True

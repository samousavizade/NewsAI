from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional


class CreateNewsSchema(BaseModel):
    title: str = Field(...)
    source: str = Field(...)
    date_published: datetime = Field(...)
    content: str = Field(...)
    tags: List[str] = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Breakthrough in AI Technology",
                "source": "TechNews",
                "date_published": "2024-07-09T14:48:00.000Z",
                "content": "A groundbreaking AI model has been developed...",
                "tags": ["AI", "Technology", "Innovation"]
            }
        }


class UpdateNewsSchema(BaseModel):
    title: Optional[str] = None
    source: Optional[str] = None
    date_published: Optional[datetime] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Breakthrough in AI Technology",
                "source": "TechNews Updated",
                "date_published": "2024-07-10T14:48:00.000Z",
                "content": "An updated groundbreaking AI model has been developed...",
                "tags": ["AI", "Technology", "Innovation", "Update"]
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
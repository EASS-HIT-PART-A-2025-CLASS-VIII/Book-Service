from pydantic import BaseModel, Field
from typing import Optional


class BookBase(BaseModel):
    """Base model for book data"""
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    genre: str = Field(..., min_length=1, max_length=50)
    rating: Optional[float] = Field(None, ge=0, le=10)


class BookCreate(BookBase):
    """Model for creating a new book"""
    pass


class Book(BookBase):
    """Model for book with ID"""
    id: int

    class Config:
        from_attributes = True
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict


class BookBase(BaseModel):
    """Base model for book data"""
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    genre: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    image_url: str = Field(..., min_length=1)


class BookCreate(BookBase):
    """Model for creating a new book"""
    pass


class Book(BookBase):
    """Model for book with ID and user interactions"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    average_rating: float = 0.0
    total_ratings: int = 0
    user_ratings: Dict[str, float] = {}  # {user_id: rating}
    favorites: List[str] = []  # [user_id1, user_id2, ...]
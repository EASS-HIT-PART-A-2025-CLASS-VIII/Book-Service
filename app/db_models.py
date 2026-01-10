from sqlalchemy import Column, Integer, String, Float, JSON, ARRAY
from app.database import Base


class BookDB(Base):
    """SQLAlchemy model for Book table"""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    genre = Column(String(50), nullable=False, index=True)
    description = Column(String(1000))
    image_url = Column(String, nullable=False)
    average_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    user_ratings = Column(JSON, default=dict)  # {user_id: rating}
    favorites = Column(JSON, default=list)  # [user_id1, user_id2, ...]
    borrowed_by = Column(JSON, default=list)  # [user_id1, user_id2, ...]
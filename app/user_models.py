from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class UserDB(Base):
    """SQLAlchemy model for User table"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # "user" or "admin"
    is_active = Column(Boolean, default=True)
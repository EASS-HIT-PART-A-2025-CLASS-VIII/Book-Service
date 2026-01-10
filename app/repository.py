from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update
from app.models import Book, BookCreate
from app.db_models import BookDB


class BookRepository:
    """
    Database storage for books using PostgreSQL.
    
    This repository provides CRUD operations for book management
    using SQLAlchemy ORM.
    """
    
    def __init__(self, db: Session):
        """Initialize the repository with database session."""
        self.db = db
    
    def create(self, book_data: BookCreate) -> Book:
        """Create a new book"""
        db_book = BookDB(
            title=book_data.title,
            author=book_data.author,
            genre=book_data.genre,
            description=book_data.description,
            image_url=book_data.image_url,
            average_rating=0.0,
            total_ratings=0,
            user_ratings={},
            favorites=[],
            borrowed_by=[]
        )
        # Don't set ID - let database auto-generate it
        
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        
        return self._to_book_model(db_book)
    
    def get_all(self) -> List[Book]:
        """
        Get all books.
        
        Returns:
            List[Book]: List of all books in the repository
        """
        db_books = self.db.query(BookDB).all()
        return [self._to_pydantic(db_book) for db_book in db_books]
    
    def get_by_id(self, book_id: int) -> Optional[Book]:
        """
        Get a book by ID.
        
        Args:
            book_id: The ID of the book to retrieve
            
        Returns:
            Optional[Book]: The book if found, None otherwise
        """
        db_book = self.db.query(BookDB).filter(BookDB.id == book_id).first()
        if not db_book:
            return None
        return self._to_pydantic(db_book)
    
    def update(self, book_id: int, book_data: BookCreate) -> Optional[Book]:
        """
        Update an existing book.
        
        Args:
            book_id: The ID of the book to update
            book_data: New book data
            
        Returns:
            Optional[Book]: The updated book if found, None otherwise
        """
        db_book = self.db.query(BookDB).filter(BookDB.id == book_id).first()
        if not db_book:
            return None
        
        db_book.title = book_data.title
        db_book.author = book_data.author
        db_book.genre = book_data.genre
        db_book.description = book_data.description
        db_book.image_url = book_data.image_url
        
        self.db.commit()
        self.db.refresh(db_book)
        
        return self._to_pydantic(db_book)
    
    def delete(self, book_id: int) -> bool:
        """
        Delete a book.
        
        Args:
            book_id: The ID of the book to delete
            
        Returns:
            bool: True if book was deleted, False if not found
        """
        db_book = self.db.query(BookDB).filter(BookDB.id == book_id).first()
        if not db_book:
            return False
        
        self.db.delete(db_book)
        self.db.commit()
        return True
    
    def rate_book(self, book_id: int, user_id: str, rating: float) -> Optional[Book]:
        """
        Rate a book.
        
        Args:
            book_id: The ID of the book to rate
            user_id: The user's ID
            rating: Rating value (0-10)
            
        Returns:
            Optional[Book]: The updated book if found, None otherwise
        """
        db_book = self.db.query(BookDB).filter(BookDB.id == book_id).first()
        if not db_book:
            return None
        
        # Update user rating - create new dict to force update
        user_ratings = dict(db_book.user_ratings) if db_book.user_ratings else {}
        user_ratings[user_id] = rating
        
        # Recalculate average
        if user_ratings:
            average_rating = sum(user_ratings.values()) / len(user_ratings)
            total_ratings = len(user_ratings)
        else:
            average_rating = 0.0
            total_ratings = 0
        
        # Use update statement to force JSON update
        self.db.execute(
            update(BookDB)
            .where(BookDB.id == book_id)
            .values(
                user_ratings=user_ratings,
                average_rating=average_rating,
                total_ratings=total_ratings
            )
        )
        
        self.db.commit()
        self.db.refresh(db_book)
        
        return self._to_pydantic(db_book)
    
    def toggle_favorite(self, book_id: int, user_id: str) -> Optional[Book]:
        """
        Toggle favorite status for a book.
        
        Args:
            book_id: The ID of the book
            user_id: The user's ID
            
        Returns:
            Optional[Book]: The updated book if found, None otherwise
        """
        db_book = self.db.query(BookDB).filter(BookDB.id == book_id).first()
        if not db_book:
            return None
        
        # Create new list to force update
        favorites = list(db_book.favorites) if db_book.favorites else []
        if user_id in favorites:
            favorites.remove(user_id)
        else:
            favorites.append(user_id)
        
        # Use update statement to force JSON update
        self.db.execute(
            update(BookDB)
            .where(BookDB.id == book_id)
            .values(favorites=favorites)
        )
        
        self.db.commit()
        self.db.refresh(db_book)
        
        return self._to_pydantic(db_book)
    
    def toggle_borrow(self, book_id: int, user_id: str) -> Optional[Book]:
        """
        Toggle borrow status for a book (add/remove from cart).
        
        Args:
            book_id: The ID of the book
            user_id: The user's ID
            
        Returns:
            Optional[Book]: The updated book if found, None otherwise
        """
        db_book = self.db.query(BookDB).filter(BookDB.id == book_id).first()
        if not db_book:
            return None
        
        # Create new list to force update
        borrowed_by = list(db_book.borrowed_by) if db_book.borrowed_by else []
        if user_id in borrowed_by:
            borrowed_by.remove(user_id)
        else:
            borrowed_by.append(user_id)
        
        # Use update statement to force JSON update
        self.db.execute(
            update(BookDB)
            .where(BookDB.id == book_id)
            .values(borrowed_by=borrowed_by)
        )
        
        self.db.commit()
        self.db.refresh(db_book)
        
        return self._to_pydantic(db_book)
    
    def _to_pydantic(self, db_book: BookDB) -> Book:
        """Convert SQLAlchemy model to Pydantic model"""
        return Book(
            id=db_book.id,
            title=db_book.title,
            author=db_book.author,
            genre=db_book.genre,
            description=db_book.description,
            image_url=db_book.image_url,
            average_rating=db_book.average_rating,
            total_ratings=db_book.total_ratings,
            user_ratings=db_book.user_ratings or {},
            favorites=db_book.favorites or [],
            borrowed_by=db_book.borrowed_by or []
        )
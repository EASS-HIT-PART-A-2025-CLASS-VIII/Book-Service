from typing import Dict, List, Optional
from app.models import Book, BookCreate
from app.initial_books import INITIAL_BOOKS


class BookRepository:
    """
    In-memory storage for books.
    
    This repository provides CRUD operations for book management
    using a simple dictionary-based in-memory storage.
    """
    
    def __init__(self) -> None:
        """Initialize the repository with pre-loaded books."""
        self._books: Dict[int, Book] = {}
        self._next_id: int = 1
        
        # Load initial books
        for book in INITIAL_BOOKS:
            self._books[book.id] = book
            if book.id >= self._next_id:
                self._next_id = book.id + 1
    
    def create(self, book_data: BookCreate) -> Book:
        """
        Create a new book.
        
        Args:
            book_data: Book data without ID
            
        Returns:
            Book: The created book with assigned ID
        """
        book = Book(
            id=self._next_id,
            title=book_data.title,
            author=book_data.author,
            genre=book_data.genre,
            description=book_data.description,
            image_url=book_data.image_url,
            average_rating=0.0,
            total_ratings=0,
            user_ratings={},
            favorites=[]
        )
        self._books[self._next_id] = book
        self._next_id += 1
        return book
    
    def get_all(self) -> List[Book]:
        """
        Get all books.
        
        Returns:
            List[Book]: List of all books in the repository
        """
        return list(self._books.values())
    
    def get_by_id(self, book_id: int) -> Optional[Book]:
        """
        Get a book by ID.
        
        Args:
            book_id: The ID of the book to retrieve
            
        Returns:
            Optional[Book]: The book if found, None otherwise
        """
        return self._books.get(book_id)
    
    def update(self, book_id: int, book_data: BookCreate) -> Optional[Book]:
        """
        Update an existing book.
        
        Args:
            book_id: The ID of the book to update
            book_data: New book data
            
        Returns:
            Optional[Book]: The updated book if found, None otherwise
        """
        if book_id not in self._books:
            return None
        
        old_book = self._books[book_id]
        book = Book(
            id=book_id,
            title=book_data.title,
            author=book_data.author,
            genre=book_data.genre,
            description=book_data.description,
            image_url=book_data.image_url,
            average_rating=old_book.average_rating,
            total_ratings=old_book.total_ratings,
            user_ratings=old_book.user_ratings,
            favorites=old_book.favorites
        )
        self._books[book_id] = book
        return book
    
    def delete(self, book_id: int) -> bool:
        """
        Delete a book.
        
        Args:
            book_id: The ID of the book to delete
            
        Returns:
            bool: True if book was deleted, False if not found
        """
        if book_id in self._books:
            del self._books[book_id]
            return True
        return False
    
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
        book = self._books.get(book_id)
        if not book:
            return None
        
        # Update user rating
        book.user_ratings[user_id] = rating
        
        # Recalculate average
        if book.user_ratings:
            book.average_rating = sum(book.user_ratings.values()) / len(book.user_ratings)
            book.total_ratings = len(book.user_ratings)
        
        return book
    
    def toggle_favorite(self, book_id: int, user_id: str) -> Optional[Book]:
        """
        Toggle favorite status for a book.
        
        Args:
            book_id: The ID of the book
            user_id: The user's ID
            
        Returns:
            Optional[Book]: The updated book if found, None otherwise
        """
        book = self._books.get(book_id)
        if not book:
            return None
        
        if user_id in book.favorites:
            book.favorites.remove(user_id)
        else:
            book.favorites.append(user_id)
        
        return book
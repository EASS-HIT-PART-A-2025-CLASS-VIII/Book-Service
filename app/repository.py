from typing import Dict, List, Optional
from app.models import Book, BookCreate


class BookRepository:
    """In-memory storage for books"""
    
    def __init__(self):
        self._books: Dict[int, Book] = {}
        self._next_id: int = 1
    
    def create(self, book_data: BookCreate) -> Book:
        """Create a new book"""
        book = Book(
            id=self._next_id,
            title=book_data.title,
            author=book_data.author,
            genre=book_data.genre,
            rating=book_data.rating
        )
        self._books[self._next_id] = book
        self._next_id += 1
        return book
    
    def get_all(self) -> List[Book]:
        """Get all books"""
        return list(self._books.values())
    
    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Get a book by ID"""
        return self._books.get(book_id)
    
    def update(self, book_id: int, book_data: BookCreate) -> Optional[Book]:
        """Update a book"""
        if book_id not in self._books:
            return None
        
        book = Book(
            id=book_id,
            title=book_data.title,
            author=book_data.author,
            genre=book_data.genre,
            rating=book_data.rating
        )
        self._books[book_id] = book
        return book
    
    def delete(self, book_id: int) -> bool:
        """Delete a book"""
        if book_id in self._books:
            del self._books[book_id]
            return True
        return False
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.models import Book, BookCreate
from app.repository import BookRepository
from app.config import settings

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version
)

# CORS middleware for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create repository instance
repo = BookRepository()


@app.get("/", tags=["Root"])
def read_root() -> dict:
    """
    Root endpoint - Welcome message.
    
    Returns:
        dict: Welcome message
    """
    return {"message": "Welcome to Book Service API"}


@app.get("/books", response_model=List[Book], tags=["Books"])
def get_books() -> List[Book]:
    """
    Get all books.
    
    Returns:
        List[Book]: List of all books in the collection
    """
    return repo.get_all()


@app.get("/books/{book_id}", response_model=Book, tags=["Books"])
def get_book(book_id: int) -> Book:
    """
    Get a specific book by ID.
    
    Args:
        book_id: The ID of the book to retrieve
        
    Returns:
        Book: The requested book
        
    Raises:
        HTTPException: 404 if book not found
    """
    book = repo.get_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(book_data: BookCreate) -> Book:
    """
    Create a new book.
    
    Args:
        book_data: Book data (title, author, genre, rating)
        
    Returns:
        Book: The created book with assigned ID
    """
    return repo.create(book_data)


@app.put("/books/{book_id}", response_model=Book, tags=["Books"])
def update_book(book_id: int, book_data: BookCreate) -> Book:
    """
    Update an existing book.
    
    Args:
        book_id: The ID of the book to update
        book_data: New book data
        
    Returns:
        Book: The updated book
        
    Raises:
        HTTPException: 404 if book not found
    """
    book = repo.update(book_id, book_data)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def delete_book(book_id: int) -> None:
    """
    Delete a book.
    
    Args:
        book_id: The ID of the book to delete
        
    Raises:
        HTTPException: 404 if book not found
    """
    if not repo.delete(book_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )


@app.post("/books/{book_id}/rate", response_model=Book, tags=["User Actions"])
def rate_book(book_id: int, user_id: str, rating: float) -> Book:
    """
    Rate a book.
    
    Args:
        book_id: The ID of the book to rate
        user_id: The user's ID
        rating: Rating value (0-10)
        
    Returns:
        Book: The updated book with new rating
        
    Raises:
        HTTPException: 404 if book not found, 400 if rating invalid
    """
    if rating < 0 or rating > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 0 and 10"
        )
    
    book = repo.rate_book(book_id, user_id, rating)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.post("/books/{book_id}/favorite", response_model=Book, tags=["User Actions"])
def toggle_favorite(book_id: int, user_id: str) -> Book:
    """
    Toggle favorite status for a book.
    
    Args:
        book_id: The ID of the book
        user_id: The user's ID
        
    Returns:
        Book: The updated book
        
    Raises:
        HTTPException: 404 if book not found
    """
    book = repo.toggle_favorite(book_id, user_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book
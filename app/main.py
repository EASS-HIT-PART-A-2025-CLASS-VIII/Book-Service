from fastapi import FastAPI, HTTPException, status
from typing import List
from app.models import Book, BookCreate
from app.repository import BookRepository

app = FastAPI(title="Book Service API")

# Create repository instance
repo = BookRepository()


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Book Service API"}


@app.get("/books", response_model=List[Book])
def get_books():
    """Get all books"""
    return repo.get_all()


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    """Get a book by ID"""
    book = repo.get_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookCreate):
    """Create a new book"""
    return repo.create(book_data)


@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_data: BookCreate):
    """Update a book"""
    book = repo.update(book_id, book_data)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    """Delete a book"""
    if not repo.delete(book_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return {"message": f"Book {book_id} deleted successfully!"}
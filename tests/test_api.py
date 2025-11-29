import pytest
from fastapi.testclient import TestClient
from app.main import app, BookRepository


@pytest.fixture
def client():
    """Create a fresh client for each test"""
    # Create a new repository instance for each test
    from app import main
    main.repo = BookRepository()
    
    with TestClient(app) as test_client:
        yield test_client


def test_read_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Book Service API"}


def test_create_book(client):
    """Test creating a book"""
    book_data = {
        "title": "Harry Potter",
        "author": "J.K. Rowling",
        "genre": "Fantasy",
        "rating": 9.5
    }
    response = client.post("/books", json=book_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Harry Potter"
    assert data["author"] == "J.K. Rowling"
    assert "id" in data


def test_get_all_books(client):
    """Test getting all books"""
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_book_by_id(client):
    """Test getting a specific book"""
    # First create a book
    book_data = {
        "title": "1984",
        "author": "George Orwell",
        "genre": "Dystopian",
        "rating": 9.0
    }
    create_response = client.post("/books", json=book_data)
    book_id = create_response.json()["id"]
    
    # Now get it
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "1984"


def test_get_nonexistent_book(client):
    """Test getting a book that doesn't exist"""
    response = client.get("/books/99999")
    assert response.status_code == 404


def test_update_book(client):
    """Test updating a book"""
    # First create a book
    book_data = {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "genre": "Fantasy",
        "rating": 8.5
    }
    create_response = client.post("/books", json=book_data)
    book_id = create_response.json()["id"]
    
    # Now update it
    updated_data = {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "genre": "Fantasy",
        "rating": 9.0
    }
    response = client.put(f"/books/{book_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 9.0


def test_delete_book(client):
    """Test deleting a book"""
    # First create a book
    book_data = {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Fiction",
        "rating": 8.8
    }
    create_response = client.post("/books", json=book_data)
    book_id = create_response.json()["id"]
    
    # Now delete it
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404
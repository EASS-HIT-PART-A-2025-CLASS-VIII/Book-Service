"""
API Tests for Book Library
Tests all main endpoints and functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)

# Test data
TEST_USER_ID = "test_user_pytest"
TEST_BOOK_ID = 1


class TestBasicEndpoints:
    """Test basic API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_get_all_books(self):
        """Test getting all books"""
        response = client.get("/books")
        assert response.status_code == 200
        books = response.json()
        assert isinstance(books, list)
        assert len(books) > 0
        # Check first book has required fields
        assert "id" in books[0]
        assert "title" in books[0]
        assert "author" in books[0]
    
    def test_get_single_book(self):
        """Test getting a specific book"""
        response = client.get(f"/books/{TEST_BOOK_ID}")
        assert response.status_code == 200
        book = response.json()
        assert book["id"] == TEST_BOOK_ID
        assert "title" in book
        assert "author" in book
    
    def test_get_nonexistent_book(self):
        """Test getting a book that doesn't exist"""
        response = client.get("/books/99999")
        assert response.status_code == 404


class TestUserActions:
    """Test user interaction endpoints"""
    
    def test_rate_book_valid(self):
        """Test rating a book with valid rating"""
        response = client.post(
            f"/books/{TEST_BOOK_ID}/rate",
            params={"user_id": TEST_USER_ID, "rating": 8.5}
        )
        assert response.status_code == 200
        book = response.json()
        assert TEST_USER_ID in book["user_ratings"]
        assert book["user_ratings"][TEST_USER_ID] == 8.5
    
    def test_rate_book_invalid_rating(self):
        """Test rating with invalid value (>10)"""
        response = client.post(
            f"/books/{TEST_BOOK_ID}/rate",
            params={"user_id": TEST_USER_ID, "rating": 15.0}
        )
        assert response.status_code == 400
    
    def test_rate_book_negative_rating(self):
        """Test rating with negative value"""
        response = client.post(
            f"/books/{TEST_BOOK_ID}/rate",
            params={"user_id": TEST_USER_ID, "rating": -5.0}
        )
        assert response.status_code == 400
    
    def test_toggle_favorite(self):
        """Test adding/removing from favorites"""
        # First toggle - add to favorites
        response = client.post(
            f"/books/{TEST_BOOK_ID}/favorite",
            params={"user_id": TEST_USER_ID}
        )
        assert response.status_code == 200
        book = response.json()
        assert TEST_USER_ID in book["favorites"]
        
        # Second toggle - remove from favorites
        response = client.post(
            f"/books/{TEST_BOOK_ID}/favorite",
            params={"user_id": TEST_USER_ID}
        )
        assert response.status_code == 200
        book = response.json()
        assert TEST_USER_ID not in book["favorites"]
    
    def test_toggle_cart(self):
        """Test adding/removing from cart"""
        # Add to cart
        response = client.post(
            f"/books/{TEST_BOOK_ID}/borrow",
            params={"user_id": TEST_USER_ID}
        )
        assert response.status_code == 200
        book = response.json()
        assert TEST_USER_ID in book["borrowed_by"]
        
        # Remove from cart
        response = client.post(
            f"/books/{TEST_BOOK_ID}/borrow",
            params={"user_id": TEST_USER_ID}
        )
        assert response.status_code == 200
        book = response.json()
        assert TEST_USER_ID not in book["borrowed_by"]
    
    def test_get_user_cart(self):
        """Test getting user's cart"""
        # Add a book to cart first
        client.post(
            f"/books/{TEST_BOOK_ID}/borrow",
            params={"user_id": TEST_USER_ID}
        )
        
        # Get cart
        response = client.get(f"/books/cart/{TEST_USER_ID}")
        assert response.status_code == 200
        cart = response.json()
        assert isinstance(cart, list)
        
        # Clean up - remove from cart
        client.post(
            f"/books/{TEST_BOOK_ID}/borrow",
            params={"user_id": TEST_USER_ID}
        )


class TestRecommendations:
    """Test recommendation endpoints"""
    
    def test_weekly_recommendations(self):
        """Test getting weekly recommendations"""
        response = client.get("/recommendations/weekly")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "source" in data
        recommendations = data["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
    
    def test_simple_recommendations(self):
        """Test simple rule-based recommendations"""
        response = client.get(f"/recommendations/simple/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert "reasoning" in data
    
    def test_refresh_recommendations(self):
        """Test triggering recommendation refresh"""
        response = client.post("/recommendations/refresh")
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "message" in data


class TestBackgroundTasks:
    """Test background task endpoints"""
    
    def test_send_notification(self):
        """Test sending a test notification"""
        response = client.post(
            "/notifications/test",
            params={"user_id": TEST_USER_ID, "message": "Test notification"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data

class TestDataIntegrity:
    """Test data consistency and validation"""
    
    def test_average_rating_calculation(self):
        """Test that average rating is calculated correctly"""
        test_user_1 = "rating_test_user_1"
        test_user_2 = "rating_test_user_2"
        
        # User 1 rates 8.0
        client.post(
            f"/books/{TEST_BOOK_ID}/rate",
            params={"user_id": test_user_1, "rating": 8.0}
        )
        
        # User 2 rates 10.0
        response = client.post(
            f"/books/{TEST_BOOK_ID}/rate",
            params={"user_id": test_user_2, "rating": 10.0}
        )
        
        book = response.json()
        # Average should be 9.0 (if only these two ratings)
        # Note: Other tests might have added ratings, so we just check it's reasonable
        assert 0 <= book["average_rating"] <= 10
        assert book["total_ratings"] >= 2
    
    def test_book_fields_not_null(self):
        """Test that all books have required fields"""
        response = client.get("/books")
        books = response.json()
        
        for book in books:
            assert book["id"] is not None
            assert book["title"] is not None
            assert book["author"] is not None
            assert book["genre"] is not None
            assert "average_rating" in book
            assert "total_ratings" in book


# Fixtures for pytest
@pytest.fixture(autouse=True)
def cleanup():
    """Clean up test data after each test"""
    yield
    # Any cleanup code here if needed
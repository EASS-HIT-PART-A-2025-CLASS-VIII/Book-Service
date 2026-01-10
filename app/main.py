from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import redis
import json

from sqlalchemy.orm import Session

from app.models import Book, BookCreate
from app.repository import BookRepository
from app.config import settings
from app.database import engine, get_db, Base
from app.db_models import BookDB
from app.initial_books import INITIAL_BOOKS
from app.worker import update_recommendations, send_notification, celery_app

from app.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    Token,
    TokenData
)
from app.user_models import UserDB
from app.auth import UserCreate, UserLogin, UserResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.llm_recommendations import (
    get_llm_recommendations, 
    get_simple_recommendations,
    RecommendationResult
)
import asyncio

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Library API",
    description="A comprehensive API for managing a book library with authentication",
    version="3.0.0",
    openapi_tags=[
        {"name": "Books", "description": "Book management operations"},
        {"name": "User Actions", "description": "User interactions with books"},
        {"name": "Recommendations", "description": "Book recommendation system"},
        {"name": "Background Tasks", "description": "Async background workers"},
        {"name": "Authentication", "description": "User registration and login"},
        {"name": "Protected Actions", "description": "Actions requiring authentication"},
        {"name": "Admin Only", "description": "Admin-only operations"},
    ]
)

# Mount static files for images
images_path = os.path.join(os.path.dirname(__file__), "images")
if os.path.exists(images_path):
    app.mount("/images", StaticFiles(directory=images_path), name="images")
    
# CORS middleware for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)


@app.on_event("startup")
def startup_event():
    """Initialize database with initial books if empty"""
    db = next(get_db())
    try:
        # Check if database is empty
        count = db.query(BookDB).count()
        if count == 0:
            print("📚 Initializing database with initial books...")
            for book in INITIAL_BOOKS:
                db_book = BookDB(
                    id=book.id,
                    title=book.title,
                    author=book.author,
                    genre=book.genre,
                    description=book.description,
                    image_url=book.image_url,
                    average_rating=book.average_rating,
                    total_ratings=book.total_ratings,
                    user_ratings=book.user_ratings,
                    favorites=book.favorites,
                    borrowed_by=book.borrowed_by
                )
                db.add(db_book)
            db.commit()
            print(f"✅ Added {len(INITIAL_BOOKS)} books to database!")
    finally:
        db.close()


@app.get("/", tags=["Root"])
def read_root() -> dict:
    """Root endpoint - Welcome message"""
    return {"message": "Welcome to Book Service API"}


@app.get("/books", response_model=List[Book], tags=["Books"])
def get_books(db: Session = Depends(get_db)) -> List[Book]:
    """Get all books"""
    repo = BookRepository(db)
    return repo.get_all()


@app.get("/books/{book_id}", response_model=Book, tags=["Books"])
def get_book(book_id: int, db: Session = Depends(get_db)) -> Book:
    """Get a specific book by ID"""
    repo = BookRepository(db)
    book = repo.get_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["Books"])
def create_book(book_data: BookCreate, db: Session = Depends(get_db)) -> Book:
    """Create a new book"""
    repo = BookRepository(db)
    return repo.create(book_data)


@app.put("/books/{book_id}", response_model=Book, tags=["Books"])
def update_book(book_id: int, book_data: BookCreate, db: Session = Depends(get_db)) -> Book:
    """Update an existing book"""
    repo = BookRepository(db)
    book = repo.update(book_id, book_data)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Books"])
def delete_book(book_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a book"""
    repo = BookRepository(db)
    if not repo.delete(book_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )


@app.post("/books/{book_id}/rate", response_model=Book, tags=["User Actions"])
def rate_book(book_id: int, user_id: str, rating: float, db: Session = Depends(get_db)) -> Book:
    """Rate a book"""
    if rating < 0 or rating > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 0 and 10"
        )
    
    repo = BookRepository(db)
    book = repo.rate_book(book_id, user_id, rating)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.post("/books/{book_id}/favorite", response_model=Book, tags=["User Actions"])
def toggle_favorite(book_id: int, user_id: str, db: Session = Depends(get_db)) -> Book:
    """Toggle favorite status for a book"""
    repo = BookRepository(db)
    book = repo.toggle_favorite(book_id, user_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.post("/books/{book_id}/borrow", response_model=Book, tags=["User Actions"])
def borrow_book(book_id: int, user_id: str, db: Session = Depends(get_db)) -> Book:
    """Add or remove book from user's cart"""
    repo = BookRepository(db)
    book = repo.toggle_borrow(book_id, user_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return book


@app.get("/books/cart/{user_id}", response_model=List[Book], tags=["User Actions"])
def get_user_cart(user_id: str, db: Session = Depends(get_db)) -> List[Book]:
    """Get all books in user's cart"""
    repo = BookRepository(db)
    all_books = repo.get_all()
    cart_books = [book for book in all_books if user_id in book.borrowed_by]
    return cart_books


@app.get("/recommendations/weekly", tags=["Recommendations"])
def get_weekly_recommendations():
    """Get weekly top recommendations from Redis cache"""
    try:
        data = redis_client.get("weekly_recommendations")
        if data:
            recommendations = json.loads(data)
            return {
                "source": "cache",
                "recommendations": recommendations
            }
        else:
            update_recommendations.delay()
            
            db = next(get_db())
            top_books = (
                db.query(BookDB)
                .filter(BookDB.total_ratings > 0)
                .order_by(BookDB.average_rating.desc())
                .limit(5)
                .all()
            )
            
            recommendations = [
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "rating": book.average_rating,
                    "total_ratings": book.total_ratings
                }
                for book in top_books
            ]
            
            return {
                "source": "database",
                "message": "Recommendations are being updated in background",
                "recommendations": recommendations
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")


@app.post("/recommendations/refresh", tags=["Recommendations"])
def trigger_recommendation_refresh():
    """Manually trigger recommendation refresh"""
    task = update_recommendations.delay()
    return {
        "message": "Recommendation refresh triggered",
        "task_id": task.id,
        "status": "processing"
    }


@app.get("/tasks/{task_id}", tags=["Background Tasks"])
def get_task_status(task_id: str):
    """Check status of a background task"""
    from celery.result import AsyncResult
    
    task_result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }


@app.post("/notifications/test", tags=["Background Tasks"])
def send_test_notification(user_id: str, message: str):
    """Send a test notification (background task)"""
    task = send_notification.delay(user_id, message)
    return {
        "message": "Notification task queued",
        "task_id": task.id
    }

    # =====================
# LLM RECOMMENDATIONS
# =====================

@app.get("/recommendations/ai/{user_id}", response_model=RecommendationResult, tags=["Recommendations"])
async def get_ai_recommendations_endpoint(user_id: str, db: Session = Depends(get_db)):
    """
    Get AI-powered personalized recommendations based on user's reading history.
    
    Uses LLM (GPT-4) to analyze user's favorite books and recommend similar ones.
    Falls back to simple recommendations if LLM is unavailable.
    
    Requires: OPENAI_API_KEY environment variable
    """
    repo = BookRepository(db)
    all_books_db = repo.get_all()
    
    # Convert to dict for LLM
    all_books = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "average_rating": book.average_rating,
            "user_rating": book.user_ratings.get(user_id, 0)
        }
        for book in all_books_db
    ]
    
    # Get user's highly-rated books (rating >= 7)
    user_favorites = [
        book for book in all_books 
        if book["user_rating"] >= 7
    ]
    
    if not user_favorites:
        # User hasn't rated anything highly yet
        return RecommendationResult(
            recommendations=[],
            reasoning="Please rate some books first to get personalized recommendations!"
        )
    
    # Get books user hasn't rated yet
    unrated_books = [
        book for book in all_books
        if book["user_rating"] == 0
    ]
    
    if not unrated_books:
        return RecommendationResult(
            recommendations=[],
            reasoning="You've rated all the books! Check back when we add more."
        )
    
    try:
        # Try LLM recommendations
        result = await get_llm_recommendations(user_favorites, unrated_books)
        return result
    except Exception as e:
        # Fallback to simple recommendations
        simple_recs = get_simple_recommendations(user_favorites, unrated_books)
        
        return RecommendationResult(
            recommendations=[
                {
                    "title": book["title"],
                    "author": book["author"],
                    "reason": f"Recommended based on your love of {book['genre']} books",
                    "similarity_score": 7.5
                }
                for book in simple_recs
            ],
            reasoning=f"Using genre-based recommendations (LLM unavailable: {str(e)})"
        )


@app.get("/recommendations/simple/{user_id}", tags=["Recommendations"])
def get_simple_recommendations_endpoint(user_id: str, limit: int = 5, db: Session = Depends(get_db)):
    """
    Get simple rule-based recommendations (no LLM required).
    
    Recommends books from same genres as user's favorites.
    """
    repo = BookRepository(db)
    all_books_db = repo.get_all()
    
    all_books = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "average_rating": book.average_rating,
            "user_rating": book.user_ratings.get(user_id, 0)
        }
        for book in all_books_db
    ]
    
    user_favorites = [b for b in all_books if b["user_rating"] >= 7]
    
    if not user_favorites:
        # Return top-rated books
        top_rated = sorted(all_books, key=lambda x: x["average_rating"], reverse=True)[:limit]
        return {
            "recommendations": top_rated,
            "reasoning": "Top rated books (rate some books to get personalized recommendations!)"
        }
    
    recommendations = get_simple_recommendations(user_favorites, all_books, limit)
    
    return {
        "recommendations": recommendations,
        "reasoning": f"Based on your favorite genres and highly-rated books"
    }

    # =====================
# AUTHENTICATION (Session 11)
# =====================

security = HTTPBearer()


@app.post("/auth/register", response_model=UserResponse, tags=["Authentication"])
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with hashed password
    
    Session 11 deliverable: Password hashing with bcrypt
    """
    # Check if user already exists
    existing_user = db.query(UserDB).filter(
        (UserDB.username == user_data.username) | (UserDB.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    # Create new user with hashed password
    db_user = UserDB(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role="user",
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        role=db_user.role,
        is_active=db_user.is_active
    )


@app.post("/auth/login", tags=["Authentication"])
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    
    Session 11 deliverable: JWT token generation
    """
    # Find user
    user = db.query(UserDB).filter(UserDB.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active
        )
    }


@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current authenticated user info
    
    Session 11 deliverable: JWT-protected route with role checks
    Requires valid JWT token in Authorization header
    """
    # Get full user from database
    user = db.query(UserDB).filter(UserDB.username == current_user.username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active
    )

@app.post("/admin/users", tags=["Admin"])
async def admin_only_endpoint(current_user: TokenData = Depends(get_current_user)):
    """
    Admin-only endpoint - demonstrates role-based access control
    
    Session 11 deliverable: Role checks (admin only)
    Returns 403 if user role is not 'admin'
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return {
        "message": "Admin access granted",
        "admin": current_user.username
    }
    
    return {
        "message": "Admin access granted",
        "admin": current_user["username"]
    }
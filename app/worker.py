from celery import Celery
import os

# Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "book_library",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(name="update_recommendations")
def update_recommendations():
    """
    Background task: Update weekly recommendations
    Runs every day to find top-rated books
    """
    from app.database import SessionLocal
    from app.db_models import BookDB
    from sqlalchemy import func
    import redis
    import json
    
    db = SessionLocal()
    
    try:
        # Find top 5 books by rating
        top_books = (
            db.query(BookDB)
            .filter(BookDB.total_ratings > 0)
            .order_by(BookDB.average_rating.desc())
            .limit(5)
            .all()
        )
        
        # Prepare data
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
        
        # Store in Redis
        r = redis.from_url(REDIS_URL)
        r.setex(
            "weekly_recommendations",
            60 * 60 * 24 * 7,  # 7 days
            json.dumps(recommendations)
        )
        
        return f"✅ Updated recommendations: {len(recommendations)} books"
        
    finally:
        db.close()


@celery_app.task(name="send_notification")
def send_notification(user_id: str, message: str):
    """
    Background task: Send notification to user
    (In real app, this would send email/push notification)
    """
    import time
    time.sleep(2)  # Simulate email sending
    
    print(f"📧 Notification sent to {user_id}: {message}")
    return f"Notification sent to {user_id}"


# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    'update-recommendations-daily': {
        'task': 'update_recommendations',
        'schedule': 60 * 60 * 24,  # Every 24 hours
    },
}
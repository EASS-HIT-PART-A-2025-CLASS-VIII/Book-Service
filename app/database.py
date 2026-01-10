from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time

# Database URL from environment or default to local PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bookuser:bookpass@localhost:5432/bookdb"
)

# Create SQLAlchemy engine with retry logic
def create_engine_with_retry(max_retries=5, retry_delay=2):
    """Create engine with retry logic for Docker startup"""
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            # Test connection
            engine.connect()
            print(f"✅ Successfully connected to database!")
            return engine
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"⏳ Database not ready yet (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Failed to connect to database after {max_retries} attempts")
                raise e

engine = create_engine_with_retry()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency for getting database session.
    Yields a database session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
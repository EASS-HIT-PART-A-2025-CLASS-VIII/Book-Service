#!/usr/bin/env python3
"""
Async Recommendation Refresh Script - Session 09 Deliverable

Features:
- Bounded concurrency with asyncio.Semaphore
- Retry logic with exponential backoff
- Redis-backed idempotency
- Detailed logging
"""

import asyncio
import aiohttp
import redis
import time
import hashlib
from typing import List, Dict, Optional
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
REDIS_URL = "redis://localhost:6379/0"
MAX_CONCURRENT = 5  # Bounded concurrency
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Redis client for idempotency
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class RecommendationRefresher:
    """Async recommendation refresh with bounded concurrency and idempotency"""
    
    def __init__(self, max_concurrent: int = MAX_CONCURRENT):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Create aiohttp session"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    def generate_task_id(self, task_type: str, params: str = "") -> str:
        """Generate idempotent task ID"""
        data = f"{task_type}:{params}:{datetime.now().strftime('%Y-%m-%d')}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def is_task_completed(self, task_id: str) -> bool:
        """Check if task was already completed today"""
        key = f"refresh:completed:{task_id}"
        return redis_client.exists(key) > 0
    
    def mark_task_completed(self, task_id: str):
        """Mark task as completed with 24h TTL"""
        key = f"refresh:completed:{task_id}"
        redis_client.setex(key, 86400, "1")  # 24 hours
    
    async def fetch_with_retry(self, url: str, method: str = "GET", **kwargs) -> Dict:
        """
        Fetch URL with retry logic and exponential backoff
        
        Args:
            url: Target URL
            method: HTTP method
            **kwargs: Additional request parameters
        
        Returns:
            Response JSON
        
        Raises:
            Exception if all retries fail
        """
        for attempt in range(MAX_RETRIES):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', RETRY_DELAY * (2 ** attempt)))
                        print(f"⚠️ Rate limited, waiting {retry_after}s...")
                        await asyncio.sleep(retry_after)
                    else:
                        print(f"⚠️ HTTP {response.status}, retrying...")
                        await asyncio.sleep(RETRY_DELAY * (2 ** attempt))
            except aiohttp.ClientError as e:
                print(f"❌ Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (2 ** attempt))
                else:
                    raise
        
        raise Exception(f"Failed after {MAX_RETRIES} attempts")
    
    async def refresh_weekly_recommendations(self) -> Dict:
        """
        Refresh weekly recommendations with idempotency
        
        Returns:
            Task result
        """
        task_id = self.generate_task_id("weekly_recommendations")
        
        # Check idempotency
        if self.is_task_completed(task_id):
            print(f"✅ Task {task_id[:8]} already completed today, skipping")
            return {"status": "skipped", "task_id": task_id, "reason": "already_completed"}
        
        print(f"🔄 Refreshing weekly recommendations (task: {task_id[:8]})")
        
        async with self.semaphore:  # Bounded concurrency
            try:
                start_time = time.time()
                
                # Trigger refresh
                result = await self.fetch_with_retry(
                    f"{API_URL}/recommendations/refresh",
                    method="POST"
                )
                
                duration = time.time() - start_time
                
                # Mark as completed
                self.mark_task_completed(task_id)
                
                print(f"✅ Weekly recommendations refreshed in {duration:.2f}s")
                return {
                    "status": "success",
                    "task_id": task_id,
                    "duration": duration,
                    "result": result
                }
            
            except Exception as e:
                print(f"❌ Failed to refresh weekly recommendations: {e}")
                return {
                    "status": "failed",
                    "task_id": task_id,
                    "error": str(e)
                }
    
    async def refresh_book_cache(self, book_id: int) -> Dict:
        """
        Refresh cache for a specific book
        
        Args:
            book_id: Book ID to refresh
        
        Returns:
            Task result
        """
        task_id = self.generate_task_id("book_cache", str(book_id))
        
        if self.is_task_completed(task_id):
            return {"status": "skipped", "book_id": book_id, "task_id": task_id}
        
        print(f"🔄 Refreshing cache for book {book_id}")
        
        async with self.semaphore:
            try:
                # Fetch book to refresh cache
                result = await self.fetch_with_retry(f"{API_URL}/books/{book_id}")
                
                self.mark_task_completed(task_id)
                
                print(f"✅ Book {book_id} cache refreshed")
                return {
                    "status": "success",
                    "book_id": book_id,
                    "task_id": task_id,
                    "title": result.get("title")
                }
            
            except Exception as e:
                print(f"❌ Failed to refresh book {book_id}: {e}")
                return {
                    "status": "failed",
                    "book_id": book_id,
                    "error": str(e)
                }
    
    async def refresh_all_books(self) -> List[Dict]:
        """
        Refresh cache for all books with bounded concurrency
        
        Returns:
            List of task results
        """
        print(f"🔄 Fetching all books...")
        
        try:
            # Get all books
            books = await self.fetch_with_retry(f"{API_URL}/books")
            print(f"📚 Found {len(books)} books")
            
            # Create tasks for all books
            tasks = [
                self.refresh_book_cache(book["id"])
                for book in books
            ]
            
            # Run with bounded concurrency
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successes
            successes = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
            skipped = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "skipped")
            
            print(f"\n✅ Completed: {successes} success, {skipped} skipped, {len(results) - successes - skipped} failed")
            
            return results
        
        except Exception as e:
            print(f"❌ Failed to refresh all books: {e}")
            return []


async def main():
    """Main async refresh routine"""
    print("=" * 60)
    print("🚀 Starting Async Recommendation Refresh")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Max concurrent: {MAX_CONCURRENT}")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    async with RecommendationRefresher(max_concurrent=MAX_CONCURRENT) as refresher:
        # Refresh weekly recommendations
        weekly_result = await refresher.refresh_weekly_recommendations()
        
        print()
        
        # Refresh all books (optional - comment out if not needed)
        # book_results = await refresher.refresh_all_books()
    
    total_duration = time.time() - start_time
    
    print()
    print("=" * 60)
    print(f"✅ Refresh completed in {total_duration:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)

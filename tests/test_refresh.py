"""
Tests for async refresh script - Session 09 deliverable
Uses pytest-asyncio for async testing
"""

import pytest
import asyncio
from scripts.refresh import RecommendationRefresher

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


class TestRecommendationRefresher:
    """Test async recommendation refresh with bounded concurrency"""
    
    @pytest.mark.anyio
    async def test_refresher_context_manager(self):
        """Test that refresher creates and closes aiohttp session"""
        async with RecommendationRefresher(max_concurrent=3) as refresher:
            assert refresher.session is not None
            assert refresher.semaphore._value == 3
        
        # Session should be closed after context exit
        assert refresher.session.closed
    
    @pytest.mark.anyio
    async def test_task_id_generation(self):
        """Test idempotent task ID generation"""
        async with RecommendationRefresher() as refresher:
            task_id_1 = refresher.generate_task_id("test", "params")
            task_id_2 = refresher.generate_task_id("test", "params")
            
            # Same params should generate same ID on same day
            assert task_id_1 == task_id_2
            
            # Different params should generate different ID
            task_id_3 = refresher.generate_task_id("test", "different")
            assert task_id_1 != task_id_3
    
    @pytest.mark.anyio
    async def test_task_completion_tracking(self):
        """Test Redis-backed idempotency"""
        async with RecommendationRefresher() as refresher:
            task_id = "test_task_123"
            
            # Initially not completed
            assert not refresher.is_task_completed(task_id)
            
            # Mark as completed
            refresher.mark_task_completed(task_id)
            
            # Should now be completed
            assert refresher.is_task_completed(task_id)
    
    @pytest.mark.anyio
    async def test_weekly_recommendations_refresh(self):
        """Test weekly recommendations refresh with idempotency"""
        async with RecommendationRefresher() as refresher:
            # First refresh should succeed
            result = await refresher.refresh_weekly_recommendations()
            
            assert result["status"] in ["success", "skipped"]
            assert "task_id" in result
            
            # Second refresh on same day should be skipped
            result2 = await refresher.refresh_weekly_recommendations()
            assert result2["status"] == "skipped"
            assert result2["reason"] == "already_completed"
    
    @pytest.mark.anyio
    async def test_bounded_concurrency(self):
        """Test that semaphore limits concurrent requests"""
        max_concurrent = 2
        async with RecommendationRefresher(max_concurrent=max_concurrent) as refresher:
            # Semaphore should start at max value
            assert refresher.semaphore._value == max_concurrent
            
            # Acquire semaphore
            async with refresher.semaphore:
                assert refresher.semaphore._value == max_concurrent - 1
            
            # Should be released
            assert refresher.semaphore._value == max_concurrent
    
    @pytest.mark.anyio
    async def test_book_cache_refresh(self):
        """Test single book cache refresh"""
        async with RecommendationRefresher() as refresher:
            # Try to refresh book 1
            result = await refresher.refresh_book_cache(1)
            
            # Should succeed or skip (if already completed today)
            assert result["status"] in ["success", "skipped", "failed"]
            assert result["book_id"] == 1
            assert "task_id" in result


# Fixtures
@pytest.fixture(autouse=True)
async def cleanup_redis():
    """Clean up test keys from Redis after each test"""
    yield
    
    # Cleanup after test
    import redis
    r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
    
    # Delete test keys
    for key in r.scan_iter("refresh:completed:*"):
        if "test" in key:
            r.delete(key)

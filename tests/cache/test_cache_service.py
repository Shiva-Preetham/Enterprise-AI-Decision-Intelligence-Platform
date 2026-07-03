"""
Tests for CacheService.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch

from backend.cache.service import CacheService

@pytest.fixture
def cache_service():
    return CacheService()

@pytest.mark.asyncio
@patch("backend.cache.service.get_redis")
async def test_cache_get_hit(mock_get_redis, cache_service):
    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps({"test": "value"})
    mock_get_redis.return_value = mock_redis
    
    result = await cache_service.get("test_key")
    assert result == {"test": "value"}
    mock_redis.get.assert_called_once_with("test_key")

@pytest.mark.asyncio
@patch("backend.cache.service.get_redis")
async def test_cache_get_miss(mock_get_redis, cache_service):
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_get_redis.return_value = mock_redis
    
    result = await cache_service.get("test_key")
    assert result is None

@pytest.mark.asyncio
@patch("backend.cache.service.get_redis")
async def test_cache_set(mock_get_redis, cache_service):
    mock_redis = AsyncMock()
    mock_get_redis.return_value = mock_redis
    
    result = await cache_service.set("test_key", {"test": "value"}, ttl=60)
    assert result is True
    mock_redis.set.assert_called_once_with("test_key", json.dumps({"test": "value"}), ex=60)

@pytest.mark.asyncio
@patch("backend.cache.service.get_redis")
async def test_cache_delete(mock_get_redis, cache_service):
    mock_redis = AsyncMock()
    mock_redis.delete.return_value = 1
    mock_get_redis.return_value = mock_redis
    
    result = await cache_service.delete("test_key")
    assert result is True
    mock_redis.delete.assert_called_once_with("test_key")

@pytest.mark.asyncio
@patch("backend.cache.service.get_redis")
async def test_cache_graceful_degradation(mock_get_redis, cache_service):
    # Simulate Redis being down (get_redis returns None)
    mock_get_redis.return_value = None
    
    get_result = await cache_service.get("test_key")
    assert get_result is None
    
    set_result = await cache_service.set("test_key", "value")
    assert set_result is False

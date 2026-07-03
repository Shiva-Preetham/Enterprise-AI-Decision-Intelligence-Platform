"""
Tests for Cache Decorators.
"""

import pytest
from unittest.mock import AsyncMock, patch
from backend.cache.decorators import cached, invalidate_cache

# Dummy function to test decorators
async def dummy_service_method(customer_id: str):
    return {"id": customer_id, "name": "John Doe"}

@pytest.mark.asyncio
@patch("backend.cache.decorators._cache_service.get", new_callable=AsyncMock)
@patch("backend.cache.decorators._cache_service.set", new_callable=AsyncMock)
async def test_cached_decorator_miss(mock_set, mock_get):
    # Simulate cache miss
    mock_get.return_value = None
    
    decorated = cached(key_builder=lambda customer_id: f"v1:test:{customer_id}")(dummy_service_method)
    result = await decorated("123")
    
    assert result == {"id": "123", "name": "John Doe"}
    mock_get.assert_called_once_with("v1:test:123")
    mock_set.assert_called_once_with("v1:test:123", {"id": "123", "name": "John Doe"}, ttl=None)

@pytest.mark.asyncio
@patch("backend.cache.decorators._cache_service.get", new_callable=AsyncMock)
@patch("backend.cache.decorators._cache_service.set", new_callable=AsyncMock)
async def test_cached_decorator_hit(mock_set, mock_get):
    # Simulate cache hit
    mock_get.return_value = {"id": "123", "name": "Cached Doe"}
    
    decorated = cached(key_builder=lambda customer_id: f"v1:test:{customer_id}")(dummy_service_method)
    result = await decorated("123")
    
    assert result == {"id": "123", "name": "Cached Doe"}
    mock_get.assert_called_once_with("v1:test:123")
    mock_set.assert_not_called()

@pytest.mark.asyncio
@patch("backend.cache.decorators._cache_service.delete", new_callable=AsyncMock)
async def test_invalidate_cache_static(mock_delete):
    decorated = invalidate_cache(patterns=["v1:test:static"])(dummy_service_method)
    result = await decorated("123")
    
    assert result == {"id": "123", "name": "John Doe"}
    mock_delete.assert_called_once_with("v1:test:static")

@pytest.mark.asyncio
@patch("backend.cache.decorators._cache_service.delete", new_callable=AsyncMock)
async def test_invalidate_cache_dynamic(mock_delete):
    decorated = invalidate_cache(patterns=lambda customer_id: [f"v1:test:{customer_id}"])(dummy_service_method)
    result = await decorated("123")
    
    assert result == {"id": "123", "name": "John Doe"}
    mock_delete.assert_called_once_with("v1:test:123")

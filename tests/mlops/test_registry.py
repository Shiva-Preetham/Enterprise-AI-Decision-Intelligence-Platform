import pytest
import os
import shutil
from unittest.mock import AsyncMock, MagicMock
from mlops.model_registry import ModelRegistry
from mlops.models import ModelRegistryModel

@pytest.mark.asyncio
async def test_model_rollback():
    repo = AsyncMock()
    registry = ModelRegistry(repo, registry_path="/tmp/test_registry")
    
    # Mocking models
    m1 = ModelRegistryModel(version=1, deployment_status="archived")
    m2 = ModelRegistryModel(version=2, deployment_status="production")
    
    repo.get_production_model.return_value = m2
    repo.get_model_by_version.return_value = m1
    
    # Mock update status to just return the updated version
    async def mock_update(version, status):
        if version == 1:
            m1.deployment_status = status
            return m1
        elif version == 2:
            m2.deployment_status = status
            return m2
    
    repo.update_deployment_status = AsyncMock(side_effect=mock_update)
    
    # Execute rollback
    prev_prod = await registry.rollback(target_version=1)
    
    # Assert rollback restores v1 to production and demotes v2
    assert repo.update_deployment_status.call_count == 2
    repo.update_deployment_status.assert_any_call(2, "archived")
    repo.update_deployment_status.assert_any_call(1, "production")
    
    assert prev_prod.version == 2 # Should return the previously-active version
    
    # Cleanup
    if os.path.exists("/tmp/test_registry"):
        shutil.rmtree("/tmp/test_registry")

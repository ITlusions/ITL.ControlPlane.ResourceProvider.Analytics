"""
Integration tests for Notebook CRUD operations

Tests the full workflow: Create → List → Get → Delete
"""

import pytest
import asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from itl_analytics_provider.models.orm import Base, Notebook, NotebookStatus
from itl_analytics_provider.repositories.notebook_repo import NotebookRepository
from itl_analytics_provider.services.notebook_service import NotebookService


@pytest.fixture
async def test_db():
    """Create in-memory SQLite database for testing"""
    
    # Use SQLite for testing (no PostgreSQL needed)
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    yield async_session
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_notebook(test_db):
    """Test notebook creation"""
    
    async with test_db() as session:
        repo = NotebookRepository(session)
        service = NotebookService(repo)
        
        # This will fail trying to reach Container Provider, which is expected
        # In a real test, we'd mock the Container and MinIO clients
        # For now, test the database layer
        
        notebook_data = {
            "subscription_id": "sub-001",
            "resource_group": "rg-test",
            "name": "test-notebook",
            "location": "eastus",
            "kernel": "python3.11",
            "compute_sku": "Standard_D4s_v3",
            "memory_gb": 16,
            "cpu_cores": 4,
            "storage_gb": 100,
            "status": NotebookStatus.CREATING.value,
            "owner_id": "test-user",
            "pod_namespace": "analytics",
        }
        
        notebook = await repo.create(notebook_data)
        
        # Verify notebook was created
        assert notebook.id is not None
        assert notebook.name == "test-notebook"
        assert notebook.status == NotebookStatus.CREATING.value
        assert notebook.owner_id == "test-user"


@pytest.mark.asyncio
async def test_list_notebooks(test_db):
    """Test listing notebooks"""
    
    async with test_db() as session:
        repo = NotebookRepository(session)
        
        # Create test notebooks
        for i in range(3):
            await repo.create({
                "subscription_id": "sub-001",
                "resource_group": "rg-test",
                "name": f"notebook-{i}",
                "location": "eastus",
                "kernel": "python3.11",
                "compute_sku": "Standard_D4s_v3",
                "memory_gb": 16,
                "cpu_cores": 4,
                "storage_gb": 100,
                "status": NotebookStatus.RUNNING.value,
                "owner_id": "test-user",
                "pod_namespace": "analytics",
            })
        
        # List notebooks
        notebooks = await repo.list_by_subscription("sub-001", "rg-test")
        
        assert len(notebooks) == 3
        assert all(nb.subscription_id == "sub-001" for nb in notebooks)


@pytest.mark.asyncio
async def test_get_notebook(test_db):
    """Test retrieving single notebook"""
    
    async with test_db() as session:
        repo = NotebookRepository(session)
        
        # Create notebook
        created = await repo.create({
            "subscription_id": "sub-001",
            "resource_group": "rg-test",
            "name": "my-notebook",
            "location": "eastus",
            "kernel": "python3.11",
            "compute_sku": "Standard_D4s_v3",
            "memory_gb": 16,
            "cpu_cores": 4,
            "storage_gb": 100,
            "status": NotebookStatus.RUNNING.value,
            "owner_id": "test-user",
            "pod_namespace": "analytics",
        })
        
        # Get by ID
        retrieved = await repo.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "my-notebook"
        
        # Get by name
        by_name = await repo.get_by_name("sub-001", "rg-test", "my-notebook")
        
        assert by_name is not None
        assert by_name.id == created.id


@pytest.mark.asyncio
async def test_update_notebook(test_db):
    """Test updating notebook"""
    
    async with test_db() as session:
        repo = NotebookRepository(session)
        
        # Create notebook
        notebook = await repo.create({
            "subscription_id": "sub-001",
            "resource_group": "rg-test",
            "name": "notebook",
            "location": "eastus",
            "kernel": "python3.11",
            "compute_sku": "Standard_D4s_v3",
            "memory_gb": 16,
            "cpu_cores": 4,
            "storage_gb": 100,
            "status": NotebookStatus.CREATING.value,
            "owner_id": "test-user",
            "pod_namespace": "analytics",
        })
        
        # Update
        updated = await repo.update(notebook.id, {
            "status": NotebookStatus.RUNNING.value,
            "pod_name": "notebook-pod-123",
            "storage_bucket": "analytics-bucket",
        })
        
        assert updated.status == NotebookStatus.RUNNING.value
        assert updated.pod_name == "notebook-pod-123"
        assert updated.storage_bucket == "analytics-bucket"


@pytest.mark.asyncio
async def test_delete_notebook(test_db):
    """Test deleting notebook"""
    
    async with test_db() as session:
        repo = NotebookRepository(session)
        
        # Create notebook
        notebook = await repo.create({
            "subscription_id": "sub-001",
            "resource_group": "rg-test",
            "name": "notebook",
            "location": "eastus",
            "kernel": "python3.11",
            "compute_sku": "Standard_D4s_v3",
            "memory_gb": 16,
            "cpu_cores": 4,
            "storage_gb": 100,
            "status": NotebookStatus.RUNNING.value,
            "owner_id": "test-user",
            "pod_namespace": "analytics",
        })
        
        # Delete
        result = await repo.delete(notebook.id)
        
        assert result is True
        
        # Verify deleted
        retrieved = await repo.get_by_id(notebook.id)
        assert retrieved is None


@pytest.mark.asyncio
async def test_notebook_status_updates(test_db):
    """Test status enum transitions"""
    
    async with test_db() as session:
        repo = NotebookRepository(session)
        
        notebook = await repo.create({
            "subscription_id": "sub-001",
            "resource_group": "rg-test",
            "name": "notebook",
            "location": "eastus",
            "status": NotebookStatus.CREATING.value,
            "kernel": "python3.11",
            "compute_sku": "Standard_D4s_v3",
            "memory_gb": 16,
            "cpu_cores": 4,
            "storage_gb": 100,
            "owner_id": "test-user",
            "pod_namespace": "analytics",
        })
        
        # Transition: Creating → Running
        updated = await repo.update_status(notebook.id, NotebookStatus.RUNNING)
        assert updated.status == NotebookStatus.RUNNING.value
        
        # Transition: Running → Stopped
        updated = await repo.update_status(notebook.id, NotebookStatus.STOPPED)
        assert updated.status == NotebookStatus.STOPPED.value
        
        # Transition: Stopped → Terminating
        updated = await repo.update_status(notebook.id, NotebookStatus.TERMINATING)
        assert updated.status == NotebookStatus.TERMINATING.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

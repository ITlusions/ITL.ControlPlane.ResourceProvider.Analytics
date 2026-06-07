"""
Notebook repository - Data access layer
"""

import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.orm import Notebook, NotebookStatus

logger = logging.getLogger(__name__)


class NotebookRepository:
    """Data access for notebooks"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Notebook:
        """Create notebook record"""
        notebook = Notebook(**data)
        self.session.add(notebook)
        await self.session.commit()
        await self.session.refresh(notebook)
        logger.info(f"Created notebook: {notebook.id}")
        return notebook

    async def get_by_id(self, notebook_id: UUID) -> Optional[Notebook]:
        """Get notebook by ID"""
        result = await self.session.execute(
            select(Notebook).where(Notebook.id == notebook_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self, subscription_id: str, resource_group: str, name: str
    ) -> Optional[Notebook]:
        """Get notebook by ARM path"""
        result = await self.session.execute(
            select(Notebook).where(
                Notebook.subscription_id == subscription_id,
                Notebook.resource_group == resource_group,
                Notebook.name == name,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_subscription(
        self, subscription_id: str, resource_group: str
    ) -> List[Notebook]:
        """List all notebooks in resource group"""
        result = await self.session.execute(
            select(Notebook).where(
                Notebook.subscription_id == subscription_id,
                Notebook.resource_group == resource_group,
            )
        )
        return result.scalars().all()

    async def update(self, notebook_id: UUID, data: dict) -> Optional[Notebook]:
        """Update notebook"""
        notebook = await self.get_by_id(notebook_id)
        if not notebook:
            return None
        
        for key, value in data.items():
            if hasattr(notebook, key):
                setattr(notebook, key, value)
        
        await self.session.commit()
        await self.session.refresh(notebook)
        logger.info(f"Updated notebook: {notebook_id}")
        return notebook

    async def delete(self, notebook_id: UUID) -> bool:
        """Delete notebook"""
        notebook = await self.get_by_id(notebook_id)
        if not notebook:
            return False
        
        await self.session.delete(notebook)
        await self.session.commit()
        logger.info(f"Deleted notebook: {notebook_id}")
        return True

    async def update_status(
        self, notebook_id: UUID, status: NotebookStatus
    ) -> Optional[Notebook]:
        """Update notebook status"""
        return await self.update(notebook_id, {"status": status.value})


class SparkClusterRepository:
    """Data access for Spark clusters"""

    def __init__(self, engine):
        self.engine = engine


class AnalyticsJobRepository:
    """Data access for analytics jobs"""

    def __init__(self, engine):
        self.engine = engine


class ModelRepository:
    """Data access for models"""

    def __init__(self, engine):
        self.engine = engine


class DatasetRepository:
    """Data access for datasets"""

    def __init__(self, engine):
        self.engine = engine

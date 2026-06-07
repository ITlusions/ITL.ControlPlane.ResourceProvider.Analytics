"""
Repository layer for Dataset resources
"""

from typing import Optional, List
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from itl_analytics_provider.models.orm import Dataset

logger = logging.getLogger(__name__)


class DatasetRepository:
    """Data access layer for datasets"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Dataset:
        """Create new dataset record"""
        dataset = Dataset(**data)
        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)
        logger.info(f"Registered dataset: {dataset.id}", extra={"dataset_id": str(dataset.id)})
        return dataset

    async def get_by_id(self, dataset_id: UUID) -> Optional[Dataset]:
        """Get dataset by ID"""
        stmt = select(Dataset).where(Dataset.id == dataset_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_subscription(
        self, subscription_id: str, resource_group: str
    ) -> List[Dataset]:
        """List all datasets in resource group"""
        stmt = select(Dataset).where(
            (Dataset.subscription_id == subscription_id)
            & (Dataset.resource_group == resource_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, dataset_id: UUID, data: dict) -> Optional[Dataset]:
        """Update dataset metadata"""
        dataset = await self.get_by_id(dataset_id)
        if not dataset:
            return None

        for key, value in data.items():
            setattr(dataset, key, value)

        await self.session.commit()
        await self.session.refresh(dataset)
        return dataset

    async def delete(self, dataset_id: UUID) -> bool:
        """Delete dataset record"""
        dataset = await self.get_by_id(dataset_id)
        if not dataset:
            return False

        await self.session.delete(dataset)
        await self.session.commit()
        logger.info(f"Deleted dataset: {dataset_id}")
        return True

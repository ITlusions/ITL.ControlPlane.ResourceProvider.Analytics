"""
Repository layer for Inference Endpoint resources
"""

from typing import Optional, List
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from itl_analytics_provider.models.orm import InferenceEndpoint

logger = logging.getLogger(__name__)


class InferenceEndpointRepository:
    """Data access layer for inference endpoints"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> InferenceEndpoint:
        """Create new endpoint record"""
        endpoint = InferenceEndpoint(**data)
        self.session.add(endpoint)
        await self.session.commit()
        await self.session.refresh(endpoint)
        logger.info(f"Created endpoint: {endpoint.id}", extra={"endpoint_id": str(endpoint.id)})
        return endpoint

    async def get_by_id(self, endpoint_id: UUID) -> Optional[InferenceEndpoint]:
        """Get endpoint by ID"""
        stmt = select(InferenceEndpoint).where(InferenceEndpoint.id == endpoint_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_subscription(
        self, subscription_id: str, resource_group: str
    ) -> List[InferenceEndpoint]:
        """List all endpoints in resource group"""
        stmt = select(InferenceEndpoint).where(
            (InferenceEndpoint.subscription_id == subscription_id)
            & (InferenceEndpoint.resource_group == resource_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, endpoint_id: UUID, data: dict) -> Optional[InferenceEndpoint]:
        """Update endpoint properties"""
        endpoint = await self.get_by_id(endpoint_id)
        if not endpoint:
            return None

        for key, value in data.items():
            setattr(endpoint, key, value)

        await self.session.commit()
        await self.session.refresh(endpoint)
        return endpoint

    async def delete(self, endpoint_id: UUID) -> bool:
        """Delete endpoint record"""
        endpoint = await self.get_by_id(endpoint_id)
        if not endpoint:
            return False

        await self.session.delete(endpoint)
        await self.session.commit()
        logger.info(f"Deleted endpoint: {endpoint_id}")
        return True

    async def update_status(self, endpoint_id: UUID, status: str) -> Optional[InferenceEndpoint]:
        """Update endpoint status"""
        return await self.update(endpoint_id, {"status": status})

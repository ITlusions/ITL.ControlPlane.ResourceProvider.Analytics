"""
Repository layer for Analytics Job resources
"""

from typing import Optional, List
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from itl_analytics_provider.models.orm import AnalyticsJob

logger = logging.getLogger(__name__)


class AnalyticsJobRepository:
    """Data access layer for analytics jobs"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> AnalyticsJob:
        """Create new job record"""
        job = AnalyticsJob(**data)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        logger.info(f"Created analytics job: {job.id}", extra={"job_id": str(job.id)})
        return job

    async def get_by_id(self, job_id: UUID) -> Optional[AnalyticsJob]:
        """Get job by ID"""
        stmt = select(AnalyticsJob).where(AnalyticsJob.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_subscription(
        self, subscription_id: str, resource_group: str
    ) -> List[AnalyticsJob]:
        """List all jobs in resource group"""
        stmt = select(AnalyticsJob).where(
            (AnalyticsJob.subscription_id == subscription_id)
            & (AnalyticsJob.resource_group == resource_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, job_id: UUID, data: dict) -> Optional[AnalyticsJob]:
        """Update job properties"""
        job = await self.get_by_id(job_id)
        if not job:
            return None

        for key, value in data.items():
            setattr(job, key, value)

        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def delete(self, job_id: UUID) -> bool:
        """Delete job record"""
        job = await self.get_by_id(job_id)
        if not job:
            return False

        await self.session.delete(job)
        await self.session.commit()
        logger.info(f"Deleted job: {job_id}")
        return True

    async def update_status(self, job_id: UUID, status: str) -> Optional[AnalyticsJob]:
        """Update job status"""
        return await self.update(job_id, {"status": status})

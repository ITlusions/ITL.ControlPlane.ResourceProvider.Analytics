"""
Repository layer for Spark Cluster resources

Provides data access abstraction for SparkCluster ORM model
"""

from typing import Optional, List
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from itl_analytics_provider.models.orm import SparkCluster

logger = logging.getLogger(__name__)


class SparkClusterRepository:
    """Data access layer for Spark clusters"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> SparkCluster:
        """Create new Spark cluster record

        Args:
            data: Cluster data dict

        Returns:
            Created SparkCluster record
        """
        cluster = SparkCluster(**data)
        self.session.add(cluster)
        await self.session.commit()
        await self.session.refresh(cluster)
        logger.info(f"Created Spark cluster: {cluster.id}", extra={"cluster_id": str(cluster.id)})
        return cluster

    async def get_by_id(self, cluster_id: UUID) -> Optional[SparkCluster]:
        """Get cluster by ID"""
        stmt = select(SparkCluster).where(SparkCluster.id == cluster_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(
        self, subscription_id: str, resource_group: str, name: str
    ) -> Optional[SparkCluster]:
        """Get cluster by ARM path (subscription/RG/name)"""
        stmt = select(SparkCluster).where(
            (SparkCluster.subscription_id == subscription_id)
            & (SparkCluster.resource_group == resource_group)
            & (SparkCluster.name == name)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_subscription(
        self, subscription_id: str, resource_group: str
    ) -> List[SparkCluster]:
        """List all clusters in resource group"""
        stmt = select(SparkCluster).where(
            (SparkCluster.subscription_id == subscription_id)
            & (SparkCluster.resource_group == resource_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, cluster_id: UUID, data: dict) -> Optional[SparkCluster]:
        """Update cluster properties"""
        cluster = await self.get_by_id(cluster_id)
        if not cluster:
            return None

        for key, value in data.items():
            setattr(cluster, key, value)

        await self.session.commit()
        await self.session.refresh(cluster)
        logger.info(f"Updated Spark cluster: {cluster_id}")
        return cluster

    async def delete(self, cluster_id: UUID) -> bool:
        """Delete cluster record"""
        cluster = await self.get_by_id(cluster_id)
        if not cluster:
            return False

        await self.session.delete(cluster)
        await self.session.commit()
        logger.info(f"Deleted Spark cluster: {cluster_id}")
        return True

    async def update_status(self, cluster_id: UUID, status: str) -> Optional[SparkCluster]:
        """Update cluster status"""
        return await self.update(cluster_id, {"status": status})

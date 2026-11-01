"""
Spark Cluster handler mixin — business logic for Spark resources

Follows Core provider pattern with engine-based session management.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from itl_controlplane_sdk.analytics import SparkCluster

logger = logging.getLogger(__name__)


class SparkClusterHandlerMixin:
    """Handler for Spark cluster operations"""

    async def _create_spark_cluster(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        properties: Dict[str, Any],
        owner_id: str,
    ) -> SparkCluster:
        """Create Spark cluster"""
        logger.info(
            f"Creating Spark cluster {name}",
            extra={
                "subscription": subscription_id,
                "resource_group": resource_group,
                "owner": owner_id,
            },
        )

        async with self.engine.session() as session:
            from ..repositories.spark_repo import SparkClusterRepository

            repo = SparkClusterRepository(session)
            cluster = await repo.create(
                {
                    "subscription_id": subscription_id,
                    "resource_group": resource_group,
                    "name": name,
                    "location": location,
                    "status": "Creating",
                    "owner_id": owner_id,
                    "cluster_size": properties.get("clusterSize", 3),
                    "spark_version": properties.get("sparkVersion", "3.5.0"),
                    "compute_sku": properties.get("computeSku", "standard"),
                }
            )
            return cluster

    async def _get_spark_cluster(
        self, subscription_id: str, resource_group: str, name: str
    ) -> Optional[SparkCluster]:
        """Get Spark cluster by name"""
        async with self.engine.session() as session:
            from ..repositories.spark_repo import SparkClusterRepository

            repo = SparkClusterRepository(session)
            return await repo.get_by_name(subscription_id, resource_group, name)

    async def _list_spark_clusters(
        self, subscription_id: str, resource_group: str
    ) -> List[SparkCluster]:
        """List Spark clusters"""
        async with self.engine.session() as session:
            from ..repositories.spark_repo import SparkClusterRepository

            repo = SparkClusterRepository(session)
            return await repo.list_by_subscription(subscription_id, resource_group)

    async def _delete_spark_cluster(
        self, subscription_id: str, resource_group: str, name: str
    ) -> bool:
        """Delete Spark cluster"""
        async with self.engine.session() as session:
            from ..repositories.spark_repo import SparkClusterRepository

            repo = SparkClusterRepository(session)
            cluster = await repo.get_by_name(subscription_id, resource_group, name)
            if not cluster:
                return False
            return await repo.delete(cluster.id)

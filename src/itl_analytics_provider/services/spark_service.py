"""
Service layer for Spark Cluster resources

Handles business logic for cluster creation, deletion, and lifecycle
"""

import logging
from uuid import UUID
from typing import Optional, List
from datetime import datetime

from itl_analytics_provider.repositories.spark_repo import SparkClusterRepository
from itl_analytics_provider.models.orm import SparkClusterStatus

logger = logging.getLogger(__name__)


class SparkClusterService:
    """Business logic for Spark clusters"""

    def __init__(self, repo: SparkClusterRepository):
        self.repo = repo

    async def create_cluster(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        properties: dict,
        owner_id: str = "default-user",
    ):
        """Create new Spark cluster

        Args:
            subscription_id: Subscription ID
            resource_group: Resource group name
            name: Cluster name
            location: Azure region
            properties: Cluster properties dict
            owner_id: Owner user ID

        Returns:
            Created SparkCluster record

        TODO (Phase 2):
            - Call Container Provider to create driver pod
            - Call Container Provider to create worker pods (worker_count)
            - Wait for all pods to be Running
            - Configure Spark master/worker networking
            - Setup cluster monitoring
        """
        logger.info(
            f"create_cluster: name={name}, location={location}",
            extra={
                "subscription": subscription_id,
                "resource_group": resource_group,
                "owner": owner_id,
            },
        )

        # Create database record
        cluster_data = {
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "name": name,
            "location": location,
            "status": SparkClusterStatus.Creating,
            "owner_id": owner_id,
            "driver_cpu": properties.get("driver_cpu", 8),
            "driver_memory_gb": properties.get("driver_memory_gb", 32),
            "worker_count": properties.get("worker_count", 3),
            "worker_cpu": properties.get("worker_cpu", 16),
            "worker_memory_gb": properties.get("worker_memory_gb", 64),
            "worker_gpus": properties.get("worker_gpus", 4),
        }

        cluster = await self.repo.create(cluster_data)
        logger.info(f"Cluster created: {cluster.id}")

        # TODO: Create pods via Container Provider
        # TODO: Wait for running
        # TODO: Setup networking
        # TODO: Update status to Running

        return cluster

    async def delete_cluster(self, cluster_id: UUID) -> bool:
        """Delete Spark cluster

        Args:
            cluster_id: Cluster ID to delete

        Returns:
            True if deleted, False if not found

        TODO (Phase 2):
            - Update status to Terminating
            - Call Container Provider to delete driver pod
            - Call Container Provider to delete all worker pods
            - Cleanup cluster resources
            - Delete database record
        """
        logger.info(f"delete_cluster: cluster_id={cluster_id}")

        cluster = await self.repo.get_by_id(cluster_id)
        if not cluster:
            return False

        # Update status to Terminating
        await self.repo.update_status(cluster_id, SparkClusterStatus.Terminating)

        # TODO: Delete pods via Container Provider
        # TODO: Cleanup resources

        # Delete from database
        result = await self.repo.delete(cluster_id)
        logger.info(f"Cluster deleted: {cluster_id}")
        return result

    async def get_cluster(self, subscription_id: str, resource_group: str, name: str):
        """Get cluster by name"""
        logger.info(
            f"get_cluster: name={name}",
            extra={"subscription": subscription_id, "resource_group": resource_group},
        )
        return await self.repo.get_by_name(subscription_id, resource_group, name)

    async def list_clusters(self, subscription_id: str, resource_group: str) -> List:
        """List all clusters in resource group"""
        logger.info(
            f"list_clusters",
            extra={"subscription": subscription_id, "resource_group": resource_group},
        )
        return await self.repo.list_by_subscription(subscription_id, resource_group)

    async def update_cluster_status(self, cluster_id: UUID, status: str):
        """Update cluster status"""
        logger.info(f"update_status: cluster_id={cluster_id}, status={status}")
        return await self.repo.update_status(cluster_id, status)

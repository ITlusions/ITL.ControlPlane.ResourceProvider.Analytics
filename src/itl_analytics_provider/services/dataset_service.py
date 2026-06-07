"""
Service layer for Dataset resources
"""

import logging
from uuid import UUID
from typing import List

from itl_analytics_provider.repositories.dataset_repo import DatasetRepository

logger = logging.getLogger(__name__)


class DatasetService:
    """Business logic for datasets"""

    def __init__(self, repo: DatasetRepository):
        self.repo = repo

    async def register_dataset(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        data_location: str,
        owner_id: str = "default-user",
    ):
        """Register new dataset

        TODO (Phase 2):
            - Validate data location (S3/MinIO path)
            - Analyze schema
            - Calculate statistics
            - Setup data lineage
        """
        logger.info(
            f"register_dataset: name={name}, location={data_location}",
            extra={"subscription": subscription_id, "resource_group": resource_group},
        )

        dataset_data = {
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "name": name,
            "location": location,
            "data_location": data_location,
            "owner_id": owner_id,
        }

        dataset = await self.repo.create(dataset_data)
        logger.info(f"Dataset registered: {dataset.id}")

        # TODO: Analyze schema
        # TODO: Calculate statistics
        # TODO: Setup lineage tracking

        return dataset

    async def delete_dataset(self, dataset_id: UUID) -> bool:
        """Delete dataset record"""
        logger.info(f"delete_dataset: dataset_id={dataset_id}")
        return await self.repo.delete(dataset_id)

    async def list_datasets(self, subscription_id: str, resource_group: str) -> List:
        """List all datasets in resource group"""
        logger.info(
            f"list_datasets",
            extra={"subscription": subscription_id, "resource_group": resource_group},
        )
        return await self.repo.list_by_subscription(subscription_id, resource_group)

"""
Dataset handler mixin — business logic for dataset resources

Follows Core provider pattern with engine-based session management.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from itl_controlplane_sdk.analytics import Dataset

logger = logging.getLogger(__name__)


class DatasetHandlerMixin:
    """Handler for dataset operations"""

    async def _create_dataset(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        properties: Dict[str, Any],
        owner_id: str,
    ) -> Dataset:
        """Create dataset"""
        logger.info(
            f"Creating dataset {name}",
            extra={
                "subscription": subscription_id,
                "resource_group": resource_group,
                "owner": owner_id,
            },
        )

        async with self.engine.session() as session:
            from ..repositories.dataset_repo import DatasetRepository

            repo = DatasetRepository(session)
            dataset = await repo.create(
                {
                    "subscription_id": subscription_id,
                    "resource_group": resource_group,
                    "name": name,
                    "location": location,
                    "status": "Available",
                    "owner_id": owner_id,
                    "dataset_type": properties.get("datasetType", "tabular"),
                    "storage_account": properties.get("storageAccount"),
                    "storage_path": properties.get("storagePath"),
                }
            )
            return dataset

    async def _get_dataset(
        self, subscription_id: str, resource_group: str, name: str
    ) -> Optional[Dataset]:
        """Get dataset by name"""
        async with self.engine.session() as session:
            from ..repositories.dataset_repo import DatasetRepository

            repo = DatasetRepository(session)
            return await repo.get_by_name(subscription_id, resource_group, name)

    async def _list_datasets(
        self, subscription_id: str, resource_group: str
    ) -> List[Dataset]:
        """List datasets"""
        async with self.engine.session() as session:
            from ..repositories.dataset_repo import DatasetRepository

            repo = DatasetRepository(session)
            return await repo.list_by_subscription(subscription_id, resource_group)

    async def _delete_dataset(
        self, subscription_id: str, resource_group: str, name: str
    ) -> bool:
        """Delete dataset"""
        async with self.engine.session() as session:
            from ..repositories.dataset_repo import DatasetRepository

            repo = DatasetRepository(session)
            dataset = await repo.get_by_name(subscription_id, resource_group, name)
            if not dataset:
                return False
            return await repo.delete(dataset.id)

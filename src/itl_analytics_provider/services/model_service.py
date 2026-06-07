"""
Service layer for Model Registry resources
"""

import logging
from uuid import UUID
from typing import List

from itl_analytics_provider.repositories.model_repo import ModelRepository

logger = logging.getLogger(__name__)


class ModelService:
    """Business logic for model registry"""

    def __init__(self, repo: ModelRepository):
        self.repo = repo

    async def register_model(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        framework: str,
        version: str,
        owner_id: str = "default-user",
    ):
        """Register new model in registry

        TODO (Phase 3):
            - Validate model artifact
            - Extract and store metadata
            - Setup model versioning
            - Create MLflow tracking entry
            - Setup artifact storage
        """
        logger.info(
            f"register_model: name={name}, framework={framework}, version={version}",
            extra={"subscription": subscription_id, "resource_group": resource_group},
        )

        model_data = {
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "name": name,
            "location": location,
            "framework": framework,
            "version": version,
            "owner_id": owner_id,
        }

        model = await self.repo.create(model_data)
        logger.info(f"Model registered: {model.id}")

        # TODO: Store in MLflow registry
        # TODO: Setup versioning
        # TODO: Create audit trail

        return model

    async def delete_model(self, model_id: UUID) -> bool:
        """Delete model record"""
        logger.info(f"delete_model: model_id={model_id}")
        return await self.repo.delete(model_id)

    async def list_models(self, subscription_id: str, resource_group: str) -> List:
        """List all models in resource group"""
        logger.info(
            f"list_models",
            extra={"subscription": subscription_id, "resource_group": resource_group},
        )
        return await self.repo.list_by_subscription(subscription_id, resource_group)

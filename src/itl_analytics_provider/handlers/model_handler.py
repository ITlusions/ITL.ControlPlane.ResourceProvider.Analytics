"""
Model handler mixin — business logic for model registry resources

Follows Core provider pattern with engine-based session management.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from itl_controlplane_sdk.analytics import Model

logger = logging.getLogger(__name__)


class ModelHandlerMixin:
    """Handler for model registry operations"""

    async def _create_model(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        properties: Dict[str, Any],
        owner_id: str,
    ) -> Model:
        """Create model registry entry"""
        logger.info(
            f"Creating model {name}",
            extra={
                "subscription": subscription_id,
                "resource_group": resource_group,
                "owner": owner_id,
            },
        )

        async with self.engine.session() as session:
            from ..repositories.model_repo import ModelRepository

            repo = ModelRepository(session)
            model = await repo.create(
                {
                    "subscription_id": subscription_id,
                    "resource_group": resource_group,
                    "name": name,
                    "location": location,
                    "status": "Registered",
                    "owner_id": owner_id,
                    "model_type": properties.get("modelType", "custom"),
                    "framework": properties.get("framework", "pytorch"),
                    "version": properties.get("version", "1.0"),
                }
            )
            return model

    async def _get_model(
        self, subscription_id: str, resource_group: str, name: str
    ) -> Optional[Model]:
        """Get model by name"""
        async with self.engine.session() as session:
            from ..repositories.model_repo import ModelRepository

            repo = ModelRepository(session)
            return await repo.get_by_name(subscription_id, resource_group, name)

    async def _list_models(
        self, subscription_id: str, resource_group: str
    ) -> List[Model]:
        """List models"""
        async with self.engine.session() as session:
            from ..repositories.model_repo import ModelRepository

            repo = ModelRepository(session)
            return await repo.list_by_subscription(subscription_id, resource_group)

    async def _delete_model(
        self, subscription_id: str, resource_group: str, name: str
    ) -> bool:
        """Delete model"""
        async with self.engine.session() as session:
            from ..repositories.model_repo import ModelRepository

            repo = ModelRepository(session)
            model = await repo.get_by_name(subscription_id, resource_group, name)
            if not model:
                return False
            return await repo.delete(model.id)

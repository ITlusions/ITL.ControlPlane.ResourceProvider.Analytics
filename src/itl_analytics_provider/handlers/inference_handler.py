"""
Inference Endpoint handler mixin — business logic for inference endpoint resources

Follows Core provider pattern with engine-based session management.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from itl_controlplane_sdk.analytics import InferenceEndpoint

logger = logging.getLogger(__name__)


class InferenceEndpointHandlerMixin:
    """Handler for inference endpoint operations"""

    async def _create_inference_endpoint(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        properties: Dict[str, Any],
        owner_id: str,
    ) -> InferenceEndpoint:
        """Create inference endpoint"""
        logger.info(
            f"Creating inference endpoint {name}",
            extra={
                "subscription": subscription_id,
                "resource_group": resource_group,
                "owner": owner_id,
            },
        )

        async with self.engine.session() as session:
            from ..repositories.inference_repo import InferenceEndpointRepository

            repo = InferenceEndpointRepository(session)
            endpoint = await repo.create(
                {
                    "subscription_id": subscription_id,
                    "resource_group": resource_group,
                    "name": name,
                    "location": location,
                    "status": "Creating",
                    "owner_id": owner_id,
                    "model_id": properties.get("modelId"),
                    "compute_sku": properties.get("computeSku", "standard"),
                    "instance_count": properties.get("instanceCount", 1),
                }
            )
            return endpoint

    async def _get_inference_endpoint(
        self, subscription_id: str, resource_group: str, name: str
    ) -> Optional[InferenceEndpoint]:
        """Get inference endpoint by name"""
        async with self.engine.session() as session:
            from ..repositories.inference_repo import InferenceEndpointRepository

            repo = InferenceEndpointRepository(session)
            return await repo.get_by_name(subscription_id, resource_group, name)

    async def _list_inference_endpoints(
        self, subscription_id: str, resource_group: str
    ) -> List[InferenceEndpoint]:
        """List inference endpoints"""
        async with self.engine.session() as session:
            from ..repositories.inference_repo import InferenceEndpointRepository

            repo = InferenceEndpointRepository(session)
            return await repo.list_by_subscription(subscription_id, resource_group)

    async def _delete_inference_endpoint(
        self, subscription_id: str, resource_group: str, name: str
    ) -> bool:
        """Delete inference endpoint"""
        async with self.engine.session() as session:
            from ..repositories.inference_repo import InferenceEndpointRepository

            repo = InferenceEndpointRepository(session)
            endpoint = await repo.get_by_name(subscription_id, resource_group, name)
            if not endpoint:
                return False
            return await repo.delete(endpoint.id)

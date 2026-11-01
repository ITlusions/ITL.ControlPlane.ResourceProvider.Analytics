"""
Main Analytics Provider class extending SDK ResourceProvider

Manages analytics resources:
- Notebooks (Jupyter sessions)
- Spark Clusters (distributed compute)
- Analytics Jobs (workflows)
- Models (ML registry)
- Datasets (data catalog)
- Inference Endpoints (model serving)
"""

from typing import Any, Dict, List
from itl_controlplane_sdk import (
    ProviderContext,
    ResourceNotFoundError,
    ResourceRequest,
    ResourceResponse,
)
from itl_controlplane_sdk.providers import ResourceProvider
from itl_controlplane_sdk.persistence import SQLAlchemyStorageEngine

from .handlers import (
    NotebookHandlerMixin,
    SparkClusterHandlerMixin,
    AnalyticsJobHandlerMixin,
    ModelHandlerMixin,
    DatasetHandlerMixin,
    InferenceEndpointHandlerMixin,
)

# resource_type -> (create_method, get_method, delete_method) on AnalyticsProvider,
# one set per handler mixin. All six mixins share the same
# (subscription_id, resource_group, name, location, properties, owner_id) /
# (subscription_id, resource_group, name) call shape — verified across all six
# handler files before relying on it here.
_RESOURCE_HANDLERS: Dict[str, tuple] = {
    "notebooks": ("_create_notebook", "_get_notebook", "_delete_notebook"),
    "sparkClusters": ("_create_spark_cluster", "_get_spark_cluster", "_delete_spark_cluster"),
    "analyticsJobs": ("_create_analytics_job", "_get_analytics_job", "_delete_analytics_job"),
    "models": ("_create_model", "_get_model", "_delete_model"),
    "datasets": ("_create_dataset", "_get_dataset", "_delete_dataset"),
    "inferenceEndpoints": ("_create_inference_endpoint", "_get_inference_endpoint", "_delete_inference_endpoint"),
}


class AnalyticsProvider(
    NotebookHandlerMixin,
    SparkClusterHandlerMixin,
    AnalyticsJobHandlerMixin,
    ModelHandlerMixin,
    DatasetHandlerMixin,
    InferenceEndpointHandlerMixin,
    ResourceProvider,
):
    """
    Analytics Resource Provider

    Namespace: ITL.Analytics
    Version: 2024-06-01
    
    Manages:
    - notebooks
    - sparkClusters
    - analyticsJobs
    - models
    - datasets
    - inferenceEndpoints
    """

    def __init__(self, engine: SQLAlchemyStorageEngine):
        """
        Initialize Analytics Provider

        Args:
            engine: Storage engine for persistence
        """
        super().__init__(provider_namespace="ITL.Analytics")
        self.engine = engine
        self.supported_resource_types = self.get_resource_types()

    @property
    def namespace(self) -> str:
        """Provider namespace (resource type prefix)"""
        return "ITL.Analytics"

    @property
    def version(self) -> str:
        """API version"""
        return "2024-06-01"

    def get_resource_types(self) -> List[str]:
        """
        Get supported resource types

        Returns:
            List of resource type names
        """
        return [
            "notebooks",
            "sparkClusters",
            "analyticsJobs",
            "models",
            "datasets",
            "inferenceEndpoints",
        ]

    async def validate_resource(self, resource_type: str, resource: dict) -> bool:
        """
        Validate resource before creation

        Args:
            resource_type: Type of resource
            resource: Resource definition

        Returns:
            True if valid
        """
        # TODO: Implement resource validation
        return True

    async def authorize_action(
        self, action: str, resource_type: str, user_id: str
    ) -> bool:
        """
        Check if user is authorized for action

        Args:
            action: Action (create, read, update, delete)
            resource_type: Type of resource
            user_id: User ID

        Returns:
            True if authorized
        """
        # TODO: Implement RBAC check via BrainCell
        return True

    # ============================================================
    # ResourceProvider abstract contract — dispatches to the
    # resource-type-specific handler mixin based on request.resource_type.
    # ============================================================

    def _handler_names(self, resource_type: str) -> tuple:
        try:
            return _RESOURCE_HANDLERS[resource_type]
        except KeyError:
            raise ResourceNotFoundError(
                f"Unknown resource type '{resource_type}' for provider {self.namespace}"
            )

    def _orm_to_properties(self, obj: Any) -> Dict[str, Any]:
        """Generic SQLAlchemy ORM instance -> JSON-safe dict, for ResourceResponse.properties."""
        properties: Dict[str, Any] = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            if value is None or isinstance(value, (str, int, float, bool)):
                properties[column.name] = value
            else:
                properties[column.name] = str(value)
        return properties

    def _to_resource_response(self, request: ResourceRequest, obj: Any) -> ResourceResponse:
        resource_id = (
            f"/subscriptions/{request.subscription_id}"
            f"/resourceGroups/{request.resource_group}"
            f"/providers/{self.namespace}/{request.resource_type}/{request.resource_name}"
        )
        return ResourceResponse(
            id=resource_id,
            name=request.resource_name,
            type=f"{self.namespace}/{request.resource_type}",
            location=request.location,
            properties=self._orm_to_properties(obj),
        )

    async def _do_create_or_update_resource(
        self, request: ResourceRequest, context: ProviderContext
    ) -> ResourceResponse:
        create_method_name, _, _ = self._handler_names(request.resource_type)
        create_method = getattr(self, create_method_name)
        obj = await create_method(
            subscription_id=request.subscription_id,
            resource_group=request.resource_group,
            name=request.resource_name,
            location=request.location,
            properties=request.body,
            owner_id=context.user_id,
        )
        return self._to_resource_response(request, obj)

    async def _do_get_resource(
        self, request: ResourceRequest, context: ProviderContext
    ) -> ResourceResponse:
        _, get_method_name, _ = self._handler_names(request.resource_type)
        get_method = getattr(self, get_method_name)
        obj = await get_method(
            request.subscription_id, request.resource_group, request.resource_name
        )
        if obj is None:
            raise ResourceNotFoundError(
                f"{request.resource_type} '{request.resource_name}' not found"
            )
        return self._to_resource_response(request, obj)

    async def _do_delete_resource(
        self, request: ResourceRequest, context: ProviderContext
    ) -> ResourceResponse:
        _, _, delete_method_name = self._handler_names(request.resource_type)
        delete_method = getattr(self, delete_method_name)
        deleted = await delete_method(
            request.subscription_id, request.resource_group, request.resource_name
        )
        if not deleted:
            raise ResourceNotFoundError(
                f"{request.resource_type} '{request.resource_name}' not found"
            )
        resource_id = (
            f"/subscriptions/{request.subscription_id}"
            f"/resourceGroups/{request.resource_group}"
            f"/providers/{self.namespace}/{request.resource_type}/{request.resource_name}"
        )
        return ResourceResponse(
            id=resource_id,
            name=request.resource_name,
            type=f"{self.namespace}/{request.resource_type}",
            location=request.location,
            properties={},
        )

"""
Routes for Inference Endpoint resources

Provides inference endpoint management endpoints following Core provider pattern.
"""

from fastapi import APIRouter, HTTPException, status
from structlog import get_logger

from ..models import InferenceEndpointRequest, InferenceEndpointResponse

logger = get_logger()


def setup_inference_endpoints_routes(app, engine, provider) -> APIRouter:
    """
    Setup inference endpoint routes

    Endpoints:
    - POST   /inferenceEndpoints           - Create endpoint
    - GET    /inferenceEndpoints           - List endpoints
    - GET    /inferenceEndpoints/{name}    - Get endpoint
    - DELETE /inferenceEndpoints/{name}    - Delete endpoint

    Uses provider handler methods (Core provider pattern):
    - provider._create_inference_endpoint()
    - provider._get_inference_endpoint()
    - provider._list_inference_endpoints()
    - provider._delete_inference_endpoint()
    """
    router = APIRouter(tags=["inferenceEndpoints"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/inferenceEndpoints",
        response_model=InferenceEndpointResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_inference_endpoint(
        subscription_id: str, resource_group: str, request: InferenceEndpointRequest
    ):
        """Create inference endpoint"""
        logger.info(
            "create_inference_endpoint",
            subscription_id=subscription_id,
            resource_group=resource_group,
            name=request.name,
        )

        try:
            owner_id = "default-user"

            endpoint = await provider._create_inference_endpoint(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                properties=request.properties.dict(),
                owner_id=owner_id,
            )

            return InferenceEndpointResponse(
                id=endpoint.id,
                name=endpoint.name,
                location=endpoint.location,
                status=endpoint.status,
                created_at=endpoint.created_at,
                updated_at=endpoint.updated_at,
                owner_id=endpoint.owner_id,
                properties={
                    "modelId": endpoint.model_id,
                    "computeSku": endpoint.compute_sku,
                    "instanceCount": endpoint.instance_count,
                },
            )

        except Exception as e:
            logger.error("create_inference_endpoint_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/inferenceEndpoints",
        status_code=status.HTTP_200_OK,
    )
    async def list_inference_endpoints(subscription_id: str, resource_group: str):
        """List inference endpoints in resource group"""
        logger.info(
            "list_inference_endpoints",
            subscription_id=subscription_id,
            resource_group=resource_group,
        )

        try:
            endpoints = await provider._list_inference_endpoints(
                subscription_id, resource_group
            )

            return {
                "value": [
                    InferenceEndpointResponse(
                        id=e.id,
                        name=e.name,
                        location=e.location,
                        status=e.status,
                        created_at=e.created_at,
                        updated_at=e.updated_at,
                        owner_id=e.owner_id,
                        properties={
                            "modelId": e.model_id,
                            "computeSku": e.compute_sku,
                            "instanceCount": e.instance_count,
                        },
                    )
                    for e in endpoints
                ]
            }

        except Exception as e:
            logger.error("list_inference_endpoints_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/inferenceEndpoints/{endpoint_name}",
        response_model=InferenceEndpointResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_inference_endpoint(
        subscription_id: str, resource_group: str, endpoint_name: str
    ):
        """Get inference endpoint details"""
        logger.info(
            "get_inference_endpoint",
            subscription_id=subscription_id,
            resource_group=resource_group,
            endpoint_name=endpoint_name,
        )

        try:
            endpoint = await provider._get_inference_endpoint(
                subscription_id, resource_group, endpoint_name
            )

            if not endpoint:
                raise HTTPException(status_code=404, detail="Endpoint not found")

            return InferenceEndpointResponse(
                id=endpoint.id,
                name=endpoint.name,
                location=endpoint.location,
                status=endpoint.status,
                created_at=endpoint.created_at,
                updated_at=endpoint.updated_at,
                owner_id=endpoint.owner_id,
                properties={
                    "modelId": endpoint.model_id,
                    "computeSku": endpoint.compute_sku,
                    "instanceCount": endpoint.instance_count,
                },
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("get_inference_endpoint_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/inferenceEndpoints/{endpoint_name}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_inference_endpoint(
        subscription_id: str, resource_group: str, endpoint_name: str
    ):
        """Delete inference endpoint"""
        logger.info(
            "delete_inference_endpoint",
            subscription_id=subscription_id,
            resource_group=resource_group,
            endpoint_name=endpoint_name,
        )

        try:
            result = await provider._delete_inference_endpoint(
                subscription_id, resource_group, endpoint_name
            )

            if not result:
                raise HTTPException(status_code=404, detail="Endpoint not found")

            return None

        except HTTPException:
            raise
        except Exception as e:
            logger.error("delete_inference_endpoint_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    return router

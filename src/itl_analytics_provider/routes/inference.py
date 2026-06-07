"""
FastAPI routes for Inference Endpoint resources
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from itl_analytics_provider.models.notebook import InferenceEndpointRequest, InferenceEndpointResponse
from itl_analytics_provider.services.inference_service import InferenceEndpointService
from itl_analytics_provider.repositories.inference_repo import InferenceEndpointRepository
from itl_analytics_provider.core.database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Inference Endpoints"])


@router.post(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/inferenceEndpoints",
    response_model=InferenceEndpointResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_inference_endpoint(
    subscription_id: str,
    resource_group: str,
    request: InferenceEndpointRequest,
):
    """Deploy model as inference endpoint

    TODO (Phase 3):
        - Create Kubernetes deployment
        - Setup REST service
        - Configure auto-scaling
        - Return endpoint URL
    """
    logger.info(
        f"POST /inferenceEndpoints: name={request.name}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = InferenceEndpointRepository(session)
            service = InferenceEndpointService(repo)

            endpoint = await service.create_endpoint(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                model_id=request.properties.model_id,
                replica_count=request.properties.replica_count,
            )

            return InferenceEndpointResponse(
                id=endpoint.id,
                name=endpoint.name,
                type="ITL.Analytics/inferenceEndpoints",
                status=endpoint.status,
                properties={
                    "model_id": endpoint.model_id,
                    "replica_count": endpoint.replica_count,
                    "cpu_per_replica": endpoint.cpu_per_replica,
                    "memory_gb_per_replica": endpoint.memory_gb_per_replica,
                },
                created_at=endpoint.created_at,
                url=endpoint.url,
            )

    except Exception as e:
        logger.error(f"Failed to create endpoint: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/inferenceEndpoints"
)
async def list_inference_endpoints(subscription_id: str, resource_group: str):
    """List inference endpoints in resource group"""
    logger.info(
        f"GET /inferenceEndpoints",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = InferenceEndpointRepository(session)
            service = InferenceEndpointService(repo)
            endpoints = await service.list_endpoints(subscription_id, resource_group)

            return {
                "value": [
                    InferenceEndpointResponse(
                        id=e.id,
                        name=e.name,
                        type="ITL.Analytics/inferenceEndpoints",
                        status=e.status,
                        properties={
                            "model_id": e.model_id,
                            "replica_count": e.replica_count,
                        },
                        created_at=e.created_at,
                        url=e.url,
                    )
                    for e in endpoints
                ]
            }

    except Exception as e:
        logger.error(f"Failed to list endpoints: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/inferenceEndpoints/{endpoint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_inference_endpoint(
    subscription_id: str, resource_group: str, endpoint_id: UUID
):
    """Delete inference endpoint"""
    logger.info(
        f"DELETE /inferenceEndpoints/{endpoint_id}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = InferenceEndpointRepository(session)
            service = InferenceEndpointService(repo)
            result = await service.delete_endpoint(endpoint_id)

            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete endpoint: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

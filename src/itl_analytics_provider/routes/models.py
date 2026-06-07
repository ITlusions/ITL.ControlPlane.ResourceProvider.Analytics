"""
FastAPI routes for Model Registry resources
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from itl_analytics_provider.models.notebook import ModelRequest, ModelResponse
from itl_analytics_provider.services.model_service import ModelService
from itl_analytics_provider.repositories.model_repo import ModelRepository
from itl_analytics_provider.core.database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Models"])


@router.post(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/models",
    response_model=ModelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_model(
    subscription_id: str,
    resource_group: str,
    request: ModelRequest,
):
    """Register new model in registry

    TODO (Phase 3):
        - Store in MLflow registry
        - Setup versioning
        - Create artifact storage
    """
    logger.info(
        f"POST /models: name={request.name}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = ModelRepository(session)
            service = ModelService(repo)

            model = await service.register_model(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                framework=request.properties.framework,
                version=request.properties.version,
            )

            return ModelResponse(
                id=model.id,
                name=model.name,
                type="ITL.Analytics/models",
                properties={
                    "framework": model.framework,
                    "version": model.version,
                },
                created_at=model.created_at,
                updated_at=model.updated_at,
            )

    except Exception as e:
        logger.error(f"Failed to register model: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/models"
)
async def list_models(subscription_id: str, resource_group: str):
    """List models in resource group"""
    logger.info(
        f"GET /models",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = ModelRepository(session)
            service = ModelService(repo)
            models = await service.list_models(subscription_id, resource_group)

            return {
                "value": [
                    ModelResponse(
                        id=m.id,
                        name=m.name,
                        type="ITL.Analytics/models",
                        properties={
                            "framework": m.framework,
                            "version": m.version,
                        },
                        created_at=m.created_at,
                        updated_at=m.updated_at,
                    )
                    for m in models
                ]
            }

    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/models/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_model(subscription_id: str, resource_group: str, model_id: UUID):
    """Delete model"""
    logger.info(
        f"DELETE /models/{model_id}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = ModelRepository(session)
            service = ModelService(repo)
            result = await service.delete_model(model_id)

            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete model: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

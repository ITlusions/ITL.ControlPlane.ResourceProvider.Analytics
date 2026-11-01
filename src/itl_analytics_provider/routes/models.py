"""
Routes for Model Registry resources

Provides model registry management endpoints following Core provider pattern.
"""

from fastapi import APIRouter, HTTPException, status
from structlog import get_logger

from ..models import ModelRequest, ModelResponse

logger = get_logger()


def setup_models_routes(app, engine, provider) -> APIRouter:
    """
    Setup model registry routes

    Endpoints:
    - POST   /models                  - Register model
    - GET    /models                  - List models
    - GET    /models/{name}           - Get model
    - DELETE /models/{name}           - Delete model

    Uses provider handler methods (Core provider pattern):
    - provider._create_model()
    - provider._get_model()
    - provider._list_models()
    - provider._delete_model()
    """
    router = APIRouter(tags=["models"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/models",
        response_model=ModelResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def register_model(
        subscription_id: str, resource_group: str, request: ModelRequest
    ):
        """Register model in registry"""
        logger.info(
            "register_model",
            subscription_id=subscription_id,
            resource_group=resource_group,
            name=request.name,
        )

        try:
            owner_id = "default-user"

            model = await provider._create_model(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                properties=request.properties.dict(),
                owner_id=owner_id,
            )

            return ModelResponse(
                id=model.id,
                name=model.name,
                location=model.location,
                status=model.status,
                created_at=model.created_at,
                updated_at=model.updated_at,
                owner_id=model.owner_id,
                properties={
                    "modelType": model.model_type,
                    "framework": model.framework,
                    "version": model.version,
                },
            )

        except Exception as e:
            logger.error("register_model_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/models",
        status_code=status.HTTP_200_OK,
    )
    async def list_models(subscription_id: str, resource_group: str):
        """List models in resource group"""
        logger.info(
            "list_models",
            subscription_id=subscription_id,
            resource_group=resource_group,
        )

        try:
            models = await provider._list_models(subscription_id, resource_group)

            return {
                "value": [
                    ModelResponse(
                        id=m.id,
                        name=m.name,
                        location=m.location,
                        status=m.status,
                        created_at=m.created_at,
                        updated_at=m.updated_at,
                        owner_id=m.owner_id,
                        properties={
                            "modelType": m.model_type,
                            "framework": m.framework,
                            "version": m.version,
                        },
                    )
                    for m in models
                ]
            }

        except Exception as e:
            logger.error("list_models_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/models/{model_name}",
        response_model=ModelResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_model(subscription_id: str, resource_group: str, model_name: str):
        """Get model details"""
        logger.info(
            "get_model",
            subscription_id=subscription_id,
            resource_group=resource_group,
            model_name=model_name,
        )

        try:
            model = await provider._get_model(subscription_id, resource_group, model_name)

            if not model:
                raise HTTPException(status_code=404, detail="Model not found")

            return ModelResponse(
                id=model.id,
                name=model.name,
                location=model.location,
                status=model.status,
                created_at=model.created_at,
                updated_at=model.updated_at,
                owner_id=model.owner_id,
                properties={
                    "modelType": model.model_type,
                    "framework": model.framework,
                    "version": model.version,
                },
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("get_model_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/models/{model_name}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_model(subscription_id: str, resource_group: str, model_name: str):
        """Delete model"""
        logger.info(
            "delete_model",
            subscription_id=subscription_id,
            resource_group=resource_group,
            model_name=model_name,
        )

        try:
            result = await provider._delete_model(
                subscription_id, resource_group, model_name
            )

            if not result:
                raise HTTPException(status_code=404, detail="Model not found")

            return None

        except HTTPException:
            raise
        except Exception as e:
            logger.error("delete_model_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    return router

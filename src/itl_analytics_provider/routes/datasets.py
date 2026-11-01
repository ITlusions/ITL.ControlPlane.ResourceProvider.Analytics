"""
Routes for Dataset resources

Provides dataset management endpoints following Core provider pattern.
"""

from fastapi import APIRouter, HTTPException, status
from structlog import get_logger

from ..models import DatasetRequest, DatasetResponse

logger = get_logger()


def setup_datasets_routes(app, engine, provider) -> APIRouter:
    """
    Setup dataset routes

    Endpoints:
    - POST   /datasets                - Create dataset
    - GET    /datasets                - List datasets
    - GET    /datasets/{name}         - Get dataset
    - DELETE /datasets/{name}         - Delete dataset

    Uses provider handler methods (Core provider pattern):
    - provider._create_dataset()
    - provider._get_dataset()
    - provider._list_datasets()
    - provider._delete_dataset()
    """
    router = APIRouter(tags=["datasets"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/datasets",
        response_model=DatasetResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def register_dataset(
        subscription_id: str, resource_group: str, request: DatasetRequest
    ):
        """Register dataset"""
        logger.info(
            "register_dataset",
            subscription_id=subscription_id,
            resource_group=resource_group,
            name=request.name,
        )

        try:
            owner_id = "default-user"

            dataset = await provider._create_dataset(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                properties=request.properties.dict(),
                owner_id=owner_id,
            )

            return DatasetResponse(
                id=dataset.id,
                name=dataset.name,
                location=dataset.location,
                status=dataset.status,
                created_at=dataset.created_at,
                updated_at=dataset.updated_at,
                owner_id=dataset.owner_id,
                properties={
                    "datasetType": dataset.dataset_type,
                    "storageAccount": dataset.storage_account,
                    "storagePath": dataset.storage_path,
                },
            )

        except Exception as e:
            logger.error("register_dataset_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/datasets",
        status_code=status.HTTP_200_OK,
    )
    async def list_datasets(subscription_id: str, resource_group: str):
        """List datasets in resource group"""
        logger.info(
            "list_datasets",
            subscription_id=subscription_id,
            resource_group=resource_group,
        )

        try:
            datasets = await provider._list_datasets(subscription_id, resource_group)

            return {
                "value": [
                    DatasetResponse(
                        id=d.id,
                        name=d.name,
                        location=d.location,
                        status=d.status,
                        created_at=d.created_at,
                        updated_at=d.updated_at,
                        owner_id=d.owner_id,
                        properties={
                            "datasetType": d.dataset_type,
                            "storageAccount": d.storage_account,
                            "storagePath": d.storage_path,
                        },
                    )
                    for d in datasets
                ]
            }

        except Exception as e:
            logger.error("list_datasets_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/datasets/{dataset_name}",
        response_model=DatasetResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_dataset(
        subscription_id: str, resource_group: str, dataset_name: str
    ):
        """Get dataset details"""
        logger.info(
            "get_dataset",
            subscription_id=subscription_id,
            resource_group=resource_group,
            dataset_name=dataset_name,
        )

        try:
            dataset = await provider._get_dataset(
                subscription_id, resource_group, dataset_name
            )

            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            return DatasetResponse(
                id=dataset.id,
                name=dataset.name,
                location=dataset.location,
                status=dataset.status,
                created_at=dataset.created_at,
                updated_at=dataset.updated_at,
                owner_id=dataset.owner_id,
                properties={
                    "datasetType": dataset.dataset_type,
                    "storageAccount": dataset.storage_account,
                    "storagePath": dataset.storage_path,
                },
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("get_dataset_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/datasets/{dataset_name}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_dataset(
        subscription_id: str, resource_group: str, dataset_name: str
    ):
        """Delete dataset"""
        logger.info(
            "delete_dataset",
            subscription_id=subscription_id,
            resource_group=resource_group,
            dataset_name=dataset_name,
        )

        try:
            result = await provider._delete_dataset(
                subscription_id, resource_group, dataset_name
            )

            if not result:
                raise HTTPException(status_code=404, detail="Dataset not found")

            return None

        except HTTPException:
            raise
        except Exception as e:
            logger.error("delete_dataset_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    return router

"""
FastAPI routes for Dataset resources
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from itl_analytics_provider.models.notebook import DatasetRequest, DatasetResponse
from itl_analytics_provider.services.dataset_service import DatasetService
from itl_analytics_provider.repositories.dataset_repo import DatasetRepository
from itl_analytics_provider.core.database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Datasets"])


@router.post(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/datasets",
    response_model=DatasetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_dataset(
    subscription_id: str,
    resource_group: str,
    request: DatasetRequest,
):
    """Register new dataset

    TODO (Phase 2):
        - Analyze schema
        - Calculate statistics
        - Setup lineage tracking
    """
    logger.info(
        f"POST /datasets: name={request.name}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = DatasetRepository(session)
            service = DatasetService(repo)

            dataset = await service.register_dataset(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                data_location=request.properties.location,
            )

            return DatasetResponse(
                id=dataset.id,
                name=dataset.name,
                type="ITL.Analytics/datasets",
                location=dataset.location,
                properties={
                    "location": dataset.data_location,
                    "schema": dataset.schema or {},
                },
                created_at=dataset.created_at,
            )

    except Exception as e:
        logger.error(f"Failed to register dataset: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/datasets"
)
async def list_datasets(subscription_id: str, resource_group: str):
    """List datasets in resource group"""
    logger.info(
        f"GET /datasets",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = DatasetRepository(session)
            service = DatasetService(repo)
            datasets = await service.list_datasets(subscription_id, resource_group)

            return {
                "value": [
                    DatasetResponse(
                        id=d.id,
                        name=d.name,
                        type="ITL.Analytics/datasets",
                        location=d.location,
                        properties={
                            "location": d.data_location,
                            "schema": d.schema or {},
                        },
                        created_at=d.created_at,
                    )
                    for d in datasets
                ]
            }

    except Exception as e:
        logger.error(f"Failed to list datasets: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/datasets/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_dataset(subscription_id: str, resource_group: str, dataset_id: UUID):
    """Delete dataset"""
    logger.info(
        f"DELETE /datasets/{dataset_id}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = DatasetRepository(session)
            service = DatasetService(repo)
            result = await service.delete_dataset(dataset_id)

            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dataset: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

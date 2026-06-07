"""
FastAPI routes for Spark Cluster resources
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from itl_analytics_provider.models.notebook import SparkClusterRequest, SparkClusterResponse
from itl_analytics_provider.services.spark_service import SparkClusterService
from itl_analytics_provider.repositories.spark_repo import SparkClusterRepository
from itl_analytics_provider.core.database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Spark Clusters"])


@router.post(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters",
    response_model=SparkClusterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_spark_cluster(
    subscription_id: str,
    resource_group: str,
    request: SparkClusterRequest,
):
    """Create new Spark cluster

    TODO:
        - Integrate with Container Provider
        - Wait for pods to be ready
        - Setup master/worker networking
        - Return cluster with status Running
    """
    logger.info(
        f"POST /sparkClusters: name={request.name}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = SparkClusterRepository(session)
            service = SparkClusterService(repo)

            cluster = await service.create_cluster(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                properties=request.properties.dict(),
                owner_id="default-user",  # TODO: Get from auth context
            )

            return SparkClusterResponse(
                id=cluster.id,
                name=cluster.name,
                type="ITL.Analytics/sparkClusters",
                location=cluster.location,
                status=cluster.status,
                properties={
                    "driver_cpu": cluster.driver_cpu,
                    "driver_memory_gb": cluster.driver_memory_gb,
                    "worker_count": cluster.worker_count,
                    "worker_cpu": cluster.worker_cpu,
                    "worker_memory_gb": cluster.worker_memory_gb,
                    "worker_gpus": cluster.worker_gpus,
                },
                created_at=cluster.created_at,
                updated_at=cluster.updated_at,
            )

    except Exception as e:
        logger.error(f"Failed to create cluster: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters"
)
async def list_spark_clusters(subscription_id: str, resource_group: str):
    """List Spark clusters in resource group"""
    logger.info(
        f"GET /sparkClusters",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = SparkClusterRepository(session)
            service = SparkClusterService(repo)
            clusters = await service.list_clusters(subscription_id, resource_group)

            return {
                "value": [
                    SparkClusterResponse(
                        id=c.id,
                        name=c.name,
                        type="ITL.Analytics/sparkClusters",
                        location=c.location,
                        status=c.status,
                        properties={
                            "driver_cpu": c.driver_cpu,
                            "driver_memory_gb": c.driver_memory_gb,
                            "worker_count": c.worker_count,
                        },
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                    )
                    for c in clusters
                ]
            }

    except Exception as e:
        logger.error(f"Failed to list clusters: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters/{cluster_id}"
)
async def get_spark_cluster(
    subscription_id: str, resource_group: str, cluster_id: UUID
):
    """Get specific Spark cluster"""
    logger.info(
        f"GET /sparkClusters/{cluster_id}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = SparkClusterRepository(session)
            cluster = await repo.get_by_id(cluster_id)

            if not cluster:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            return SparkClusterResponse(
                id=cluster.id,
                name=cluster.name,
                type="ITL.Analytics/sparkClusters",
                location=cluster.location,
                status=cluster.status,
                properties={
                    "driver_cpu": cluster.driver_cpu,
                    "driver_memory_gb": cluster.driver_memory_gb,
                    "worker_count": cluster.worker_count,
                },
                created_at=cluster.created_at,
                updated_at=cluster.updated_at,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cluster: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters/{cluster_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_spark_cluster(
    subscription_id: str, resource_group: str, cluster_id: UUID
):
    """Delete Spark cluster"""
    logger.info(
        f"DELETE /sparkClusters/{cluster_id}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = SparkClusterRepository(session)
            service = SparkClusterService(repo)
            result = await service.delete_cluster(cluster_id)

            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete cluster: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

"""
Routes for Spark Cluster resources

Provides Spark cluster management endpoints following Core provider pattern.
"""

from fastapi import APIRouter, HTTPException, status
from structlog import get_logger

from ..models import SparkClusterRequest, SparkClusterResponse

logger = get_logger()


def setup_spark_clusters_routes(app, engine, provider) -> APIRouter:
    """
    Setup Spark cluster routes

    Endpoints:
    - POST   /sparkClusters           - Create cluster
    - GET    /sparkClusters           - List clusters
    - GET    /sparkClusters/{name}    - Get cluster
    - DELETE /sparkClusters/{name}    - Delete cluster

    Uses provider handler methods (Core provider pattern):
    - provider._create_spark_cluster()
    - provider._get_spark_cluster()
    - provider._list_spark_clusters()
    - provider._delete_spark_cluster()
    """
    router = APIRouter(tags=["sparkClusters"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters",
        response_model=SparkClusterResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_spark_cluster(
        subscription_id: str, resource_group: str, request: SparkClusterRequest
    ):
        """Create Spark cluster"""
        logger.info(
            "create_spark_cluster",
            subscription_id=subscription_id,
            resource_group=resource_group,
            name=request.name,
        )

        try:
            owner_id = "default-user"

            cluster = await provider._create_spark_cluster(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                properties=request.properties.dict(),
                owner_id=owner_id,
            )

            return SparkClusterResponse(
                id=cluster.id,
                name=cluster.name,
                location=cluster.location,
                status=cluster.status,
                created_at=cluster.created_at,
                updated_at=cluster.updated_at,
                owner_id=cluster.owner_id,
                properties={
                    "clusterSize": cluster.cluster_size,
                    "sparkVersion": cluster.spark_version,
                    "computeSku": cluster.compute_sku,
                },
            )

        except Exception as e:
            logger.error("create_spark_cluster_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters",
        status_code=status.HTTP_200_OK,
    )
    async def list_spark_clusters(subscription_id: str, resource_group: str):
        """List Spark clusters in resource group"""
        logger.info(
            "list_spark_clusters",
            subscription_id=subscription_id,
            resource_group=resource_group,
        )

        try:
            clusters = await provider._list_spark_clusters(subscription_id, resource_group)

            return {
                "value": [
                    SparkClusterResponse(
                        id=c.id,
                        name=c.name,
                        location=c.location,
                        status=c.status,
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                        owner_id=c.owner_id,
                        properties={
                            "clusterSize": c.cluster_size,
                            "sparkVersion": c.spark_version,
                            "computeSku": c.compute_sku,
                        },
                    )
                    for c in clusters
                ]
            }

        except Exception as e:
            logger.error("list_spark_clusters_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))


    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters/{cluster_name}",
        response_model=SparkClusterResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_spark_cluster(
        subscription_id: str, resource_group: str, cluster_name: str
    ):
        """Get Spark cluster details"""
        logger.info(
            "get_spark_cluster",
            subscription_id=subscription_id,
            resource_group=resource_group,
            cluster_name=cluster_name,
        )

        try:
            cluster = await provider._get_spark_cluster(
                subscription_id, resource_group, cluster_name
            )

            if not cluster:
                raise HTTPException(status_code=404, detail="Cluster not found")

            return SparkClusterResponse(
                id=cluster.id,
                name=cluster.name,
                location=cluster.location,
                status=cluster.status,
                created_at=cluster.created_at,
                updated_at=cluster.updated_at,
                owner_id=cluster.owner_id,
                properties={
                    "clusterSize": cluster.cluster_size,
                    "sparkVersion": cluster.spark_version,
                    "computeSku": cluster.compute_sku,
                },
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("get_spark_cluster_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters/{cluster_name}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_spark_cluster(
        subscription_id: str, resource_group: str, cluster_name: str
    ):
        """Delete Spark cluster"""
        logger.info(
            "delete_spark_cluster",
            subscription_id=subscription_id,
            resource_group=resource_group,
            cluster_name=cluster_name,
        )

        try:
            result = await provider._delete_spark_cluster(
                subscription_id, resource_group, cluster_name
            )

            if not result:
                raise HTTPException(status_code=404, detail="Cluster not found")

            return None

        except HTTPException:
            raise
        except Exception as e:
            logger.error("delete_spark_cluster_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    return router

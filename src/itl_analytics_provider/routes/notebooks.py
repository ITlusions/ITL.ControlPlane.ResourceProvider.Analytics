"""
Routes for Analytics resources

Provides setup functions for:
- Notebooks
- Spark Clusters
- Analytics Jobs
- Models
- Datasets
- Inference Endpoints
"""

from fastapi import APIRouter, status, HTTPException
from structlog import get_logger
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    NotebookRequest,
    NotebookResponse,
    SparkClusterRequest,
    SparkClusterResponse,
    AnalyticsJobRequest,
    AnalyticsJobResponse,
    ModelRequest,
    ModelResponse,
    DatasetRequest,
    DatasetResponse,
    InferenceEndpointRequest,
    InferenceEndpointResponse,
)
from ..repositories.notebook_repo import NotebookRepository
from ..services.notebook_service import NotebookService

logger = get_logger()


def setup_notebooks_routes(app, engine, provider) -> APIRouter:
    """
    Setup notebook routes

    Endpoints:
    - POST   /notebooks              - Create notebook
    - GET    /notebooks              - List notebooks
    - GET    /notebooks/{id}         - Get notebook
    - DELETE /notebooks/{id}         - Delete notebook
    """
    router = APIRouter(tags=["notebooks"])

    async def get_session() -> AsyncSession:
        """Get database session"""
        async_session = engine.async_session_maker
        async with async_session() as session:
            yield session

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/notebooks",
        response_model=NotebookResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_notebook(
        subscription_id: str, resource_group: str, request: NotebookRequest
    ):
        """Create notebook session"""
        logger.info(
            "create_notebook",
            subscription_id=subscription_id,
            resource_group=resource_group,
            name=request.name,
        )

        try:
            async_session = engine.async_session_maker
            async with async_session() as session:
                repo = NotebookRepository(session)
                service = NotebookService(repo)

                # Owner ID from JWT (TODO: extract from context)
                owner_id = "default-user"

                notebook = await service.create_notebook(
                    subscription_id=subscription_id,
                    resource_group=resource_group,
                    name=request.name,
                    location=request.location,
                    properties=request.properties.dict(),
                    owner_id=owner_id,
                )

                return NotebookResponse(
                    id=notebook.id,
                    name=notebook.name,
                    location=notebook.location,
                    status=notebook.status,
                    created_at=notebook.created_at,
                    updated_at=notebook.updated_at,
                    owner_id=notebook.owner_id,
                    properties={
                        "kernel": notebook.kernel,
                        "computeSku": notebook.compute_sku,
                        "memory_gb": notebook.memory_gb,
                        "cpu_cores": notebook.cpu_cores,
                        "storage_gb": notebook.storage_gb,
                        "pod_name": notebook.pod_name,
                        "storage_bucket": notebook.storage_bucket,
                        "notebook_url": notebook.notebook_url,
                    },
                )

        except Exception as e:
            logger.error("create_notebook_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/notebooks",
        status_code=status.HTTP_200_OK,
    )
    async def list_notebooks(subscription_id: str, resource_group: str):
        """List notebooks in resource group"""
        logger.info(
            "list_notebooks",
            subscription_id=subscription_id,
            resource_group=resource_group,
        )

        try:
            async_session = engine.async_session_maker
            async with async_session() as session:
                repo = NotebookRepository(session)
                notebooks = await repo.list_by_subscription(subscription_id, resource_group)

                return {
                    "value": [
                        NotebookResponse(
                            id=nb.id,
                            name=nb.name,
                            location=nb.location,
                            status=nb.status,
                            created_at=nb.created_at,
                            updated_at=nb.updated_at,
                            owner_id=nb.owner_id,
                            properties={
                                "kernel": nb.kernel,
                                "computeSku": nb.compute_sku,
                                "memory_gb": nb.memory_gb,
                                "cpu_cores": nb.cpu_cores,
                                "storage_gb": nb.storage_gb,
                                "pod_name": nb.pod_name,
                                "storage_bucket": nb.storage_bucket,
                                "notebook_url": nb.notebook_url,
                            },
                        )
                        for nb in notebooks
                    ]
                }

        except Exception as e:
            logger.error("list_notebooks_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/notebooks/{notebook_id}",
        response_model=NotebookResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_notebook(
        subscription_id: str, resource_group: str, notebook_id: UUID
    ):
        """Get notebook details"""
        logger.info(
            "get_notebook", subscription_id=subscription_id, notebook_id=notebook_id
        )

        try:
            async_session = engine.async_session_maker
            async with async_session() as session:
                repo = NotebookRepository(session)
                notebook = await repo.get_by_id(notebook_id)

                if not notebook:
                    raise HTTPException(status_code=404, detail="Notebook not found")

                return NotebookResponse(
                    id=notebook.id,
                    name=notebook.name,
                    location=notebook.location,
                    status=notebook.status,
                    created_at=notebook.created_at,
                    updated_at=notebook.updated_at,
                    owner_id=notebook.owner_id,
                    properties={
                        "kernel": notebook.kernel,
                        "computeSku": notebook.compute_sku,
                        "memory_gb": notebook.memory_gb,
                        "cpu_cores": notebook.cpu_cores,
                        "storage_gb": notebook.storage_gb,
                        "pod_name": notebook.pod_name,
                        "storage_bucket": notebook.storage_bucket,
                        "notebook_url": notebook.notebook_url,
                    },
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("get_notebook_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/notebooks/{notebook_id}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_notebook(
        subscription_id: str, resource_group: str, notebook_id: UUID
    ):
        """Delete notebook"""
        logger.info(
            "delete_notebook", subscription_id=subscription_id, notebook_id=notebook_id
        )

        try:
            async_session = engine.async_session_maker
            async with async_session() as session:
                repo = NotebookRepository(session)
                service = NotebookService(repo)

                result = await service.delete_notebook(notebook_id)

                if not result:
                    raise HTTPException(status_code=404, detail="Notebook not found")

                return None

        except HTTPException:
            raise
        except Exception as e:
            logger.error("delete_notebook_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    return router


def setup_spark_clusters_routes(app, engine, provider) -> APIRouter:
    """Setup Spark cluster routes"""
    router = APIRouter(tags=["sparkClusters"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters",
        response_model=SparkClusterResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def create_spark_cluster(
        subscription_id: str, resource_group: str, request: SparkClusterRequest
    ):
        """Create Spark cluster"""
        logger.info("create_spark_cluster", subscription_id=subscription_id, name=request.name)
        # TODO: Implement Spark cluster creation
        return SparkClusterResponse(
            id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/sparkClusters/{request.name}",
            name=request.name,
            location=request.location,
            status="Creating",
        )

    return router


def setup_analytics_jobs_routes(app, engine, provider) -> APIRouter:
    """Setup analytics job routes"""
    router = APIRouter(tags=["analyticsJobs"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/analyticsJobs",
        response_model=AnalyticsJobResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def create_analytics_job(
        subscription_id: str, resource_group: str, request: AnalyticsJobRequest
    ):
        """Create analytics job"""
        logger.info("create_analytics_job", subscription_id=subscription_id, name=request.name)
        # TODO: Implement job creation
        return AnalyticsJobResponse(
            id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/analyticsJobs/{request.name}",
            name=request.name,
            status="Submitted",
        )

    return router


def setup_models_routes(app, engine, provider) -> APIRouter:
    """Setup model registry routes"""
    router = APIRouter(tags=["models"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/models",
        response_model=ModelResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def register_model(
        subscription_id: str, resource_group: str, request: ModelRequest
    ):
        """Register model"""
        logger.info("register_model", subscription_id=subscription_id, name=request.name)
        # TODO: Implement model registration
        return ModelResponse(
            id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/models/{request.name}",
            name=request.name,
        )

    return router


def setup_datasets_routes(app, engine, provider) -> APIRouter:
    """Setup dataset catalog routes"""
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
        logger.info("register_dataset", subscription_id=subscription_id, name=request.name)
        # TODO: Implement dataset registration
        return DatasetResponse(
            id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/datasets/{request.name}",
            name=request.name,
        )

    return router


def setup_inference_endpoints_routes(app, engine, provider) -> APIRouter:
    """Setup inference endpoint routes"""
    router = APIRouter(tags=["inferenceEndpoints"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/inferenceEndpoints",
        response_model=InferenceEndpointResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def create_inference_endpoint(
        subscription_id: str, resource_group: str, request: InferenceEndpointRequest
    ):
        """Create inference endpoint"""
        logger.info("create_inference_endpoint", subscription_id=subscription_id, name=request.name)
        # TODO: Implement endpoint creation
        return InferenceEndpointResponse(
            id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/inferenceEndpoints/{request.name}",
            name=request.name,
            status="Creating",
        )

    return router

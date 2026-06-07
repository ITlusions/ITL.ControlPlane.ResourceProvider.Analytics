"""
Notebook service - Business logic layer
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import asyncio
from ..models.orm import Notebook, NotebookStatus
from ..clients.container_client import ContainerClient
from ..clients.minio_client import MinIOClient

logger = logging.getLogger(__name__)


class NotebookService:
    """Notebook management service"""

    def __init__(self, repository):
        self.repository = repository

    async def create_notebook(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        properties: Dict[str, Any],
        owner_id: str,
    ) -> Notebook:
        """
        Create notebook session

        Steps:
        1. Create database record (status: Creating)
        2. Call Container provider to create JupyterLab pod
        3. Setup MinIO storage
        4. Update status to Running
        5. Return notebook record

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            name: Notebook name
            location: Azure region
            properties: Notebook properties
            owner_id: User ID

        Returns:
            Created Notebook record
        """
        
        logger.info(
            f"Creating notebook {name}",
            extra={
                "subscription": subscription_id,
                "resource_group": resource_group,
                "owner": owner_id,
            },
        )

        # Extract properties
        kernel = properties.get("kernel", "python3.11")
        compute_sku = properties.get("computeSku", "Standard_D4s_v3")
        memory_gb = properties.get("memory_gb", 16)
        cpu_cores = properties.get("cpu_cores", 4)
        storage_gb = properties.get("storage_gb", 100)

        # Create database record
        notebook_data = {
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "name": name,
            "location": location,
            "kernel": kernel,
            "compute_sku": compute_sku,
            "memory_gb": memory_gb,
            "cpu_cores": cpu_cores,
            "storage_gb": storage_gb,
            "status": NotebookStatus.CREATING.value,
            "owner_id": owner_id,
            "pod_namespace": "analytics",
        }

        notebook = await self.repository.create(notebook_data)

        # Call Container provider to create JupyterLab pod
        pod_name = f"notebook-{notebook.id}"
        container_client = ContainerClient(base_url="http://localhost:9508")
        
        try:
            logger.info(f"Creating JupyterLab pod via Container Provider: {pod_name}")
            
            pod_response = await container_client.create_pod(
                subscription_id=subscription_id,
                resource_group=resource_group,
                pod_name=pod_name,
                namespace="analytics",
                image="jupyter/base-notebook:latest",
                cpu_cores=cpu_cores,
                memory_gb=memory_gb,
                storage_gb=storage_gb,
                port=8888,
                labels={
                    "app": "jupyter-notebook",
                    "notebook-id": str(notebook.id),
                    "owner": owner_id,
                },
            )
            
            logger.info(f"Pod created successfully: {pod_name}")
            
        except Exception as e:
            logger.error(f"Failed to create pod: {str(e)}")
            await self.repository.update_status(notebook.id, NotebookStatus.ERROR)
            raise

        # Setup MinIO storage
        storage_bucket = f"analytics-{notebook.id}".replace("_", "-").lower()
        minio_client = MinIOClient(
            endpoint="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
        )
        
        try:
            logger.info(f"Creating MinIO bucket: {storage_bucket}")
            
            if not await minio_client.bucket_exists(storage_bucket):
                await minio_client.create_bucket(storage_bucket)
            
            # Setup CORS for web access
            await minio_client.setup_cors(storage_bucket)
            
            # Setup policy for notebook access
            await minio_client.setup_bucket_policy(storage_bucket)
            
            logger.info(f"MinIO bucket ready: {storage_bucket}")
            
        except Exception as e:
            logger.error(f"Failed to setup storage: {str(e)}")
            await self.repository.update_status(notebook.id, NotebookStatus.ERROR)
            raise

        # Wait for pod to be running
        try:
            logger.info(f"Waiting for pod to be running...")
            is_running = await container_client.wait_for_pod_running(
                subscription_id=subscription_id,
                resource_group=resource_group,
                pod_name=pod_name,
                timeout_seconds=300,
                check_interval=5,
            )
            
            if not is_running:
                logger.error(f"Pod failed to start: {pod_name}")
                await self.repository.update_status(notebook.id, NotebookStatus.ERROR)
                raise Exception(f"Pod startup timeout: {pod_name}")
            
        except Exception as e:
            logger.error(f"Failed waiting for pod: {str(e)}")
            await self.repository.update_status(notebook.id, NotebookStatus.ERROR)
            raise

        # Get pod URL
        notebook_url = await container_client.get_pod_url(
            subscription_id=subscription_id,
            resource_group=resource_group,
            pod_name=pod_name,
            service_host="notebooks.analytics.itl.com",
        )

        # Update notebook with infrastructure references
        await self.repository.update(
            notebook.id,
            {
                "pod_name": pod_name,
                "storage_bucket": storage_bucket,
                "storage_path": f"s3://{storage_bucket}/",
                "notebook_url": notebook_url,
                "status": NotebookStatus.RUNNING.value,
            },
        )

        await container_client.close()
        await minio_client.close()

        notebook = await self.repository.get_by_id(notebook.id)
        logger.info(f"Notebook created and running: {notebook.name}")
        return notebook

    async def delete_notebook(self, notebook_id: UUID) -> bool:
        """
        Delete notebook session

        Steps:
        1. Update status to Terminating
        2. Call Container provider to delete pod
        3. Call Storage provider to cleanup bucket
        4. Delete database record

        Args:
            notebook_id: Notebook ID

        Returns:
            True if deleted
        """
        logger.info(f"Deleting notebook {notebook_id}")

        notebook = await self.repository.get_by_id(notebook_id)
        if not notebook:
            logger.warning(f"Notebook not found: {notebook_id}")
            return False

        # Update status
        await self.repository.update_status(notebook_id, NotebookStatus.TERMINATING)

        # Call Container provider to delete pod
        container_client = ContainerClient(base_url="http://localhost:9508")
        
        try:
            logger.info(f"Deleting pod via Container Provider: {notebook.pod_name}")
            
            if notebook.pod_name:
                await container_client.delete_pod(
                    subscription_id=notebook.subscription_id,
                    resource_group=notebook.resource_group,
                    pod_name=notebook.pod_name,
                    namespace="analytics",
                )
                logger.info(f"Pod deleted: {notebook.pod_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete pod: {str(e)}")
            # Continue with cleanup even if pod deletion fails

        # Call Storage provider to cleanup bucket
        minio_client = MinIOClient(
            endpoint="http://localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
        )
        
        try:
            logger.info(f"Deleting MinIO bucket: {notebook.storage_bucket}")
            
            if notebook.storage_bucket and await minio_client.bucket_exists(notebook.storage_bucket):
                await minio_client.delete_bucket(notebook.storage_bucket)
                logger.info(f"Bucket deleted: {notebook.storage_bucket}")
            
        except Exception as e:
            logger.error(f"Failed to delete bucket: {str(e)}")
            # Continue with record deletion even if bucket deletion fails

        await container_client.close()
        await minio_client.close()

        # Delete database record
        result = await self.repository.delete(notebook_id)
        logger.info(f"Notebook deleted: {notebook_id}")
        return result

    async def get_notebook(
        self, subscription_id: str, resource_group: str, name: str
    ) -> Optional[Notebook]:
        """Get notebook details"""
        return await self.repository.get_by_name(subscription_id, resource_group, name)

    async def list_notebooks(
        self, subscription_id: str, resource_group: str
    ):
        """List notebooks in resource group"""
        return await self.repository.list_by_subscription(subscription_id, resource_group)

    async def update_notebook_status(
        self, notebook_id: UUID, status: NotebookStatus
    ) -> Optional[Notebook]:
        """Update notebook status"""
        return await self.repository.update_status(notebook_id, status)


class SparkService:
    """Spark cluster orchestration"""

    def __init__(self, engine):
        self.engine = engine

    async def create_cluster(self, cluster_id: str, properties: dict):
        """Create Spark cluster"""
        # TODO: Implement Spark cluster creation
        logger.info(f"Creating Spark cluster: {cluster_id}")

    async def get_cluster_status(self, cluster_id: str):
        """Get cluster status"""
        # TODO: Implement status retrieval
        logger.info(f"Getting cluster status: {cluster_id}")


class JobOrchestratorService:
    """Analytics job scheduling and orchestration"""

    def __init__(self, engine):
        self.engine = engine

    async def submit_job(self, job_id: str, properties: dict):
        """Submit analytics job"""
        # TODO: Implement job submission
        logger.info(f"Submitting job: {job_id}")


class ModelRegistryService:
    """ML model registry operations"""

    def __init__(self, engine):
        self.engine = engine

    async def register_model(self, model_id: str, properties: dict):
        """Register model"""
        # TODO: Implement model registration
        logger.info(f"Registering model: {model_id}")


class DatasetCatalogService:
    """Dataset catalog management"""

    def __init__(self, engine):
        self.engine = engine

    async def register_dataset(self, dataset_id: str, properties: dict):
        """Register dataset"""
        # TODO: Implement dataset registration
        logger.info(f"Registering dataset: {dataset_id}")

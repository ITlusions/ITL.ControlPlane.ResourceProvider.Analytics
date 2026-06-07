"""
Container Provider HTTP client

Handles communication with ITL.ControlPlane.ResourceProvider.Container
for pod/container orchestration
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
import httpx

logger = logging.getLogger(__name__)


class ContainerClient:
    """Client for Container Provider API"""

    def __init__(self, base_url: str = "http://localhost:9508"):
        """
        Initialize Container client

        Args:
            base_url: Container Provider base URL (default: localhost:9508)
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def create_pod(
        self,
        subscription_id: str,
        resource_group: str,
        pod_name: str,
        namespace: str = "analytics",
        image: str = "jupyter/base-notebook:latest",
        cpu_cores: int = 4,
        memory_gb: int = 16,
        storage_gb: int = 100,
        port: int = 8888,
        labels: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a pod via Container Provider

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            pod_name: Name for the pod
            namespace: Kubernetes namespace (default: analytics)
            image: Container image URI
            cpu_cores: CPU cores to allocate
            memory_gb: Memory in GB
            storage_gb: Storage in GB
            port: Container port to expose
            labels: Kubernetes labels

        Returns:
            Pod creation response with pod details

        Raises:
            httpx.HTTPError: If API call fails
        """

        logger.info(
            f"Creating pod via Container Provider",
            extra={
                "pod_name": pod_name,
                "namespace": namespace,
                "image": image,
                "cpu": cpu_cores,
                "memory": memory_gb,
            },
        )

        # Build ARM-style path to Container Provider
        resource_path = (
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/ITL.Container/pods"
        )

        # Prepare pod specification
        pod_spec = {
            "name": pod_name,
            "namespace": namespace,
            "image": image,
            "resources": {
                "cpu": str(cpu_cores),
                "memory": f"{memory_gb}Gi",
                "storage": f"{storage_gb}Gi",
            },
            "ports": [{"containerPort": port, "name": "jupyter"}],
            "labels": labels or {"app": pod_name, "tier": "notebook"},
            "environment": {
                "JUPYTER_ENABLE_LAB": "yes",
            },
        }

        try:
            response = await self.client.post(
                resource_path,
                json=pod_spec,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            logger.info(
                f"Pod created successfully",
                extra={"pod_name": pod_name, "status": response.status_code},
            )
            return response.json()

        except httpx.HTTPError as e:
            logger.error(
                f"Failed to create pod",
                extra={"pod_name": pod_name, "error": str(e)},
            )
            raise

    async def get_pod(
        self,
        subscription_id: str,
        resource_group: str,
        pod_name: str,
        namespace: str = "analytics",
    ) -> Dict[str, Any]:
        """
        Get pod details

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            pod_name: Pod name
            namespace: Kubernetes namespace

        Returns:
            Pod details including status, IP, etc
        """

        logger.info(f"Getting pod details: {pod_name}")

        resource_path = (
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/ITL.Container/pods/{pod_name}"
        )

        try:
            response = await self.client.get(resource_path)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to get pod: {str(e)}")
            raise

    async def delete_pod(
        self,
        subscription_id: str,
        resource_group: str,
        pod_name: str,
        namespace: str = "analytics",
    ) -> bool:
        """
        Delete a pod

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            pod_name: Pod name
            namespace: Kubernetes namespace

        Returns:
            True if deleted successfully
        """

        logger.info(f"Deleting pod: {pod_name}")

        resource_path = (
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/ITL.Container/pods/{pod_name}"
        )

        try:
            response = await self.client.delete(resource_path)
            response.raise_for_status()
            logger.info(f"Pod deleted: {pod_name}")
            return True

        except httpx.HTTPError as e:
            logger.error(f"Failed to delete pod: {str(e)}")
            raise

    async def get_pod_status(
        self,
        subscription_id: str,
        resource_group: str,
        pod_name: str,
    ) -> str:
        """
        Get pod status (Running, Pending, Failed, etc)

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            pod_name: Pod name

        Returns:
            Pod status string
        """

        try:
            pod = await self.get_pod(
                subscription_id, resource_group, pod_name
            )
            return pod.get("status", "Unknown")
        except Exception as e:
            logger.error(f"Failed to get pod status: {str(e)}")
            return "Unknown"

    async def wait_for_pod_running(
        self,
        subscription_id: str,
        resource_group: str,
        pod_name: str,
        timeout_seconds: int = 300,
        check_interval: int = 5,
    ) -> bool:
        """
        Wait for pod to reach Running status

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            pod_name: Pod name
            timeout_seconds: Max time to wait (default: 5 min)
            check_interval: Check every N seconds (default: 5)

        Returns:
            True if pod reached Running, False if timeout
        """

        import asyncio

        logger.info(
            f"Waiting for pod to be running: {pod_name}",
            extra={"timeout": timeout_seconds},
        )

        elapsed = 0
        while elapsed < timeout_seconds:
            try:
                status = await self.get_pod_status(
                    subscription_id, resource_group, pod_name
                )
                logger.info(f"Pod status: {status}")

                if status == "Running":
                    logger.info(f"Pod is running: {pod_name}")
                    return True

                elif status == "Failed":
                    logger.error(f"Pod failed: {pod_name}")
                    return False

            except Exception as e:
                logger.warning(f"Error checking pod status: {str(e)}")

            await asyncio.sleep(check_interval)
            elapsed += check_interval

        logger.error(f"Pod startup timeout: {pod_name}")
        return False

    async def get_pod_url(
        self,
        subscription_id: str,
        resource_group: str,
        pod_name: str,
        service_host: str = "notebooks.analytics.itl.com",
    ) -> Optional[str]:
        """
        Get public URL for pod

        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            pod_name: Pod name
            service_host: Public hostname

        Returns:
            Full URL to pod (e.g., https://notebooks.analytics.itl.com/xyz123)
        """

        try:
            pod = await self.get_pod(
                subscription_id, resource_group, pod_name
            )

            # Extract pod ID or use pod_name
            pod_id = pod.get("id", pod_name)
            url = f"https://{service_host}/{pod_id}"

            logger.info(f"Pod URL: {url}")
            return url

        except Exception as e:
            logger.error(f"Failed to get pod URL: {str(e)}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

"""
Service layer for Analytics Job resources
"""

import logging
from uuid import UUID
from typing import List, Optional

from itl_analytics_provider.repositories.job_repo import AnalyticsJobRepository

logger = logging.getLogger(__name__)


class AnalyticsJobService:
    """Business logic for analytics jobs"""

    def __init__(self, repo: AnalyticsJobRepository):
        self.repo = repo

    async def create_job(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        job_type: str,
        owner_id: str = "default-user",
    ):
        """Create new analytics job

        TODO (Phase 2):
            - Submit to job scheduler/queue
            - Setup job execution environment
            - Configure monitoring and logging
            - Create audit trail
        """
        logger.info(
            f"create_job: name={name}, type={job_type}",
            extra={"subscription": subscription_id, "resource_group": resource_group},
        )

        job_data = {
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "name": name,
            "location": location,
            "job_type": job_type,
            "status": "Submitted",
            "owner_id": owner_id,
        }

        job = await self.repo.create(job_data)
        logger.info(f"Job created: {job.id}")

        # TODO: Submit to execution engine
        # TODO: Monitor execution
        # TODO: Update status

        return job

    async def delete_job(self, job_id: UUID) -> bool:
        """Delete job record"""
        logger.info(f"delete_job: job_id={job_id}")
        return await self.repo.delete(job_id)

    async def list_jobs(self, subscription_id: str, resource_group: str) -> List:
        """List all jobs in resource group"""
        logger.info(
            f"list_jobs",
            extra={"subscription": subscription_id, "resource_group": resource_group},
        )
        return await self.repo.list_by_subscription(subscription_id, resource_group)

    async def update_job_status(self, job_id: UUID, status: str):
        """Update job status"""
        logger.info(f"update_status: job_id={job_id}, status={status}")
        return await self.repo.update_status(job_id, status)

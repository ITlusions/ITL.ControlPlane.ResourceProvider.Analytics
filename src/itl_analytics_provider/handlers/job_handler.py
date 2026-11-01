"""
Analytics Job handler mixin — business logic for job resources

Follows Core provider pattern with engine-based session management.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from itl_controlplane_sdk.analytics import AnalyticsJob

logger = logging.getLogger(__name__)


class AnalyticsJobHandlerMixin:
    """Handler for analytics job operations"""

    async def _create_analytics_job(
        self,
        subscription_id: str,
        resource_group: str,
        name: str,
        location: str,
        properties: Dict[str, Any],
        owner_id: str,
    ) -> AnalyticsJob:
        """Create analytics job"""
        logger.info(
            f"Creating analytics job {name}",
            extra={
                "subscription": subscription_id,
                "resource_group": resource_group,
                "owner": owner_id,
            },
        )

        async with self.engine.session() as session:
            from ..repositories.job_repo import AnalyticsJobRepository

            repo = AnalyticsJobRepository(session)
            job = await repo.create(
                {
                    "subscription_id": subscription_id,
                    "resource_group": resource_group,
                    "name": name,
                    "location": location,
                    "status": "Queued",
                    "owner_id": owner_id,
                    "job_type": properties.get("jobType", "batch"),
                    "compute_sku": properties.get("computeSku", "standard"),
                }
            )
            return job

    async def _get_analytics_job(
        self, subscription_id: str, resource_group: str, name: str
    ) -> Optional[AnalyticsJob]:
        """Get analytics job by name"""
        async with self.engine.session() as session:
            from ..repositories.job_repo import AnalyticsJobRepository

            repo = AnalyticsJobRepository(session)
            return await repo.get_by_name(subscription_id, resource_group, name)

    async def _list_analytics_jobs(
        self, subscription_id: str, resource_group: str
    ) -> List[AnalyticsJob]:
        """List analytics jobs"""
        async with self.engine.session() as session:
            from ..repositories.job_repo import AnalyticsJobRepository

            repo = AnalyticsJobRepository(session)
            return await repo.list_by_subscription(subscription_id, resource_group)

    async def _delete_analytics_job(
        self, subscription_id: str, resource_group: str, name: str
    ) -> bool:
        """Delete analytics job"""
        async with self.engine.session() as session:
            from ..repositories.job_repo import AnalyticsJobRepository

            repo = AnalyticsJobRepository(session)
            job = await repo.get_by_name(subscription_id, resource_group, name)
            if not job:
                return False
            return await repo.delete(job.id)

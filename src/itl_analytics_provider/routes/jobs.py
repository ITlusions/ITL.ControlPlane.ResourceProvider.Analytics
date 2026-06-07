"""
FastAPI routes for Analytics Job resources
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from itl_analytics_provider.models.notebook import AnalyticsJobRequest, AnalyticsJobResponse
from itl_analytics_provider.services.job_service import AnalyticsJobService
from itl_analytics_provider.repositories.job_repo import AnalyticsJobRepository
from itl_analytics_provider.core.database import get_async_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Analytics Jobs"])


@router.post(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/analyticsJobs",
    response_model=AnalyticsJobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_analytics_job(
    subscription_id: str,
    resource_group: str,
    request: AnalyticsJobRequest,
):
    """Create new analytics job

    TODO (Phase 2):
        - Submit to job scheduler
        - Setup execution environment
        - Configure monitoring
    """
    logger.info(
        f"POST /analyticsJobs: name={request.name}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = AnalyticsJobRepository(session)
            service = AnalyticsJobService(repo)

            job = await service.create_job(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                job_type=request.properties.job_type,
            )

            return AnalyticsJobResponse(
                id=job.id,
                name=job.name,
                type="ITL.Analytics/analyticsJobs",
                status=job.status,
                properties={"job_type": job.job_type},
                created_at=job.created_at,
            )

    except Exception as e:
        logger.error(f"Failed to create job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/analyticsJobs"
)
async def list_analytics_jobs(subscription_id: str, resource_group: str):
    """List analytics jobs in resource group"""
    logger.info(
        f"GET /analyticsJobs",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = AnalyticsJobRepository(session)
            service = AnalyticsJobService(repo)
            jobs = await service.list_jobs(subscription_id, resource_group)

            return {
                "value": [
                    AnalyticsJobResponse(
                        id=j.id,
                        name=j.name,
                        type="ITL.Analytics/analyticsJobs",
                        status=j.status,
                        properties={"job_type": j.job_type},
                        created_at=j.created_at,
                    )
                    for j in jobs
                ]
            }

    except Exception as e:
        logger.error(f"Failed to list jobs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/analyticsJobs/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_analytics_job(
    subscription_id: str, resource_group: str, job_id: UUID
):
    """Delete analytics job"""
    logger.info(
        f"DELETE /analyticsJobs/{job_id}",
        extra={"subscription": subscription_id, "resource_group": resource_group},
    )

    try:
        async with get_async_session() as session:
            repo = AnalyticsJobRepository(session)
            service = AnalyticsJobService(repo)
            result = await service.delete_job(job_id)

            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

            return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

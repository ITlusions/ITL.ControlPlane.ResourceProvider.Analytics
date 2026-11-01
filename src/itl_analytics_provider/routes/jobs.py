"""
Routes for Analytics Job resources

Provides analytics job management endpoints following Core provider pattern.
"""

from fastapi import APIRouter, HTTPException, status
from structlog import get_logger

from ..models import AnalyticsJobRequest, AnalyticsJobResponse

logger = get_logger()


def setup_jobs_routes(app, engine, provider) -> APIRouter:
    """
    Setup analytics job routes

    Endpoints:
    - POST   /analyticsJobs           - Create job
    - GET    /analyticsJobs           - List jobs
    - GET    /analyticsJobs/{name}    - Get job
    - DELETE /analyticsJobs/{name}    - Delete job

    Uses provider handler methods (Core provider pattern):
    - provider._create_analytics_job()
    - provider._get_analytics_job()
    - provider._list_analytics_jobs()
    - provider._delete_analytics_job()
    """
    router = APIRouter(tags=["analyticsJobs"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/analyticsJobs",
        response_model=AnalyticsJobResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_analytics_job(
        subscription_id: str, resource_group: str, request: AnalyticsJobRequest
    ):
        """Create analytics job"""
        logger.info(
            "create_analytics_job",
            subscription_id=subscription_id,
            resource_group=resource_group,
            name=request.name,
        )

        try:
            owner_id = "default-user"

            job = await provider._create_analytics_job(
                subscription_id=subscription_id,
                resource_group=resource_group,
                name=request.name,
                location=request.location,
                properties=request.properties.dict(),
                owner_id=owner_id,
            )

            return AnalyticsJobResponse(
                id=job.id,
                name=job.name,
                location=job.location,
                status=job.status,
                created_at=job.created_at,
                updated_at=job.updated_at,
                owner_id=job.owner_id,
                properties={
                    "jobType": job.job_type,
                    "computeSku": job.compute_sku,
                },
            )

        except Exception as e:
            logger.error("create_analytics_job_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/analyticsJobs",
        status_code=status.HTTP_200_OK,
    )
    async def list_analytics_jobs(subscription_id: str, resource_group: str):
        """List analytics jobs in resource group"""
        logger.info(
            "list_analytics_jobs",
            subscription_id=subscription_id,
            resource_group=resource_group,
        )

        try:
            jobs = await provider._list_analytics_jobs(subscription_id, resource_group)

            return {
                "value": [
                    AnalyticsJobResponse(
                        id=j.id,
                        name=j.name,
                        location=j.location,
                        status=j.status,
                        created_at=j.created_at,
                        updated_at=j.updated_at,
                        owner_id=j.owner_id,
                        properties={
                            "jobType": j.job_type,
                            "computeSku": j.compute_sku,
                        },
                    )
                    for j in jobs
                ]
            }

        except Exception as e:
            logger.error("list_analytics_jobs_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/analyticsJobs/{job_name}",
        response_model=AnalyticsJobResponse,
        status_code=status.HTTP_200_OK,
    )
    async def get_analytics_job(
        subscription_id: str, resource_group: str, job_name: str
    ):
        """Get analytics job details"""
        logger.info(
            "get_analytics_job",
            subscription_id=subscription_id,
            resource_group=resource_group,
            job_name=job_name,
        )

        try:
            job = await provider._get_analytics_job(
                subscription_id, resource_group, job_name
            )

            if not job:
                raise HTTPException(status_code=404, detail="Job not found")

            return AnalyticsJobResponse(
                id=job.id,
                name=job.name,
                location=job.location,
                status=job.status,
                created_at=job.created_at,
                updated_at=job.updated_at,
                owner_id=job.owner_id,
                properties={
                    "jobType": job.job_type,
                    "computeSku": job.compute_sku,
                },
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("get_analytics_job_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Analytics/analyticsJobs/{job_name}",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def delete_analytics_job(
        subscription_id: str, resource_group: str, job_name: str
    ):
        """Delete analytics job"""
        logger.info(
            "delete_analytics_job",
            subscription_id=subscription_id,
            resource_group=resource_group,
            job_name=job_name,
        )

        try:
            result = await provider._delete_analytics_job(
                subscription_id, resource_group, job_name
            )

            if not result:
                raise HTTPException(status_code=404, detail="Job not found")

            return None

        except HTTPException:
            raise
        except Exception as e:
            logger.error("delete_analytics_job_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

    return router

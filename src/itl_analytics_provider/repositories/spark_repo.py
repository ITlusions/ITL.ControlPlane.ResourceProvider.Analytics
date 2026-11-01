"""
Repository layer for Spark Cluster resources

Provides basic CRUD operations for SparkCluster resources.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from itl_controlplane_sdk.analytics import BaseAnalyticsRepository, SparkCluster

logger = logging.getLogger(__name__)


class SparkClusterRepository(BaseAnalyticsRepository[SparkCluster]):
    """Data access layer for Spark clusters"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, SparkCluster)


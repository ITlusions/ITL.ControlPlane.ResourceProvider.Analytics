"""
Repository layer for Analytics Job resources

Provides basic CRUD operations for job resources.
Custom operations (e.g., status updates) are handled by the handler layer.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from itl_controlplane_sdk.analytics import BaseAnalyticsRepository, AnalyticsJob

logger = logging.getLogger(__name__)


class AnalyticsJobRepository(BaseAnalyticsRepository[AnalyticsJob]):
    """Data access layer for analytics jobs"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, AnalyticsJob)



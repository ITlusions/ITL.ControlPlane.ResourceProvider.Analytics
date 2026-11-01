"""
Repository layer for Dataset resources

Provides basic CRUD operations for dataset resources.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from itl_controlplane_sdk.analytics import BaseAnalyticsRepository, Dataset

logger = logging.getLogger(__name__)


class DatasetRepository(BaseAnalyticsRepository[Dataset]):
    """Data access layer for datasets"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Dataset)


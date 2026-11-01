"""
Repository layer for Model Registry resources

Provides basic CRUD operations for model resources.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from itl_controlplane_sdk.analytics import BaseAnalyticsRepository, Model

logger = logging.getLogger(__name__)


class ModelRepository(BaseAnalyticsRepository[Model]):
    """Data access layer for model registry"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Model)


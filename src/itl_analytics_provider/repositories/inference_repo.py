"""
Repository layer for Inference Endpoint resources

Provides basic CRUD operations for inference endpoint resources.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from itl_controlplane_sdk.analytics import BaseAnalyticsRepository, InferenceEndpoint

logger = logging.getLogger(__name__)


class InferenceEndpointRepository(BaseAnalyticsRepository[InferenceEndpoint]):
    """Data access layer for inference endpoints"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, InferenceEndpoint)


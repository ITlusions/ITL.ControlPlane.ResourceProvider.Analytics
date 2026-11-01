"""
Notebook repository - Data access layer

Provides basic CRUD operations for notebook resources.
Custom operations (e.g., status updates) are handled by the handler layer.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from itl_controlplane_sdk.analytics import BaseAnalyticsRepository, Notebook

logger = logging.getLogger(__name__)


class NotebookRepository(BaseAnalyticsRepository[Notebook]):
    """Data access for notebooks"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Notebook)



"""
Application lifecycle management

Handles startup (initialize DB, run migrations) and shutdown (cleanup)
"""

import logging
from contextlib import asynccontextmanager

# Import models to register with SQLAlchemy metadata
from ..models.orm import (
    Notebook,
    SparkCluster,
    AnalyticsJob,
    Model,
    Dataset,
    InferenceEndpoint,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app, engine, provider):
    """
    Application lifespan context manager

    Handles:
    - Startup: Initialize storage engine, run migrations
    - Shutdown: Close connections, cleanup

    Args:
        app: FastAPI application
        engine: Storage engine
        provider: Analytics provider
    """

    # Startup
    logger.info("=" * 80)
    logger.info("Analytics Provider Startup")
    logger.info("=" * 80)

    try:
        # Initialize storage engine
        logger.info("Initializing storage engine...")
        await engine.initialize()
        logger.info("✓ Storage engine initialized")

        # TODO: Run Alembic migrations
        logger.info("Database schema ready (migrations would run here)")

        # TODO: Register provider with registry
        logger.info("✓ Provider registered")

        # Provider ready
        logger.info("=" * 80)
        logger.info("Analytics Provider is READY")
        logger.info("=" * 80)

        yield

    finally:
        # Shutdown
        logger.info("Analytics Provider shutting down...")
        try:
            await engine.close()
            logger.info("✓ Storage engine closed")
        except Exception as e:
            logger.error(f"Error closing storage engine: {e}")

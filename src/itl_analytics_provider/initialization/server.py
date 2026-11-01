"""
Analytics Provider Server

Extends SDK BaseProviderServer with analytics-specific configuration
"""

import os
import logging
from itl_controlplane_sdk.fastapi import BaseProviderServer
from itl_controlplane_sdk.persistence import SQLAlchemyStorageEngine
from ..analytics import AnalyticsProvider
from .app_factory import create_app
from ..config import get_settings

logger = logging.getLogger(__name__)


class AnalyticsProviderServer(BaseProviderServer):
    """
    Analytics Provider Server

    Manages:
    - Storage engine initialization
    - Provider instance creation
    - FastAPI app creation
    - Mode selection (api/servicebus/hybrid)
    """

    def __init__(self):
        """Initialize Analytics Provider Server"""
        settings = get_settings()
        
        logger.info("Initializing Analytics Provider Server")
        
        # Create storage engine
        self.engine = SQLAlchemyStorageEngine(
            database_url=settings.database_url
        )
        
        # Create provider instance
        self.provider = AnalyticsProvider(engine=self.engine)
        
        logger.info(f"Provider: {self.provider.namespace} v{self.provider.version}")
        logger.info(f"Resource types: {', '.join(self.provider.get_resource_types())}")

    def create_app(self):
        """Create FastAPI application"""
        return create_app(self, self.engine, self.provider)

    def run(self, host: str = "0.0.0.0", port: int = 9509, **kwargs):
        """
        Run the Analytics Provider Server

        Args:
            host: Bind host (default: 0.0.0.0)
            port: Bind port (default: 9509)
            **kwargs: Additional uvicorn arguments
        """
        settings = get_settings()
        
        print("=" * 80)
        print("Analytics Provider Configuration")
        print("=" * 80)
        print(f"Mode: {settings.provider_mode.upper()}")
        print(f"Host: {host}:{port}")
        print(f"Provider: {self.provider.namespace} v{self.provider.version}")
        print(f"Resource Types: {', '.join(self.provider.get_resource_types())}")
        print("=" * 80)
        
        # Create app
        app = self.create_app()
        
        # Run with uvicorn
        import uvicorn
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=settings.log_level.lower(),
            **kwargs
        )

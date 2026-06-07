"""
Analytics Provider initialization package

Provides:
- AnalyticsProviderServer: Main server class
- create_app: FastAPI app factory
- app_lifespan: Startup/shutdown management
"""

from .server import AnalyticsProviderServer

__all__ = ["AnalyticsProviderServer"]

"""
FastAPI application factory for Analytics Provider

Creates and configures the FastAPI application with:
- Standard SDK middleware (audit, observability)
- Route setup
- Lifecycle management
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from itl_controlplane_sdk.persistence.audit import AuditContextMiddleware
from itl_controlplane_sdk.api import setup_generic_routes, setup_observability_routes
from ..routes import (
    setup_notebooks_routes,
    setup_spark_clusters_routes,
    setup_analytics_jobs_routes,
    setup_models_routes,
    setup_datasets_routes,
    setup_inference_endpoints_routes,
)
from .lifecycle import app_lifespan


def create_app(server, engine, provider) -> FastAPI:
    """
    Create and configure FastAPI application

    Args:
        server: AnalyticsProviderServer instance
        engine: Storage engine
        provider: AnalyticsProvider instance

    Returns:
        Configured FastAPI application
    """

    app = FastAPI(
        title="ITL Analytics Provider",
        version="0.1.0",
        description="Analytics Resource Provider for Control Plane",
        lifespan=lambda app: app_lifespan(app, engine, provider),
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # SDK standard middleware
    app.add_middleware(AuditContextMiddleware)

    # SDK standard routes
    setup_generic_routes(app)
    setup_observability_routes(app, engine)

    # Provider-specific routes
    app.include_router(setup_notebooks_routes(app, engine, provider), prefix="/api/v1")
    app.include_router(setup_spark_clusters_routes(app, engine, provider), prefix="/api/v1")
    app.include_router(setup_analytics_jobs_routes(app, engine, provider), prefix="/api/v1")
    app.include_router(setup_models_routes(app, engine, provider), prefix="/api/v1")
    app.include_router(setup_datasets_routes(app, engine, provider), prefix="/api/v1")
    app.include_router(
        setup_inference_endpoints_routes(app, engine, provider), prefix="/api/v1"
    )

    return app

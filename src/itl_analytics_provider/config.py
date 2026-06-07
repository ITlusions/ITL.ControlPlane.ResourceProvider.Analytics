"""
Configuration for Analytics Provider
"""

import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Analytics Provider configuration from environment variables"""

    # Service settings
    service_name: str = Field(default="Analytics Provider", alias="SERVICE_NAME")
    service_port: int = Field(default=9509, alias="SERVICE_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://analytics:analytics-dev@localhost/analytics_db",
        alias="DATABASE_URL",
    )

    # Cache
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # MinIO
    minio_endpoint: str = Field(default="localhost:9000", alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(default="minioadmin", alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(default="minioadmin", alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(default="analytics", alias="MINIO_BUCKET")
    minio_secure: bool = Field(default=False, alias="MINIO_SECURE")

    # Kubernetes
    kubeconfig_path: Optional[str] = Field(default=None, alias="KUBECONFIG")
    kubernetes_namespace: str = Field(default="analytics", alias="K8S_NAMESPACE")

    # Container provider integration
    container_provider_url: str = Field(
        default="http://localhost:8002", alias="CONTAINER_PROVIDER_URL"
    )

    # Accelerator provider integration
    accelerator_provider_url: str = Field(
        default="http://localhost:8003", alias="ACCELERATOR_PROVIDER_URL"
    )

    # Storage provider integration
    storage_provider_url: str = Field(
        default="http://localhost:8001", alias="STORAGE_PROVIDER_URL"
    )

    # BrainCell integration
    braincell_url: str = Field(default="http://localhost:9504", alias="BRAINCELL_URL")

    # Provider mode
    provider_mode: str = Field(default="api", alias="PROVIDER_MODE")

    # Control Plane
    controlplane_api_url: str = Field(
        default="http://localhost:8081", alias="CONTROLPLANE_API_URL"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get singleton settings instance"""
    return Settings()

"""
External service clients

Provides integration with:
- Container Provider (pod orchestration)
- MinIO Storage (S3-compatible storage)
- Storage Provider (data lake)
"""

from .container_client import ContainerClient
from .minio_client import MinIOClient

__all__ = [
    "ContainerClient",
    "MinIOClient",
]

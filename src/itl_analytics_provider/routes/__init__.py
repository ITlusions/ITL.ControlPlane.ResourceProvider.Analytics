"""
Routes package for Analytics resources

Individual routers for each resource type:
- Notebooks
- Spark Clusters
- Analytics Jobs
- Models
- Datasets
- Inference Endpoints
"""

from . import notebooks
from . import spark
from . import jobs
from . import models
from . import datasets
from . import inference

from .notebooks import setup_notebooks_routes
from .spark import setup_spark_clusters_routes
from .jobs import setup_analytics_jobs_routes
from .models import setup_models_routes
from .datasets import setup_datasets_routes
from .inference import setup_inference_endpoints_routes

__all__ = [
    "notebooks",
    "spark",
    "jobs",
    "models",
    "datasets",
    "inference",
    "setup_notebooks_routes",
    "setup_spark_clusters_routes",
    "setup_analytics_jobs_routes",
    "setup_models_routes",
    "setup_datasets_routes",
    "setup_inference_endpoints_routes",
]

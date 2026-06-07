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

__all__ = [
    "notebooks",
    "spark",
    "jobs",
    "models",
    "datasets",
    "inference",
]

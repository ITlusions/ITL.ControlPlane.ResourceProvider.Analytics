"""
Analytics Provider handlers — business logic mixins

Each handler mixin encapsulates CRUD operations for a resource type,
following the Core provider pattern with engine-based session management.
"""

from .notebook_handler import NotebookHandlerMixin
from .spark_handler import SparkClusterHandlerMixin
from .job_handler import AnalyticsJobHandlerMixin
from .model_handler import ModelHandlerMixin
from .dataset_handler import DatasetHandlerMixin
from .inference_handler import InferenceEndpointHandlerMixin

__all__ = [
    "NotebookHandlerMixin",
    "SparkClusterHandlerMixin",
    "AnalyticsJobHandlerMixin",
    "ModelHandlerMixin",
    "DatasetHandlerMixin",
    "InferenceEndpointHandlerMixin",
]

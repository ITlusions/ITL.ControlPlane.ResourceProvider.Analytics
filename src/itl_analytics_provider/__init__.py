"""
Analytics Provider package

Manages:
- Notebooks (Jupyter sessions)
- Spark Clusters (distributed compute)
- Analytics Jobs (workflows)
- Models (ML registry)
- Datasets (data catalog)
- Inference Endpoints (model serving)
"""

from .analytics import AnalyticsProvider

__version__ = "0.1.0"
__all__ = ["AnalyticsProvider", "__version__"]

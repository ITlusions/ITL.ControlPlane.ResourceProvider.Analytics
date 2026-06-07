# Analytics Provider Architecture

## Overview

The Analytics Provider is a Control Plane resource provider that manages data science and ML infrastructure:

- **Notebooks**: Interactive Jupyter-based development environments
- **Spark Clusters**: Distributed compute with GPU acceleration
- **Analytics Jobs**: Scheduled ETL and processing workloads
- **Models**: ML model registry with versioning
- **Datasets**: Data catalog with metadata
- **Inference Endpoints**: Model serving APIs

## Namespace & Version

- **Namespace**: `ITL.Analytics`
- **Version**: `2024-06-01`
- **Port**: `9509`

## Resource Types

```
ITL.Analytics/notebooks               Notebook sessions
ITL.Analytics/sparkClusters          Spark distributed compute
ITL.Analytics/analyticsJobs          Scheduled jobs/workflows
ITL.Analytics/models                 ML model registry
ITL.Analytics/datasets               Data catalog
ITL.Analytics/inferenceEndpoints     Model serving
```

## Architecture Diagram

```

             Analytics Provider API                      
  Port 9509 - Manages analytics resources               

                                         
    Notebooks   Spark Clusters  Jobs     Models
                                         
    
       Orchestration Layer (Services)               
    
     - NotebookService     (pod management)         
     - SparkService        (cluster orchestration)  
     - JobOrchestratorService (workflow engine)     
     - ModelRegistryService   (ML tracking)         
     - DatasetCatalogService  (metadata)            
    
                                         
    
    Container AcceleratorStorage  Identity 
    Provider  Provider  Provider Provider 
    
                                         
    K8s Pods   GPU Nodes    S3/Blobs  Service
                                    Accounts
```

## Data Flow: Create Notebook

```
User Request:
  POST /providers/ITL.Analytics/notebooks
  {
    "name": "ml-project",
    "location": "westeurope",
    "properties": { "kernel": "python3.11" }
  }
    
Analytics Provider:
  1. Routes request  setup_notebooks_routes()
  2. Validates request
  3. Creates service instance (NotebookService)
  4. Calls service.create_notebook()
    
Service Layer:
  1. Call Container Provider API
      Create JupyterLab pod
  2. Call Storage Provider API
      Allocate notebook storage
  3. Call Identity Provider API
      Create service account
  4. Store metadata in repository
    
Response:
  {
    "id": "/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Analytics/notebooks/ml-project",
    "name": "ml-project",
    "status": "Running",
    "url": "https://notebooks.analytics.itl.com/ml-project"
  }
```

## Data Flow: Create Spark Cluster

```
User Request:
  POST /providers/ITL.Analytics/sparkClusters
  {
    "name": "ml-training",
    "workers": {"count": 3, "gpu_per_worker": 4}
  }
    
Analytics Provider:
  1. Routes to setup_spark_clusters_routes()
  2. Creates SparkService
  3. Calls service.create_cluster()
    
Service Layer:
  1. Call Accelerator Provider
      Allocate GPU nodes (3H100 nodes)
  2. Call Container Provider
      Create Spark driver pod
      Create Spark worker pods (pinned to GPU nodes)
  3. Initialize Spark master/slaves
  4. Configure networking
  5. Store cluster metadata
    
Response:
  {
    "id": "/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Analytics/sparkClusters/ml-training",
    "status": "Creating",
    "master_url": "spark://ml-training-driver:7077"
  }
```

## Integration Points

### Container Provider

Used by Analytics Provider for:
- Creating Jupyter notebook pods
- Creating Spark driver/worker pods
- Creating inference serving containers

**API Used**:
```
POST /providers/ITL.Container/pods
{
  "name": "jupyter-ml-project",
  "image": "jupyter/datascience-notebook:latest",
  "resources": {"cpu": "4", "memory": "16Gi"}
}
```

### Accelerator Provider

Used for GPU compute:
- Allocating H100/A100 nodes for Spark workers
- Tracking GPU utilization and costs

**API Used**:
```
POST /providers/ITL.Accelerator/sparkNodes?allocate=3
{
  "gpu_count": 4,
  "gpu_model": "H100",
  "duration_minutes": 120
}
```

### Storage Provider

Used for persistent data:
- Notebook storage
- Model artifacts
- Spark shuffle storage
- Dataset files

**API Used**:
```
POST /providers/ITL.Storage/blobs
{
  "bucket": "analytics",
  "path": "notebooks/ml-project/",
  "size_gb": 100
}
```

### Identity Provider

Used for authentication:
- Service accounts for job execution
- RBAC for resource access

**API Used**:
```
POST /providers/ITL.Identity/serviceIdentities
{
  "name": "notebook-ml-project-executor",
  "roles": ["analytics-reader", "storage-writer
}
```

### BrainCell Integration

Used for metadata and governance:
- Store notebook metadata (created by, when, status)
- Track model lineage (trained on dataset X with params Y)
- Audit logging (who accessed what)

**API Used**:
```
POST /api/cells/analytics/notebooks/{notebook_id}
{
  "created_by": "user@company.com",
  "kernel": "python3.11",
  "status": "running",
  "metadata": {...}
}
```

## Implementation Status

| Component | Status | Next Steps |
|-----------|--------|-----------|
| Notebooks |  Scaffolded | Implement pod creation, persistence |
| Spark Clusters |  Scaffolded | Implement cluster orchestration |
| Analytics Jobs |  Scaffolded | Implement job scheduling |
| Models |  Scaffolded | MLflow integration |
| Datasets |  Scaffolded | Catalog + lineage |
| Inference |  Scaffolded | Model serving |

## Resource Provider Pattern

Analytics Provider follows the standard Control Plane SDK pattern:

```python
from itl_controlplane_sdk.providers import ResourceProvider

class AnalyticsProvider(ResourceProvider):
    @property
    def namespace(self) -> str:
        return "ITL.Analytics"
    
    @property
    def version(self) -> str:
        return "2024-06-01"
    
    def get_resource_types(self) -> List[st:
        return ["notebooks", "sparkClusters", ..
```

## Route Pattern

All routes use the setup function pattern for dependency injection:

```python
def setup_notebooks_routes(app, engine, provider) -> APIRouter:
    router = APIRouter(tags=["notebooks)
    
    @router.post("/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Analytics/notebooks")
    async def create_notebook(...):
        # Can access: app, engine, provider
        pass
    
    return router
```

Benefits:
- Dependency injection (access to storage engine, provider)
- Better testability
- Cleaner separation of concerns

## Running the Provider

### Development

```bash
# Install
pip install -e ".[de"

# Start infrastructure
docker compose up -d

# Run provider
python -m itl_analytics_provider.main
```

### Production (Kubernetes)

```bash
# Build image
docker build -t analytics-provider:0.1.0 .

# Push to registry
docker push itl-registry/analytics-provider:0.1.0

# Deploy
kubectl apply -f k8s/deployment.yaml
```

## Next Steps

1. **Implement Notebook Routes** (Week 1-2)
   - Pod creation via Container provider
   - Persistent storage setup
   - JupyterLab configuration

2. **Implement Spark Orchestration** (Week 3-4)
   - GPU node allocation via Accelerator provider
   - Spark cluster setup
   - Auto-scaling

3. **Add Job Scheduling** (Week 5-6)
   - Temporal workflow integration
   - Job submission/monitoring

4. **Model Registry** (Week 7-8)
   - MLflow integration
   - Model versioning
   - Artifact storage

5. **Testing & Optimization** (Week 9-12)
   - End-to-end testing
   - Performance tuning
   - Documentation

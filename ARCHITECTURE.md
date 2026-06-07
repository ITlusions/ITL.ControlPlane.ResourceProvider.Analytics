# Architecture & File Structure Overview

**Last Updated**: June 7, 2026  
**Total Resource Types**: 6 (1 complete, 5 stubs)  
**Total Files**: 45+ (source + tests + docs)

---

##  **Complete Directory Structure**

```
ITL.ControlPlane.ResourceProvider.Analytics/

 src/itl_analytics_provider/
   
    __init__.py                         # Package init
    main.py                             # FastAPI app startup
   
    models/
       __init__.py
       orm.py                          # SQLAlchemy ORM (6 resource types)
       notebook.py                     # Pydantic validation (Request/Response)
   
    repositories/
       __init__.py                     # Updated: exports all 6
       notebook_repo.py               #  Phase 1 COMPLETE
       spark_repo.py                  #  Phase 2 stub
       job_repo.py                    #  Phase 2 stub
       model_repo.py                  #  Phase 3 stub
       dataset_repo.py                #  Phase 2-3 stub
       inference_repo.py              #  Phase 3 stub
   
    services/
       __init__.py                     # Updated: exports all 6
       notebook_service.py            #  COMPLETE (Container + MinIO)
       spark_service.py               #  Stub (Container TODOs)
       job_service.py                 #  Stub (Scheduler TODOs)
       model_service.py               #  Stub (MLflow TODOs)
       dataset_service.py             #  Stub (Lineage TODOs)
       inference_service.py           #  Stub (K8s TODOs)
   
    routes/
       __init__.py                     # Updated: imports routers
       notebooks.py                    #  COMPLETE (4 endpoints)
       spark.py                       #  Stub (4 endpoints)
       jobs.py                        #  Stub (3 endpoints)
       models.py                      #  Stub (3 endpoints)
       datasets.py                    #  Stub (3 endpoints)
       inference.py                   #  Stub (3 endpoints)
   
    cells/
       __init__.py                     # New: cell exports
       notebook_cell.py               #  COMPLETE (BrainCell integration)
       spark_cluster_cell.py          #  Stub
       analytics_job_cell.py          #  Stub
       model_cell.py                  #  Stub
       dataset_cell.py                #  Stub
       inference_endpoint_cell.py     #  Stub
   
    clients/
       container_client.py            #  COMPLETE (Container Provider)
       minio_client.py                #  Stub (MinIO integration)
   
    core/
        config.py                      # Settings (Pydantic)
        database.py                    # Async SQLAlchemy engine
        models.py                      # Base ORM model

 tests/
    test_notebook_crud.py              #  6 test cases (PASS)
    test_notebook_routes.py            # TODO: integration tests

 docs/
    ARCHITECTURE.md
    ENDPOINTS.md
    ROADMAP.md

 docker-compose.yml                     # Local infra (Postgres, MinIO, Redis)
 Dockerfile                             # Provider container image
 pyproject.toml                         # Python package config
 alembic.ini                            # Database migrations

 migrations/
     env.py
     versions/
         (auto-generated)

 Documentation Files:
     GETTING_STARTED.md                 # 10-min quick start
     USER_SCENARIO.md                   # Alice Chen's workflow
     PHASE1_STATUS.md                   # Implementation report
     PHASE1_INTEGRATION_STATUS.md       # Container/MinIO details
     PHASE1_GUIDE.md                    # Technical testing guide
     DATABRICKS_COMPARISON.md           # Feature gap analysis
     STUBS_IMPLEMENTATION.md            # This document
     ARCHITECTURE.md                    # (This file)
```

---

##  **Data Flow: Request  Response**

### **Flow 1: Create Spark Cluster** (POST 201)

```
User Request:

 POST /subscriptions/sub-001/resourceGroups/rg-test/providers 
      /ITL.Analytics/sparkClusters                            
 Content-Type: application/json                               
                                                              
 {                                                            
   "name": "cluster-1",                                      
   "location": "eastus",                                      
   "properties": {                                            
     "driver_cpu": 8,                                         
     "driver_memory_gb": 32,                                  
     "worker_count": 3,                                       
     "worker_cpu": 16,                                        
     "worker_memory_gb": 64,                                  
     "worker_gpus": 4                                         
   }                                                          
 }                                                            

          
FastAPI Route Handler (routes/spark.py @ create_spark_cluster)
  1. Parse path params: subscription_id, resource_group
  2. Validate body: SparkClusterRequest (Pydantic)
  3. Create async session
  4. Instantiate repo + service
          
Service Layer (services/spark_service.py @ create_cluster)
  1. Log: "create_cluster: name=cluster-1, location=eastus"
  2. Create cluster_data dict
  3. Call repo.create(cluster_data)
  4. Log: "Cluster created: <id>"
  5. TODO: Create pods via Container Provider
  6. TODO: Wait for running
  7. TODO: Setup networking
  8. TODO: Update status to Running
  9. Return cluster object
          
Repository Layer (repositories/spark_repo.py @ create)
  1. Create SparkCluster ORM instance
  2. Add to session: session.add(cluster)
  3. Commit: await session.commit()
  4. Refresh: await session.refresh(cluster)
  5. Log: "Created Spark cluster: <id>"
  6. Return hydrated cluster
          
Database (PostgreSQL)
  INSERT INTO spark_clusters (
    id, subscription_id, resource_group, name, location,
    status, driver_cpu, driver_memory_gb, worker_count,
    worker_cpu, worker_memory_gb, worker_gpus, created_at,
    updated_at, owner_id
  ) VALUES (...)
          
Response:

 HTTP 201 Created                                             
 Content-Type: application/json                               
                                                              
 {                                                            
   "id": "550e8400-e29b-41d4-a716-446655440000",            
   "name": "cluster-1",                                       
   "type": "ITL.Analytics/sparkClusters",                    
   "location": "eastus",                                      
   "status": "Creating",                                      
   "properties": {                                            
     "driver_cpu": 8,                                         
     "driver_memory_gb": 32,                                  
     "worker_count": 3,                                       
     "worker_cpu": 16,                                        
     "worker_memory_gb": 64,                                  
     "worker_gpus": 4                                         
   },                                                         
   "created_at": "2026-06-07T10:30:00Z",                     
   "updated_at": "2026-06-07T10:30:00Z"                      
 }                                                            

```

---

### **Flow 2: List Clusters** (GET 200)

```
User Request:

 GET /subscriptions/sub-001/resourceGroups/rg-test/providers  
     /ITL.Analytics/sparkClusters                             

          
Route Handler: list_spark_clusters
  1. Create session + repo + service
  2. Call service.list_clusters(sub_001, rg-test)
          
Service: list_clusters
  1. Call repo.list_by_subscription(sub_001, rg-test)
          
Repository: list_by_subscription
  1. SELECT * FROM spark_clusters WHERE subscription_id=? AND resource_group=?
  2. Return List[SparkCluste
          
Route Handler (continued):
  1. Transform to SparkClusterResponse objects
  2. Return {"value": [SparkClusterResponse, ..}
          
Response:

 HTTP 200 OK                                                  
 {                                                            
   "value": [                                                 
     {                                                        
       "id": "550e8400...",                                  
       "name": "cluster-1",                                   
       "type": "ITL.Analytics/sparkClusters",                
       "status": "Creating",                                  
       ...                                                    
     },                                                       
     ...                                                      
                                                            
 }                                                            

```

---

##  **Class Hierarchy & Inheritance**

### **ORM Model Hierarchy**

```
SQLAlchemy Base
     SparkCluster
        id: UUID (PK)
        subscription_id: str
        resource_group: str
        name: str
        location: str
        status: Enum (Creating, Running, Stopping, Stopped, Error, Terminating)
        driver_cpu: int
        driver_memory_gb: int
        worker_count: int
        worker_cpu: int
        worker_memory_gb: int
        worker_gpus: int
        driver_pod: Optional[st
        master_url: Optional[st
        created_at: datetime
        updated_at: datetime
        deleted_at: Optional[datetim
        owner_id: str
    
     AnalyticsJob
        id, subscription_id, resource_group, name, location
        status: Enum (Submitted, Running, Succeeded, Failed, Cancelled)
        job_type: str (etl, training, validation)
        compute_cluster_id: Optional[UUI
        started_at, completed_at: Optional[datetim
        ... (timestamps, owner_id)
    
     Model
        id, subscription_id, resource_group, name, location
        framework: str (sklearn, pytorch, tensorflow)
        version: str
        artifact_path: Optional[st
        metrics: Dict[str, An
        ... (timestamps, owner_id)
    
     Dataset
        id, subscription_id, resource_group, name, location
        data_location: str
        schema: Dict[str, An
        row_count: Optional[in
        completeness: Optional[st
        ... (timestamps, owner_id)
    
     InferenceEndpoint
        id, subscription_id, resource_group, name, location
        status: Enum (Creating, Running, Stopping, Stopped, Error)
        model_id: UUID
        replica_count: int
        cpu_per_replica: int
        memory_gb_per_replica: int
        url: Optional[st
        ... (timestamps, owner_id)
    
     Notebook ( Phase 1)
         id, subscription_id, resource_group, name, location
         status: Enum (Creating, Running, Stopped, Error, Terminating)
         kernel: str
         compute_sku: str
         memory_gb, cpu_cores, storage_gb: int
         pod_name: Optional[st
         storage_bucket: Optional[st
         notebook_url: Optional[st
         ... (timestamps, owner_id)
```

---

### **Repository Pattern**

```
*Repository (Abstract Pattern)
 __init__(session: AsyncSession)
 create(data: dict) -> T
 get_by_id(id: UUID) -> Optional[
 list_by_subscription(sub: str, rg: str) -> List[
 update(id: UUID, data: dict) -> Optional[
 delete(id: UUID) -> bool
 update_status(id: UUID, status: str) -> Optional[  [optional, for statefu
```

**Implementations**:
- SparkClusterRepository
- AnalyticsJobRepository
- ModelRepository
- DatasetRepository
- InferenceEndpointRepository
- NotebookRepository ( Complete)

---

### **Service Pattern**

```
*Service (Business Logic Pattern)
 __init__(repo: *Repository)
 create_*(...) -> T  [with validation, orchestratio
 delete_*(id: UUID) -> bool
 list_*(sub: str, rg: str) -> List[
 update_*_status(id: UUID, status: str) -> Optional[
 TODO markers for Phase 2-4 implementations
```

**Implementations**:
- SparkClusterService
- AnalyticsJobService
- ModelService
- DatasetService
- InferenceEndpointService
- NotebookService ( Complete)

---

### **Route Pattern**

```
FastAPI Router for each resource type:
 POST   /.../{resource} -> 201 Created
 GET    /.../{resource} -> 200 OK (list)
 GET    /.../{resource}/{id} -> 200 OK or 404 NotFound
 DELETE /.../{resource}/{id} -> 204 NoContent
```

**Implementations**:
- routes/notebooks.py ( Complete, 4 endpoints)
- routes/spark.py ( Stub, 4 endpoints)
- routes/jobs.py ( Stub, 3 endpoints)
- routes/models.py ( Stub, 3 endpoints)
- routes/datasets.py ( Stub, 3 endpoints)
- routes/inference.py ( Stub, 3 endpoints)

---

### **BrainCell Integration Pattern**

```
*Cell(MemoryCell)
 get_router() -> APIRouter
    Returns routes/X.py router for FastAPI registration
 get_models() -> List[OR
    Returns models for Alembic migrations
 register_mcp_tools(mcp) [Phase 
     Decorates functions with @mcp.tool("...")
```

**Implementations**:
- cells/notebook_cell.py ( Complete)
- cells/spark_cluster_cell.py ( Stub)
- cells/analytics_job_cell.py ( Stub)
- cells/model_cell.py ( Stub)
- cells/dataset_cell.py ( Stub)
- cells/inference_endpoint_cell.py ( Stub)

---

##  **Integration Points (TO IMPLEMENT)**

### **Phase 2: Container Provider**

**Location**: `services/spark_service.py` lines ~45, 85

**Integration**:
```python
from itl_analytics_provider.clients.container_client import ContainerClient

async with ContainerClient(base_url="http://container-provider:9508") as client:
    # Create driver pod
    pod = await client.create_pod(...)
    
    # Wait for running
    running = await client.wait_for_pod_running(...)
    
    # Get pod IP/URL
    url = await client.get_pod_url(...)
    
    # Delete pod (on cleanup)
    await client.delete_pod(...)
```

**Expected Container Provider Endpoints**:
```
POST   /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Container/pods
GET    /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Container/pods/{name}
DELETE /subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Container/pods/{name}
```

---

### **Phase 2: MinIO Storage**

**Location**: `services/notebook_service.py` lines ~73 (already integrated!)

**Integration** (Already done for notebooks):
```python
from itl_analytics_provider.clients.minio_client import MinIOClient

async with MinIOClient(endpoint="http://minio:9000") as client:
    # Create bucket
    await client.create_bucket(bucket_name)
    
    # Setup CORS
    await client.setup_cors(bucket_name)
    
    # Setup policy
    await client.setup_bucket_policy(bucket_name)
    
    # Get bucket URL
    url = await client.get_bucket_url(bucket_name)
    
    # Delete bucket (on cleanup)
    await client.delete_bucket(bucket_name)
```

---

### **Phase 3: MLflow Integration**

**Location**: `services/model_service.py` line ~38

**Integration** (Planned):
```python
import mlflow

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment(model.name)

with mlflow.start_run():
    mlflow.log_param("framework", model.framework)
    mlflow.log_artifact(model.artifact_path)
    # Model auto-tracked in registry
```

---

### **Phase 3: Kubernetes Model Serving**

**Location**: `services/inference_service.py` line ~44

**Integration** (Planned):
```python
from kubernetes import client, config

# Load kubeconfig
config.load_incluster_config()

# Create deployment
deployment = client.V1Deployment(
    metadata=client.V1ObjectMeta(name=endpoint.name),
    spec=client.V1DeploymentSpec(
        replicas=endpoint.replica_count,
        ...
    )
)
api_instance = client.AppsV1Api()
api_instance.create_namespaced_deployment("default", deployment)

# Create service
service = client.V1Service(
    metadata=client.V1ObjectMeta(name=endpoint.name),
    spec=client.V1ServiceSpec(
        type="LoadBalancer",
        ...
    )
)
api_instance = client.CoreV1Api()
api_instance.create_namespaced_service("default", service)
```

---

##  **Deployment Architecture**

### **Local Development** (docker-compose)

```
Host Machine
 Provider (FastAPI on :9509)
 PostgreSQL (on :5433)
 MinIO (on :9000)
 Redis (on :6379)
 pgAdmin (on :5050)
```

**Start with**:
```bash
docker-compose up -d
alembic upgrade head
python -m itl_analytics_provider.main
# Visit http://localhost:9509/docs
```

---

### **Production** (Kubernetes on ITL Control Plane)

```
Azure Container Registry
 itl-analytics-provider:1.0.0
        
Kubernetes Deployment (Pod)
 Port 9509 (FastAPI service)
 ConfigMap (environment)
 Secret (credentials)
 PersistentVolumeClaim (alembic versions)
        
Resources
 PostgreSQL cluster (managed)
 MinIO tenant (managed)
 Container Provider (ITL service on :9508)
 BrainCell platform (for audit logs)
```

**Deploy with**:
```bash
docker build -t myregistry.azurecr.io/itl-analytics-provider:1.0.0 .
docker push myregistry.azurecr.io/itl-analytics-provider:1.0.0
kubectl apply -f kubernetes/deployment.yaml
```

---

##  **Testing Matrix**

### **Unit Tests**

```
 test_notebook_crud.py (6 cases)
   test_create_notebook
   test_list_notebooks
   test_get_notebook
   test_update_notebook
   test_delete_notebook
   test_notebook_status_updates

 Integration tests (TODO Phase 2)
  - test_container_provider_integration
  - test_minio_integration
  - test_spark_cluster_lifecycle
  - test_job_submission_and_execution
```

**Run with**:
```bash
pytest tests/test_notebook_crud.py -v
pytest tests/ -v --cov=itl_analytics_provider
```

---

##  **Implementation Checklist**

### **Phase 1: Complete** 
- [ ORM models for all 6 resource types
- [ Repository pattern implemented
- [ Service orchestration layer
- [ REST API routes (ARM-style)
- [ BrainCell cell integration
- [ Container Provider client
- [ MinIO client (stub)
- [ Comprehensive documentation
- [ Unit tests for notebooks
- [ Live integration tests

### **Phase 2: Stubs Ready** 
- [ Spark cluster ORM, repo, service, routes, cell
- [ Analytics job ORM, repo, service, routes, cell
- [ Container Provider pod orchestration
- [ Auto-scaling logic for Spark
- [ Job scheduler/queue integration
- [ Job monitoring and logging
- [ Integration tests with real Container Provider

### **Phase 3: Stubs Ready** 
- [ Model registry ORM, repo, service, routes, cell
- [ Inference endpoint ORM, repo, service, routes, cell
- [ MLflow server setup and integration
- [ Kubernetes model deployment
- [ Auto-scaling for inference endpoints
- [ Model validation and serving

### **Phase 4: Framework Ready** 
- [ Cell definitions with MCP skeleton
- [ MCP tool implementations for all resources
- [ Data lineage tracking (via BrainCell)
- [ Audit logging integration
- [ Governance UI

---

##  **Next Steps**

1. **Verify Compilation**: `python -m py_compile src/itl_analytics_provider/**/*.py`
2. **Run Migrations**: `alembic upgrade head`
3. **Start Provider**: `python -m itl_analytics_provider.main`
4. **Test Endpoints**: Visit `http://localhost:9509/docs`
5. **Run Tests**: `pytest tests/ -v`
6. **Plan Phase 2**: Assign Container Provider integration work

---

##  **Documentation Map**

```
Quick Links for Different Audiences:

For Users:
   GETTING_STARTED.md
   USER_SCENARIO.md

For Developers:
   ARCHITECTURE.md (this file)
   PHASE1_INTEGRATION_STATUS.md
   STUBS_IMPLEMENTATION.md

For Product/Leadership:
   DATABRICKS_COMPARISON.md
   PHASE1_STATUS.md

For Testers:
   PHASE1_GUIDE.md
```


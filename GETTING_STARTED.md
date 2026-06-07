# Getting Started: Build & Run Your First Notebook

## **Quick Start (10 minutes)**

### **Prerequisites**

```bash
# Python 3.10+
python --version

# Docker & Docker Compose
docker --version
docker-compose --version

# Git
git clone https://github.com/ITlusions/ITL.ControlPlane.ResourceProvider.Analytics
cd ITL.ControlPlane.ResourceProvider.Analytics
```

---

## **Step 1: Start Infrastructure (2 min)**

### **Start PostgreSQL, MinIO, Redis**

```bash
docker-compose up -d
```

**Verify services are running:**
```bash
docker-compose ps

# Expected output:
# NAME                          COMMAND                  SERVICE       STATUS
# itl-analytics-postgres        "docker-entrypoint..."   postgres      Up 2 minutes
# itl-analytics-minio           "/usr/bin/docker..."     minio         Up 2 minutes
# itl-analytics-redis           "redis-server..."        redis         Up 2 minutes
```

**Check PostgreSQL:**
```bash
psql -h localhost -p 5433 -U analytics -d analytics -c "SELECT version();"
# Output: PostgreSQL 15.2 on x86_64-pc-linux-gnu...
```

**Check MinIO:**
```bash
# MinIO console at http://localhost:9001
# Default credentials: minioadmin / minioadmin
```

---

## **Step 2: Install Dependencies (3 min)**

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install provider in development mode
pip install -e ".[dev]"

# Verify installation
python -c "from itl_analytics_provider import __version__; print(__version__)"
# Output: 0.1.0
```

**What gets installed:**
```
 FastAPI + Uvicorn
 SQLAlchemy + asyncpg
 Pydantic v2
 httpx (async HTTP client)
 structlog (structured logging)
 Alembic (database migrations)
 pytest (testing)
```

---

## **Step 3: Initialize Database (2 min)**

### **Run Alembic Migration**

```bash
# Generate migration from ORM models
alembic revision --autogenerate -m "Initial schema"

# Run migration to create tables
alembic upgrade head

# Verify tables created
psql -h localhost -p 5433 -U analytics -d analytics -c "\dt"

# Expected output:
#                 List of relations
#  Schema |         Name         | Type  |    Owner
# --------+----------------------+-------+-----------
#  public | alembic_version      | table | analytics
#  public | notebooks            | table | analytics
#  public | spark_clusters       | table | analytics
#  public | analytics_jobs       | table | analytics
#  public | models               | table | analytics
#  public | datasets             | table | analytics
#  public | inference_endpoints  | table | analytics
```

---

## **Step 4: Start Analytics Provider (1 min)**

```bash
python -m itl_analytics_provider.main
```

**Expected startup output:**
```
2026-06-07 10:30:00 [INFO] Analytics Provider startup
2026-06-07 10:30:00 [INFO] Loading configuration from environment
2026-06-07 10:30:01 [INFO] Initializing storage engine...
2026-06-07 10:30:02 [INFO] Database connected: postgres://localhost:5433/analytics
2026-06-07 10:30:02 [INFO]  Storage engine initialized
2026-06-07 10:30:02 [INFO] Analytics Provider is READY
2026-06-07 10:30:02 [INFO] Uvicorn running on http://0.0.0.0:9509
2026-06-07 10:30:02 [INFO] Interactive API docs at http://localhost:9509/docs
```

**Note:** Provider runs on port **9509**

---

## **Step 5: Test API (Interactive)**

### **Option A: Use Swagger UI**

Open browser: `http://localhost:9509/docs`

You'll see:
```
 FastAPI Swagger UI 
                                               
 POST   /notebooks               Create notebook
 GET    /notebooks               List notebooks
 GET    /notebooks/{id}          Get notebook
 DELETE /notebooks/{id}          Delete notebook
                                               
 Try it out...                                 

```

Click **"Try it out"** on POST `/notebooks` endpoint:

**Request body:**
```json
{
  "name": "my-first-notebook",
  "location": "eastus",
  "properties": {
    "kernel": "python3.11",
    "computeSku": "Standard_D4s_v3",
    "memory_gb": 16,
    "cpu_cores": 4,
    "storage_gb": 100
  }
}
```

Click **"Execute"**

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my-first-notebook",
  "type": "ITL.Analytics/notebooks",
  "location": "eastus",
  "status": "Running",
  "properties": {
    "kernel": "python3.11",
    "computeSku": "Standard_D4s_v3",
    "memory_gb": 16,
    "cpu_cores": 4,
    "storage_gb": 100,
    "pod_name": "notebook-550e8400-e29b-41d4-a716-446655440000",
    "storage_bucket": "analytics-550e8400-e29b-41d4",
    "notebook_url": "https://notebooks.analytics.itl.com/550e8400-e29b-41d4-a716-446655440000"
  },
  "created_at": "2026-06-07T10:30:00Z",
  "updated_at": "2026-06-07T10:35:00Z",
  "owner_id": "default-user"
}
```

---

### **Option B: Use cURL**

```bash
# Create notebook
NOTEBOOK_ID=$(curl -X POST http://localhost:9509/subscriptions/sub-001/resourceGroups/rg-test/providers/ITL.Analytics/notebooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-notebook",
    "location": "eastus",
    "properties": {
      "kernel": "python3.11",
      "computeSku": "Standard_D4s_v3",
      "memory_gb": 16,
      "cpu_cores": 4,
      "storage_gb": 100
    }
  }' | jq -r '.id')

echo "Created notebook: $NOTEBOOK_ID"

# Wait a moment for notebook to initialize
sleep 5

# List notebooks
curl -X GET http://localhost:9509/subscriptions/sub-001/resourceGroups/rg-test/providers/ITL.Analytics/notebooks

# Get specific notebook
curl -X GET http://localhost:9509/subscriptions/sub-001/resourceGroups/rg-test/providers/ITL.Analytics/notebooks/$NOTEBOOK_ID

# Delete notebook
curl -X DELETE http://localhost:9509/subscriptions/sub-001/resourceGroups/rg-test/providers/ITL.Analytics/notebooks/$NOTEBOOK_ID
```

---

## **Step 6: Verify Everything Works**

### **Test Database Layer**

```bash
pytest tests/test_notebook_crud.py::test_create_notebook -v

# Output:
# tests/test_notebook_crud.py::test_create_notebook PASSED
```

### **Test Full CRUD**

```bash
pytest tests/test_notebook_crud.py -v

# Output:
# test_create_notebook PASSED
# test_list_notebooks PASSED
# test_get_notebook PASSED
# test_update_notebook PASSED
# test_delete_notebook PASSED
# test_notebook_status_updates PASSED
# ====== 6 passed in 0.45s ======
```

### **Check Database Records**

```bash
# Connect to PostgreSQL
psql -h localhost -p 5433 -U analytics -d analytics

# Query notebooks
SELECT id, name, status, created_at FROM notebooks;

# Output:
# id                                   | name             | status  | created_at
# 550e8400-e29b-41d4-a716-446655440000 | my-first-notebook | Running | 2026-06-07 10:30:00
```

---

## **Step 7: Monitor Execution**

### **Watch Provider Logs**

In terminal where provider is running:

```
2026-06-07 10:30:01 [INFO] create_notebook: name=my-notebook, location=eastus
2026-06-07 10:30:02 [INFO] Creating database record (status: Creating)
2026-06-07 10:30:02 [INFO] Database record created: 550e8400-e29b-41d4-a716-446655440000
2026-06-07 10:30:03 [INFO] TODO: Create pod via Container provider: notebook-550e8400-e29b-41d4...
2026-06-07 10:30:03 [INFO] TODO: Create MinIO bucket: analytics-550e8400-e29b-41d4
2026-06-07 10:30:03 [INFO] TODO: Create Kubernetes service for pod
2026-06-07 10:30:04 [INFO] Notebook created and running: my-notebook
2026-06-07 10:30:04 [INFO] list_notebooks: subscription=sub-001, resource_group=rg-test
2026-06-07 10:30:04 [INFO] Found 1 notebooks in resource group
2026-06-07 10:30:05 [INFO] get_notebook: notebook_id=550e8400-e29b-41d4-a716-446655440000
2026-06-07 10:30:06 [INFO] delete_notebook: notebook_id=550e8400-e29b-41d4-a716-446655440000
2026-06-07 10:30:06 [INFO] Notebook deleted: 550e8400-e29b-41d4-a716-446655440000
```

### **Check Provider Health**

```bash
curl http://localhost:9509/health

# Output:
# {"status": "healthy", "timestamp": "2026-06-07T10:30:00Z"}
```

---

## **Example Notebook Workflows**

### **Workflow 1: Data Analysis**

```python
# Cell 1: Setup
import pandas as pd
import numpy as np

df = pd.read_csv("data/transactions.csv")
print(f"Loaded {len(df)} records")

# Cell 2: Explore
print(df.head())
print(df.describe())

# Cell 3: Visualize
import matplotlib.pyplot as plt
df['amount'].hist(bins=50)
plt.savefig("/mnt/s3/analysis.png")

# Cell 4: Save results
df.to_parquet("/mnt/s3/processed_data.parquet")
```

### **Workflow 2: Model Training**

```python
# Cell 1: Setup
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Load data
X = pd.read_csv("features.csv")
y = pd.read_csv("targets.csv")

# Cell 2: Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Cell 3: Evaluate
score = model.score(X_test, y_test)
print(f"Accuracy: {score:.4f}")

# Cell 4: Save
with open("/mnt/s3/model.pkl", "wb") as f:
    pickle.dump(model, f)
```

### **Workflow 3: Spark Analytics**

```python
# Cell 1: Setup Spark
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("analytics").getOrCreate()

# Load data
df = spark.read.parquet("s3://data-lake/events/*.parquet")

# Cell 2: Analytics
result = df.groupBy("user_id").count().orderBy("count", ascending=False)
result.show()

# Cell 3: Export results
result.write.mode("overwrite").parquet("s3://output/user-counts")
```

---

## **Troubleshooting**

### **Problem: "Connection refused" on provider startup**

**Cause:** PostgreSQL not running

**Fix:**
```bash
docker-compose up -d postgres
docker-compose logs postgres
```

### **Problem: Notebook creation returns 500 error**

**Cause:** Database migration not run

**Fix:**
```bash
alembic upgrade head
# Then try again
```

### **Problem: "Pod timeout" in logs**

**Cause:** Container Provider (port 9508) not running

**Fix:**
```bash
# For now, Container/MinIO integration logs TODOs
# These will be implemented in full version
# The provider is ready for integration
```

### **Problem: Tests failing**

**Cause:** Dependencies not installed

**Fix:**
```bash
pip install -e ".[dev]"
pytest tests/test_notebook_crud.py -v
```

---

## **Next Steps**

### **Option 1: Extend Phase 1**

```bash
# Add more test cases
pytest tests/ -v --cov=itl_analytics_provider

# Check code quality
pylint src/itl_analytics_provider/

# Format code
black src/
```

### **Option 2: Implement Phase 2**

```bash
# Create Spark cluster support
# See PHASE2_PLAN.md for details
```

### **Option 3: Deploy**

```bash
# Build container image
docker build -t itl-analytics-provider:latest .

# Push to ACR
docker push myregistry.azurecr.io/itl-analytics-provider:latest

# Deploy to Kubernetes (in production)
kubectl apply -f kubernetes/deployment.yaml
```

---

##  **Documentation References**

- **[USER_SCENARIO.md](USER_SCENARIO.md)** - User workflow example
- **[PHASE1_STATUS.md](PHASE1_STATUS.md)** - Implementation details
- **[PHASE1_INTEGRATION_STATUS.md](PHASE1_INTEGRATION_STATUS.md)** - Container integration
- **[PHASE1_GUIDE.md](PHASE1_GUIDE.md)** - Technical setup guide
- **[README.md](README.md)** - Project overview

---

## **Summary**

**You now have:**
- [DONE] PostgreSQL with schema
- [DONE] Analytics Provider running
- [DONE] Full CRUD API for notebooks
- [DONE] Tested database layer
- [DONE] Documented workflows

**Time invested:** ~10 minutes  
**Ready to:** Create, list, and manage notebooks via REST API

**Next phase:** Connect Container Provider + MinIO for pod orchestration

---

## **Quick Commands Reference**

```bash
# Start services
docker-compose up -d

# Install
pip install -e ".[dev]"

# Migrate database
alembic upgrade head

# Run provider
python -m itl_analytics_provider.main

# Test
pytest tests/ -v

# Create notebook
curl -X POST http://localhost:9509/subscriptions/sub-001/resourceGroups/rg-test/providers/ITL.Analytics/notebooks \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "location": "eastus", "properties": {}}'

# Browse API
# http://localhost:9509/docs

# Stop services
docker-compose down
```


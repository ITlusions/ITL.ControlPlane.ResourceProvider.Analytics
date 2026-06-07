# Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.12+
- kubectl (for Kubernetes deployment)
- Git

## Installation

### 1. Clone and Setup

```bash
git clone https://github.com/ITlusions/ITL.ControlPlane.ResourceProvider.Analytics.git
cd ITL.ControlPlane.ResourceProvider.Analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Start Infrastructure

```bash
# Start PostgreSQL, MinIO, Redis with Docker Compose
docker compose up -d

# Verify services are running
docker compose ps

# Expected output:
# NAME                  STATUS
# analytics-postgres    Up (healthy)
# analytics-minio       Up (healthy)
# analytics-redis       Up (healthy)
```

### 3. Run Provider Locally

```bash
# Run the Analytics Provider
python -m itl_analytics_provider.main

# Expected output:
# ================================================================================
# Analytics Provider Configuration
# ================================================================================
# Mode: API
# Host: 0.0.0.0:9509
# Provider: ITL.Analytics v2024-06-01
# Resource Types: notebooks, sparkClusters, analyticsJobs, models, datasets, inferenceEndpoints
# ================================================================================
# 
# INFO:     Started server process [12345]
# INFO:     Waiting for application startup.
# ================================================================================
# Analytics Provider Startup
# ================================================================================
#  Storage engine initialized
#  Database schema ready
#  Provider registered
# ================================================================================
# Analytics Provider is READY
# ================================================================================
```

## API Usage

### Health Check

```bash
curl http://localhost:9509/health
# Response: {"status": "healthy"}
```

### API Documentation

Visit interactive Swagger UI:
```
http://localhost:9509/docs
```

### Create Notebook

```bash
curl -X POST http://localhost:9509/api/v1/subscriptions/sub-123/resourceGroups/rg-dev/providers/ITL.Analytics/notebooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-notebook",
    "location": "westeurope",
    "properties": {
      "kernel": "python3.11",
      "computeSku": "Standard_D4s_v3"
    }
  }'

# Response:
# {
#   "id": "/subscriptions/sub-123/resourceGroups/rg-dev/providers/ITL.Analytics/notebooks/my-notebook",
#   "name": "my-notebook",
#   "type": "ITL.Analytics/notebooks",
#   "location": "westeurope",
#   "status": "Running",
#   "url": "https://notebooks.analytics.itl.com/my-notebook",
#   "created_at": "2024-06-07T14:00:00Z"
# }
```

### List Notebooks

```bash
curl http://localhost:9509/api/v1/subscriptions/sub-123/resourceGroups/rg-dev/providers/ITL.Analytics/notebooks

# Response:
# {
#   "value": [
#     {"id": "...", "name": "my-notebook", "status": "Running"},
#     ...
#   ]
# }
```

### Create Spark Cluster

```bash
curl -X POST http://localhost:9509/api/v1/subscriptions/sub-123/resourceGroups/rg-dev/providers/ITL.Analytics/sparkClusters \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ml-training",
    "location": "westeurope",
    "properties": {
      "driver": {"cpu": 8, "memory": "32Gi"},
      "workers": {
        "count": 3,
        "cpu_per_worker": 16,
        "memory_per_worker": "64Gi",
        "gpu_per_worker": 4,
        "gpu_type": "H100"
      }
    }
  }'

# Response (202 Accepted - async):
# {
#   "id": "/subscriptions/sub-123/resourceGroups/rg-dev/providers/ITL.Analytics/sparkClusters/ml-training",
#   "name": "ml-training",
#   "status": "Creating",
#   "master_url": "spark://ml-training-driver:7077"
# }
```

### Register Model

```bash
curl -X POST http://localhost:9509/api/v1/subscriptions/sub-123/resourceGroups/rg-dev/providers/ITL.Analytics/models \
  -H "Content-Type: application/json" \
  -d '{
    "name": "customer-churn-classifier",
    "location": "westeurope",
    "properties": {
      "version": "1.0.0",
      "framework": "sklearn",
      "metrics": {
        "accuracy": 0.87,
        "precision": 0.85,
        "recall": 0.89
      },
      "artifacts": {
        "model_path": "s3://analytics/models/customer-churn/v1.0.0/model.pkl"
      }
    }
  }'

# Response:
# {
#   "id": "/subscriptions/sub-123/resourceGroups/rg-dev/providers/ITL.Analytics/models/customer-churn-classifier",
#   "name": "customer-churn-classifier",
#   "version": "1.0.0",
#   "status": "Registered"
# }
```

## Development

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=itl_analytics_provider --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/

# Type checking
mypy src/
```

### Project Structure

```
src/itl_analytics_provider/
 __init__.py              Package init
 analytics.py             Main provider class
 config.py                Configuration
 main.py                  Entry point

 initialization/          Server setup
   server.py             AnalyticsProviderServer
   app_factory.py        FastAPI app creation
   lifecycle.py          Startup/shutdown

 routes/                  Route handlers
   notebooks.py          Notebook routes (all resource types)
   __init__.py           Route exports

 models/                  Pydantic models
   notebook.py           Request/response models
   __init__.py           Model exports

 services/                Business logic
   notebook_service.py   Service implementations
   __init__.py           Service exports

 repositories/            Data access
    notebook_repo.py      Repository implementations
    __init__.py           Repository exports
```

## Deployment

### Docker

```bash
# Build image
docker build -t analytics-provider:0.1.0 .

# Run container
docker run -p 9509:9509 \
  -e DATABASE_URL="postgresql+asyncpg://analytics:pass@postgres/analytics_db" \
  -e MINIO_ENDPOINT="minio:9000" \
  analytics-provider:0.1.0
```

### Kubernetes

```bash
# Create namespace
kubectl create namespace analytics

# Deploy
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -n analytics
kubectl logs -n analytics -f deployment/analytics-provider
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 9509
lsof -i :9509

# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Verify PostgreSQL is running
docker compose ps postgres

# Check logs
docker compose logs postgres

# Restart database
docker compose restart postgres
```

### MinIO Access Issues

```bash
# MinIO console
http://localhost:9001
# Login: minioadmin / minioadmin

# Create bucket if needed
aws s3 mb s3://analytics --endpoint-url http://localhost:9000 \
  --access-key minioadmin --secret-key minioadmin
```

## Next Steps

1. **Implement notebook routes** - Pod creation, JupyterLab setup
2. **Integrate with Accelerator provider** - GPU allocation
3. **Add MLflow support** - Model registry
4. **Write tests** - Unit and integration tests
5. **Deploy to Kubernetes** - Production setup

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/ITlusions/ITL.ControlPlane.ResourceProvider.Analytics/issues
- Documentation: See `docs/` directory

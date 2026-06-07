# ITL Analytics Resource Provider

The Analytics Resource Provider manages data science and machine learning infrastructure on the ITL Control Plane.

**Namespace**: `ITL.Analytics`  
**Version**: `2024-06-01`  
**Python**: `>=3.12`

## Features

- **Notebooks**: Interactive Jupyter-based data science environments
- **Spark Clusters**: Distributed compute with GPU acceleration
- **Analytics Jobs**: Scheduled ETL, training, and data processing workloads
- **Models**: ML model registry with versioning and lineage
- **Datasets**: Data catalog with schema and quality metadata
- **Inference Endpoints**: REST API serving for trained models

## Resource Types

```
- notebooks              (Jupyter notebook sessions)
- sparkClusters         (Distributed Spark compute)
- analyticsJobs         (Scheduled workflows)
- models                (ML model registry)
- datasets              (Data catalog entries)
- inferenceEndpoints    (Model serving APIs)
```

## Quick Start

### Install

```bash
pip install -e ".[dev]"
```

### Run Locally

```bash
# Start infrastructure
docker compose up -d

# Run provider
python -m itl_analytics_provider.main
```

### Deploy to Kubernetes

```bash
docker build -t analytics-provider:0.1.0 .
docker tag analytics-provider:0.1.0 itl-registry/analytics-provider:0.1.0
docker push itl-registry/analytics-provider:0.1.0

kubectl apply -f k8s/deployment.yaml
```

## API Examples

### Create Notebook

```bash
curl -X POST http://localhost:9509/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Analytics/notebooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-notebook",
    "location": "westeurope",
    "properties": {
      "kernel": "python3.11",
      "computeSku": "Standard_D4s_v3"
    }
  }'
```

### Create Spark Cluster

```bash
curl -X POST http://localhost:9509/subscriptions/{sub}/resourceGroups/{rg}/providers/ITL.Analytics/sparkClusters \
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
        "gpu_per_worker": 4
      }
    }
  }'
```

## Architecture

### Integration Points

- **Control Plane**: Authentication, RBAC, multi-tenancy
- **Container Provider**: Pod/container orchestration
- **Accelerator Provider**: GPU allocation and tracking
- **Storage Provider**: Data lake and artifact storage
- **Identity Provider**: Service accounts for jobs
- **BrainCell**: Metadata, lineage, and governance

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## Development

### Run Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=itl_analytics_provider
```

### Lint & Format

```bash
black src/
ruff check src/
mypy src/
```

## Status

 **Alpha** - MVP implementation in progress

| Component | Status |
|-----------|--------|
| Notebooks |  In Development |
| Spark Clusters |  Planned |
| Jobs |  Planned |
| Models |  Planned |
| Datasets |  Planned |
| Inference |  Planned |

## License

MIT

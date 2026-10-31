# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ ./src/

# docker build --secret id=forgejo_token,env=FORGEJO_PACKAGE_TOKEN .
RUN --mount=type=secret,id=forgejo_token \
    pip install --no-cache-dir \
      --index-url "https://itladmin:$(cat /run/secrets/forgejo_token)@git.itlusions.com/api/packages/ITlusions/pypi/simple/" \
      --extra-index-url https://pypi.org/simple/ \
      -e .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9509/health')"

# Run provider
EXPOSE 9509
CMD ["python", "-m", "itl_analytics_provider.main"]

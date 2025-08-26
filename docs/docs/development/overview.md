# Overview

The Dev Coach project uses Docker Compose to provide isolated, reproducible development environments. This setup ensures consistent behavior across different machines and simplifies the development workflow.

## Development Environments

The project supports two main development environments:

### Local Environment
- **Purpose**: Full local development with isolated database
- **Database**: Local PostgreSQL container
- **Use Case**: Primary development environment
- **Command**: `COMPOSE_PROJECT_NAME=dev-coach-local docker compose --profile local -f docker/docker-compose.yml -f docker/docker-compose.local.yml up --build -d`

### Dev Environment
- **Purpose**: Local code with remote staging database
- **Database**: Remote Render PostgreSQL
- **Use Case**: Integration testing with production-like data
- **Command**: `COMPOSE_PROJECT_NAME=dev-coach-dev docker compose --profile dev -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up --build -d`

**Key Difference**: The only difference between these environments is the database - local uses a containerized PostgreSQL, while dev connects to the remote Render database.

## Technology Stack

| Component | Technology | Port | Description |
|-----------|------------|------|-------------|
| **Frontend** | Vite + React + TypeScript | 5173 | Modern React application with hot reload |
| **Backend** | Django Rest Framework | 8000 | Python API with auto-reload |
| **Database** | PostgreSQL 17.1 | 5432 | Local database with persistent storage |
| **Cache/Queue** | Redis | 6379 | Celery task queue and caching |
| **Documentation** | Docusaurus | 5174 | This documentation site |

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Git](https://git-scm.com/) for version control

### Start Local Environment
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose --profile local \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.local.yml up --build -d
```

### Start Dev Environment
```bash
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose --profile dev \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.dev.yml up --build -d
```

### Access Your Services
- **Frontend**: [http://localhost:5173/](http://localhost:5173/)
- **Backend**: [http://localhost:8000/admin](http://localhost:8000/admin)
- **Documentation**: [http://localhost:5174/](http://localhost:5174/)

## Key Features

- **Live Development**: Hot reload for frontend, auto-reload for backend
- **Volume Mounting**: Code changes immediately reflected without rebuilding
- **Health Checks**: Database ready before dependent services start
- **Profile-based**: Different services run based on environment profile

## Next Steps

- [Docker Configuration](./docker-configuration.md) - Docker setup explanation
- [Common Commands](./common-commands.md) - Essential development commands

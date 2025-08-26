# Docker Configuration

This document explains how the Docker setup is configured for the Dev Coach project.

## Architecture Overview

The project uses a multi-file Docker Compose configuration with profiles to support different environments:

```
docker/
├── docker-compose.yml          # Base configuration (all services)
├── docker-compose.local.yml    # Local environment overrides
└── docker-compose.dev.yml      # Dev environment overrides
```

## Services

### Base Configuration (`docker-compose.yml`)

| Service      | Image/Build     | Port | Profile        | Description                            |
| ------------ | --------------- | ---- | -------------- | -------------------------------------- |
| **db**       | `postgres:17.1` | 5432 | `local`        | PostgreSQL database with health checks |
| **backend**  | `../server`     | 8000 | `local`, `dev` | Django development server              |
| **frontend** | `../client`     | 5173 | -              | Vite/React development server          |
| **docs**     | `../docs`       | 5174 | -              | Docusaurus documentation               |
| **redis**    | `redis:7`       | 6379 | `local`, `dev` | Cache and Celery task queue            |
| **celery**   | `../server`     | -    | `local`, `dev` | Background task worker                 |

### Environment Overrides

#### Local Environment (`docker-compose.local.yml`)

- Uses local PostgreSQL database
- Backend waits for database health check
- Frontend configured for local API endpoint

#### Dev Environment (`docker-compose.dev.yml`)

- No local database (uses remote Render PostgreSQL)
- Development settings for remote database connection

## Volume Management

### Named Volumes

- **`db-data`**: PostgreSQL data persistence
- **`/client/node_modules`**: Frontend dependency cache
- **`/docs/node_modules`**: Documentation dependency cache

### Bind Mounts

- **`../server:/server`**: Backend code for live reloading
- **`../client:/client`**: Frontend code for live reloading
- **`../docs:/docs`**: Documentation code for live reloading

## Environment Variables

### Backend

- Local: `DJANGO_SETTINGS_MODULE=settings.local`
- Dev: `DJANGO_SETTINGS_MODULE=settings.development`

### Frontend

- Local: `VITE_ENV=LOCAL`
- Dev: `VITE_ENV=DEVELOPMENT`

Backend environment configuration is centralized in a single `.env` file located in `server/.env`. All Django settings modules (local, development, etc.) load from this same file via `server/load_env.py`, and environment selection is handled by `DJANGO_SETTINGS_MODULE`.

Need access to the `.env` file? Email `caseywschmid@gmail.com` and it will be shared securely via Proton Pass.

## Key Features

- **Health Checks**: Database waits for readiness before starting dependent services
- **Live Reloading**: Volume mounts enable code changes without rebuilding
- **Profile-based**: Different services run based on environment profile
- **Dependency Management**: Services start in correct order with health checks

## Next Steps

- [Common Commands](./common-commands.md) - Essential development commands

# Dev Coach – Local & Dev Docker Environments

This project uses Docker Compose to run both the backend (Django) and frontend (Vite/React) in isolated environments for local development and dev/staging integration.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Git](https://git-scm.com/) installed

---

## Environments Overview

| Environment | Database       | Frontend | Backend | Celery | Redis  | Usage                                  |
| ----------- | -------------- | -------- | ------- | ------ | ------ | -------------------------------------- |
| local       | Local Postgres | Local    | Local   | Local  | Local  | Full local stack for development       |
| dev         | Hosted         | Local    | Local   | Local  | Local  | Local code, but DB is remote (staging) |
| staging     | Hosted         | Hosted   | Hosted  | Hosted | Hosted | (To be defined, typically for QA)      |
| prod        | Hosted         | Hosted   | Hosted  | Hosted | Hosted | (To be defined, for production)        |

---

## Quick Start

### 1. **Clone the repository:**

```sh
git clone <your-repo-url>
cd dev-coach
```

### 2. **Start the Local Environment**

This runs everything (frontend, backend, celery, redis, and Postgres) locally.

```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose --profile local \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.local.yml up --build
```

- **Frontend (Vite/React):** [http://localhost:5173/](http://localhost:5173/)
- **Backend (Django):** [http://localhost:8000/admin](http://localhost:8000/admin)
- **Database:** Local Postgres (see docker-compose.yml for credentials)

### 3. **Start the Dev Environment**

This runs frontend, backend, celery, and redis locally, but connects to the remote (staging) database.

```sh
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose --profile dev \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.dev.yml up --build
```

- **Frontend (Vite/React):** [http://localhost:5173/](http://localhost:5173/)
- **Backend (Django):** [http://localhost:8000/admin](http://localhost:8000/admin)
- **Database:** Remote (staging) Postgres

---

## Project Structure

- `server/` – Django backend
- `client/` – Vite/React frontend
- `docker-compose.yml` – Base Compose file (services, volumes)
- `docker-compose.local.yml` – Local overrides (local DB, etc.)
- `docker-compose.dev.yml` – Dev overrides (remote DB, etc.)
- `server/Dockerfile.local` – Backend Docker build for local/dev
- `client/Dockerfile.local` – Frontend Docker build for local/dev

---

## Troubleshooting

- **Frontend 404 or not available:**
  - Ensure `client/index.html` exists and is not excluded by `.dockerignore`.
  - Check frontend logs: `docker compose logs frontend`
- **Backend static files warning:**
  - You may see a warning about `/server/apps/static` not existing. This is safe to ignore unless you need custom static files.
- **Database connection issues:**
  - For local: ensure the `db` service is healthy and ports are not in use.
  - For dev: ensure you have network access to the remote DB.

---

## Stopping the Environment

To stop the containers, press `Ctrl+C` in the terminal where Docker Compose is running. To remove containers and networks:

```sh
docker compose down
```

---

## Customization

- You can mount your local code into the containers for live reload (already set up in `docker-compose.yml`).
- To run backend or frontend commands, use `docker compose exec`:
  - Backend: `docker compose exec backend bash`
  - Frontend: `docker compose exec frontend bash`

---

For more details, see the `docker-compose.yml` and Dockerfiles in each service directory.

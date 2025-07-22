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

---

## Managing Migrations and Container Lifecycle

### Starting the Environment

To start all services (frontend, backend, celery, redis, and Postgres) for local development:

```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose --profile local \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.local.yml up --build
```

- Add `-d` to run in detached mode (in the background):
  ```sh
  COMPOSE_PROJECT_NAME=dev-coach-local \
    docker compose --profile local \
    -f docker/docker-compose.yml \
    -f docker/docker-compose.local.yml up --build -d --force-recreate
  ```

### Forcing Dependency Reinstalls and Rebuilds (Frontend/Backend)

**If you add new packages or dependencies to the frontend or backend, Docker may use cached layers and not install them unless you force a rebuild.**

- To ensure all new dependencies are installed and recognized, use the following flags:

```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose --profile local \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.local.yml up --build --force-recreate --no-deps
```

- **Flags explained:**
  - `--build`: Always build images before starting containers.
  - `--force-recreate`: Recreate containers even if their configuration and image haven't changed.
  - `--no-deps`: Don't start linked services (dependencies). Use this if you only want to rebuild a specific service (e.g., frontend or backend) without restarting the database or redis.
  - `--no-cache`: (use with `docker compose build`) Forces Docker to not use any cache when building images. Use this if you suspect the build cache is stale:
    ```sh
    COMPOSE_PROJECT_NAME=dev-coach-local \
      docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml build --no-cache frontend
    ```
    Then bring up the environment as usual.

#### Common Troubleshooting

- **New packages not recognized in containers?**
  - Make sure you:
    1. Add the package to the correct `package.json` or `requirements.txt`.
    2. Run with `--build --force-recreate` to ensure Docker rebuilds the image and reinstalls dependencies.
    3. If still not working, try `docker compose build --no-cache` for the affected service.
- **Frontend/Backend code changes not reflected?**
  - If you only changed code (not dependencies), a simple `docker compose up --build` is usually enough.
  - For dependency changes, always use `--build --force-recreate`.
- **Want to rebuild only the frontend or backend?**
  - You can specify the service name at the end:
    ```sh
    COMPOSE_PROJECT_NAME=dev-coach-local \
      docker compose --profile local \
      -f docker/docker-compose.yml \
      -f docker/docker-compose.local.yml up --build --force-recreate frontend
    ```

### Stopping the Environment

To stop and remove all containers and networks:

```sh
docker compose down
```

---

### Making and Applying Django Migrations (While Containers Are Running)

You can make and apply migrations directly inside the running backend container. Your code and migration files will be updated on your host machine thanks to the volume mount.

#### **Using Docker Compose Exec**

Make migrations:
```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml exec backend python manage.py makemigrations
```

Apply migrations:
```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml exec backend python manage.py migrate
```

---

### Running Tests Inside the Backend Docker Container

Ensure the local environment is running according to the directions above.

To run your Django/pytest tests in the same environment as your backend (recommended for this project):

- **In a new terminal, run your tests inside the backend container:**
  ```sh
  COMPOSE_PROJECT_NAME=dev-coach-local docker compose --profile local -f docker/docker-compose.yml -f docker/docker-compose.local.yml exec backend pytest apps/test_scenario/tests/
  ```
  - This will run all tests in the `server/apps/test_scenario/tests/` directory.
  - To run all tests in the project, omit the path:
    ```sh
    COMPOSE_PROJECT_NAME=dev-coach-local docker compose --profile local -f docker/docker-compose.yml -f docker/docker-compose.local.yml exec backend pytest
    ```

**Tip:**
- This approach ensures your tests use the same environment, database, and dependencies as your running backend service.
- You can use this pattern for any Django management or test command.

---

## Managing Migrations and Container Lifecycle

### Starting the Environment

To start all services (frontend, backend, celery, redis, and Postgres) for local development:

```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose --profile local \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.local.yml up --build
```

- Add `-d` to run in detached mode (in the background):
  ```sh
  COMPOSE_PROJECT_NAME=dev-coach-local \
    docker compose --profile local \
    -f docker/docker-compose.yml \
    -f docker/docker-compose.local.yml up --build -d --force-recreate
  ```

### Stopping the Environment

To stop and remove all containers and networks:

```sh
docker compose down
```

---

### Making and Applying Django Migrations (While Containers Are Running)

You can make and apply migrations directly inside the running backend container. Your code and migration files will be updated on your host machine thanks to the volume mount.

#### **Using Docker Compose Exec**

Make migrations:
```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml exec backend python manage.py makemigrations
```

Apply migrations:
```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml exec backend python manage.py migrate
```

Create a super user:
```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
docker compose \
-f docker/docker-compose.yml \
-f docker/docker-compose.local.yml \
exec backend python manage.py createsuperuser \
--noinput --email superadmin@admin.com
```

```sh
COMPOSE_PROJECT_NAME=dev-coach-local \
docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml exec backend \
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u=User.objects.get(email='superadmin@admin.com'); u.set_password('Coach123!'); u.save()"
```

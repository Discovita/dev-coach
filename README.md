# Dev Coach – Local Development Environment

This project uses Docker Compose to run both the backend (Django) and frontend (Vite/React) in a local development environment.

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Git](https://git-scm.com/) installed

## Quick Start

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd dev-coach
   ```

2. **Start the environment:**
   ```sh
   docker-compose up --build
   ```
   This will build and start both the backend and frontend containers.

3. **Access the apps:**
   - **Backend (Django):** [http://localhost:8000/admin](http://localhost:8000/admin)
   - **Frontend (Vite/React):** [http://localhost:5173/](http://localhost:5173/)

## Project Structure
- `server/` – Django backend
- `client/` – Vite/React frontend
- `docker-compose.yml` – Orchestrates both services
- `server/Dockerfile.local` – Backend Docker build
- `client/Dockerfile.local` – Frontend Docker build

## Troubleshooting
- **Frontend fails with `Missing script: "local"`:**
  - The Docker Compose file tries to run `npm run local` for the frontend. If you see this error, either:
    - Change the `command` in `docker-compose.yml` for the frontend service to `npm run dev`, or
    - Add a `local` script to your `client/package.json`:
      ```json
      "scripts": {
        "local": "vite"
      }
      ```
- **Backend static files warning:**
  - You may see a warning about `/server/apps/static` not existing. This is safe to ignore unless you need custom static files.

## Stopping the Environment
To stop the containers, press `Ctrl+C` in the terminal where Docker Compose is running. To remove containers and networks:
```sh
docker-compose down
```

## Customization
- You can mount your local code into the containers for live reload (already set up in `docker-compose.yml`).
- To run backend or frontend commands, use `docker-compose exec`:
  - Backend: `docker-compose exec backend bash`
  - Frontend: `docker-compose exec frontend bash`

---

For more details, see the `docker-compose.yml` and Dockerfiles in each service directory. 
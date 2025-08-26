# Common Commands

This document provides a quick reference for all essential development commands used in the Dev Coach project.

## Development Workflow

### Docker Desktop Workflow

I typically manage the development environment using Docker Desktop:

1. **Initial Build**: Run the build command with `-d` flag to start in detached mode (no terminal logs)
2. **Monitor Logs**: Use Docker Desktop interface to monitor container logs
3. **Restart Services**: Use Docker Desktop "play" button to restart containers after code changes
4. **Container Management**: Use Docker Desktop for stopping, starting, and managing containers

### Starting Environments

**Note**: Commands are the same across environments - only the project name changes:

#### Local Environment
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose --profile local \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.local.yml up --build -d
```

#### Dev Environment
```bash
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose --profile dev \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.dev.yml up --build -d
```

#### Detached Mode (Background)
The `-d` flag runs containers in background mode, allowing you to monitor logs through Docker Desktop instead of terminal output.

#### Force Rebuild
For dependency changes or cache issues:
```bash
# Local environment
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose --profile local \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.local.yml up --build --force-recreate

# Dev environment
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose --profile dev \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.dev.yml up --build --force-recreate
```

### Stopping Environments

#### Graceful Shutdown
Press `Ctrl+C` in the terminal where Docker Compose is running.

#### Complete Cleanup
```bash
# Local environment
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml down

# Dev environment
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml down

# Remove volumes (WARNING: deletes database data)
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml down -v
```

## Backend Commands (Django)

### Database Management

#### Make Migrations
```bash
# Local environment
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend python manage.py makemigrations

# Dev environment
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
  exec backend python manage.py makemigrations
```

#### Apply Migrations
```bash
# Local environment
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend python manage.py migrate

# Dev environment
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
  exec backend python manage.py migrate
```

#### Database Shell
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend python manage.py dbshell
```

### User Management

#### Create Superuser
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend python manage.py createsuperuser --noinput --email superadmin@admin.com
```

#### Set Superuser Password
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend python manage.py shell -c \
  "from django.contrib.auth import get_user_model; User = get_user_model(); u=User.objects.get(email='superadmin@admin.com'); u.set_password('Coach123!'); u.save()"
```

### Development Commands

#### Django Shell
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend python manage.py shell
```

#### Collect Static Files
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend python manage.py collectstatic --noinput
```

#### Check Django Configuration
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend python manage.py check
```

### Testing

#### Run All Tests
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend pytest
```

#### Run Specific Test File
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend pytest apps/test_scenario/tests/
```

#### Run Tests with Coverage
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec backend pytest --cov=apps
```

## Frontend Commands (React/Vite)

### Package Management

#### Install Dependencies
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec frontend npm install
```

#### Install Specific Package
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec frontend npm install <package-name>
```

#### Update Dependencies
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec frontend npm update
```

### Development Commands

#### Start Development Server
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec frontend npm run dev
```

#### Build for Production
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec frontend npm run build
```

#### Run Tests
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec frontend npm test
```

#### Lint Code
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec frontend npm run lint
```

## Database Commands

### Backup and Restore

#### Create Backup (Local)
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec db pg_dump -U dev_coach_database_user -d local_dev_coach -Fc > \
  server/backups/dev_coach_local_backup_$(date +%Y%m%d_%H%M%S).dump
```

#### Restore from Backup (Local)
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec -T db pg_restore -U postgres -d dev_coach_core_local < \
  server/backups/your_backup_file.dump
```

### Database Maintenance

#### Connect to Database
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec db psql -U dev_coach_database_user -d local_dev_coach
```

#### List Databases
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec db psql -U dev_coach_database_user -l
```

## Docker Commands

### Container Management

#### View Running Containers
```bash
docker ps
```

#### View All Containers
```bash
docker ps -a
```

#### View Container Logs
```bash
# All services
docker compose logs

# Specific service
docker compose logs backend
docker compose logs frontend
docker compose logs db

# Follow logs
docker compose logs -f backend
```

#### Restart Service
```bash
# Local environment
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  restart backend

# Dev environment
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
  restart backend
```

### Image Management

#### Build Specific Service
```bash
# Local environment
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  build backend

# Dev environment
COMPOSE_PROJECT_NAME=dev-coach-dev \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml \
  build frontend
```

#### Build Without Cache
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  build --no-cache backend
```

#### Clean Up Docker
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a
```

## Documentation Commands

### Start Documentation Server
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec docs npm start
```

### Build Documentation
```bash
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml \
  exec docs npm run build
```

## Quick Reference

### Environment Variables
```bash
# Local environment
COMPOSE_PROJECT_NAME=dev-coach-local
COMPOSE_FILE=docker/docker-compose.yml:docker/docker-compose.local.yml

# Dev environment
COMPOSE_PROJECT_NAME=dev-coach-dev
COMPOSE_FILE=docker/docker-compose.yml:docker/docker-compose.dev.yml
```

### Common Patterns

#### Execute Command in Container
```bash
# Backend
docker compose exec backend <command>

# Frontend
docker compose exec frontend <command>

# Database
docker compose exec db <command>
```

#### View Service Status
```bash
# Check if services are running
docker compose ps

# Check service health
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

## Troubleshooting

### Adding NPM Packages

**Important**: When you add a new npm package while Docker containers are running, you need to do a COMPLETE rebuild. Docker's cache system doesn't properly handle npm package changes.

**Solution**: Use the fresh-start script or manually clean up:

```bash
# Option 1: Use the fresh-start script
./scripts/fresh-start.sh

# Option 2: Manual cleanup (preserves database)
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml down --remove-orphans

# Remove project images and volumes (but NOT db-data)
docker images | grep dev-coach-local | awk '{print $3}' | xargs -r docker rmi
docker volume ls | grep dev-coach-local | grep -v db-data | awk '{print $2}' | xargs -r docker volume rm

# Rebuild
COMPOSE_PROJECT_NAME=dev-coach-local \
  docker compose --profile local \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.local.yml up --build -d
```

### Common Issues

#### Check Service Health
```bash
# Check all services
docker compose ps

# Check specific service logs
docker compose logs backend --tail=50
```

#### Reset Environment
```bash
# Stop and remove everything
docker compose down -v

# Remove all images
docker system prune -a

# Rebuild from scratch
docker compose up --build --force-recreate
```

#### Debug Container
```bash
# Access container shell
docker compose exec backend bash
docker compose exec frontend sh
docker compose exec db psql -U dev_coach_database_user -d local_dev_coach
```

## Next Steps

- [Docker Configuration](./docker-configuration.md) - Understanding the Docker setup

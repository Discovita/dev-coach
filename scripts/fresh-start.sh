#!/bin/bash

# Fresh Start Script for Dev Coach
# This script does a complete fresh rebuild of the development environment

echo "🧹 Starting fresh rebuild..."

# Stop and remove everything for this project
echo "📦 Stopping containers and removing volumes..."
COMPOSE_PROJECT_NAME=dev-coach-local docker compose --profile local -f docker/docker-compose.yml -f docker/docker-compose.local.yml down --volumes --remove-orphans

# Remove project-specific images
echo "🗑️  Removing project images..."
docker images | grep dev-coach-local | awk '{print $3}' | xargs -r docker rmi

# Remove project-specific volumes
echo "🗑️  Removing project volumes..."
docker volume ls | grep dev-coach-local | awk '{print $2}' | xargs -r docker volume rm

# Fresh rebuild with no cache
echo "🔨 Building fresh containers..."
COMPOSE_PROJECT_NAME=dev-coach-local docker compose --profile local -f docker/docker-compose.yml -f docker/docker-compose.local.yml build --no-cache
COMPOSE_PROJECT_NAME=dev-coach-local docker compose --profile local -f docker/docker-compose.yml -f docker/docker-compose.local.yml up -d

echo "Fresh rebuild complete!"
echo "Frontend: http://localhost:5173"
echo "Backend: http://localhost:8000" 
#!/bin/bash

# Usage: ./backup_local_db.sh [output_file]
# Example: ./backup_local_db.sh my_local_backup.sql

# Local database credentials from .env
LOCAL_DB_HOST="localhost"
LOCAL_DB_NAME="local_dev_coach"
LOCAL_DB_USER="dev_coach_database_user"
LOCAL_DB_PASSWORD="UxRZ75YUsR2wFL6B3JnUDWN8XDyriY3v"
LOCAL_DB_PORT="5432"

# Check if the Docker container is running
echo "Checking if dev-coach-local database container is running..."
if ! docker ps --format "table {{.Names}}" | grep -q "dev-coach-local-db-1"; then
    echo "Error: dev-coach-local-db-1 container is not running"
    echo "Please start the container with: COMPOSE_PROJECT_NAME=dev-coach-local docker compose --profile local -f docker/docker-compose.yml -f docker/docker-compose.local.yml up -d"
    exit 1
fi

# Check if the db service is healthy
echo "Checking if database service is healthy..."
if ! docker exec dev-coach-local-db-1 pg_isready -h localhost -U "$LOCAL_DB_USER" > /dev/null 2>&1; then
    echo "Error: Database service is not ready"
    echo "Please wait for the database to fully start up"
    exit 1
fi

echo "Database container is running and ready"

# Create backups directory if it doesn't exist
mkdir -p backups/local

# Output file
OUTPUT_FILE=${1:-"backups/local/dev_coach_local_database_backup_$(date +%Y%m%d_%H%M%S).sql"}

# Run the backup inside the container
echo "Creating backup inside container..."
docker exec dev-coach-local-db-1 pg_dump -h localhost -U "$LOCAL_DB_USER" -d "$LOCAL_DB_NAME" -F c -b -v -f "/tmp/backup.sql"

# Copy the backup file from the container to the host
echo "Copying backup file from container..."
docker cp dev-coach-local-db-1:/tmp/backup.sql "$OUTPUT_FILE"

# Clean up the temporary file in the container
docker exec dev-coach-local-db-1 rm -f /tmp/backup.sql

echo "Local backup complete: $OUTPUT_FILE" 
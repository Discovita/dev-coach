#!/bin/bash

# Fresh Start Script for Dev Coach
# This script does a complete fresh rebuild of the development environment
# while preserving the database volume (db-data)

set -e  # Exit on error

COMPOSE_PROJECT_NAME=dev-coach-local
COMPOSE_FILES="-f docker/docker-compose.yml -f docker/docker-compose.local.yml"
COMPOSE_PROFILE="--profile local"

echo "🧹 Starting fresh rebuild..."

# Stop and remove containers (but preserve database volume)
# NOTE: 'down' without '-v' flag does NOT remove volumes - this is intentional and safe
echo "📦 Stopping containers..."
COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME docker compose $COMPOSE_PROFILE $COMPOSE_FILES down --remove-orphans || true

# Remove project-specific images
echo "🗑️  Removing project images..."
IMAGES=$(docker images --format "{{.ID}}" --filter "reference=*dev-coach-local*" 2>/dev/null || true)
if [ -n "$IMAGES" ]; then
  echo "$IMAGES" | while read -r image_id; do
    docker rmi "$image_id" 2>/dev/null || echo "  ⚠️  Could not remove image $image_id (may be in use)"
  done
else
  echo "  ℹ️  No project images found to remove"
fi

# Remove project-specific volumes (but preserve database)
# SAFETY: Explicitly exclude database volume with multiple checks
echo "🗑️  Removing project volumes (preserving database)..."
DB_VOLUME="${COMPOSE_PROJECT_NAME}_db-data"

# First, verify database volume exists and is protected
if docker volume inspect "$DB_VOLUME" >/dev/null 2>&1; then
  echo "  🔒 Database volume found: $DB_VOLUME (will be preserved)"
else
  echo "  ℹ️  Database volume not found (will be created on first run)"
fi

# Get volumes to remove (exclude database volume with explicit check)
VOLUMES=$(docker volume ls --format "{{.Name}}" | grep "^${COMPOSE_PROJECT_NAME}_" || true)
if [ -n "$VOLUMES" ]; then
  echo "$VOLUMES" | while read -r volume_name; do
    # DOUBLE SAFETY CHECK: Explicitly skip database volume
    if [ "$volume_name" = "$DB_VOLUME" ]; then
      echo "  ✅ SKIPPING database volume: $volume_name (protected)"
      continue
    fi
    # Additional pattern check as backup
    if echo "$volume_name" | grep -q "_db-data$"; then
      echo "  ✅ SKIPPING database volume (pattern match): $volume_name (protected)"
      continue
    fi
    # Safe to remove - not the database volume
    docker volume rm "$volume_name" 2>/dev/null || echo "  ⚠️  Could not remove volume $volume_name"
  done
else
  echo "  ℹ️  No project volumes found to remove (database preserved)"
fi

# Final verification: Database volume is still intact
echo "🔍 Final safety check: Verifying database volume..."
if docker volume inspect "$DB_VOLUME" >/dev/null 2>&1; then
  VOLUME_SIZE=$(docker system df -v | grep "$DB_VOLUME" | awk '{print $3}' || echo "unknown")
  echo "  ✅ Database volume verified: $DB_VOLUME (size: $VOLUME_SIZE)"
  echo "  ✅ Database is SAFE and PRESERVED"
else
  echo "  ⚠️  Database volume not found (will be created on first run - this is normal for new setups)"
fi

# Fresh rebuild with no cache
echo "🔨 Building fresh containers..."
COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME docker compose $COMPOSE_PROFILE $COMPOSE_FILES build --no-cache

echo "🚀 Starting containers..."
COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME docker compose $COMPOSE_PROFILE $COMPOSE_FILES up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 3

# Check service status
echo "📊 Service status:"
COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME docker compose $COMPOSE_PROFILE $COMPOSE_FILES ps

echo ""
echo "✅ Fresh rebuild complete!"
echo "🌐 Frontend: http://localhost:5173"
echo "🌐 Backend: http://localhost:8000"
echo "🌐 Docs: http://localhost:5174"
echo ""
echo "💡 Tip: Use 'docker compose logs -f [service]' to view logs" 
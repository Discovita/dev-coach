#!/bin/bash
# Render Build Script for Dev Coach - STAGING
# This script handles staging deployment and prompt synchronization

set -e  # Exit on any error

echo "🚀 Starting Render build process for Dev Coach - STAGING..."

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to run command with error handling
run_command() {
    local description="$1"
    local command="$2"
    
    log "🔄 $description..."
    if eval "$command"; then
        log "✅ $description completed successfully"
        return 0
    else
        log "❌ $description failed"
        return 1
    fi
}

# Main build process for staging
main() {
    log "🏗️  Starting Dev Coach STAGING build process..."
    
    # Step 1: Install dependencies
    if ! run_command "Installing Python dependencies" "pip install -r server/requirements.txt"; then
        log "❌ Failed to install dependencies - stopping build"
        exit 1
    fi
    
    # Step 2: Run database migrations
    if ! run_command "Running database migrations" "cd server && python manage.py migrate"; then
        log "❌ Failed to run migrations - stopping build"
        exit 1
    fi
    
    # Step 3: Collect static files
    if ! run_command "Collecting static files" "cd server && python manage.py collectstatic --noinput"; then
        log "❌ Failed to collect static files - stopping build"
        exit 1
    fi
    
    # Step 4: Staging deployment complete    
    log "🎉 STAGING build process completed successfully!"
    log "🚀 Dev Coach STAGING is ready to deploy!"
}

# Run main function
main "$@"
scripts/render/render_build_staging.sh
#!/bin/bash
# Render Build Script for Dev Coach - PRODUCTION
# This script handles production deployment and prompt synchronization

set -e  # Exit on any error

echo "🚀 Starting Render build process for Dev Coach - PRODUCTION..."

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

# Main build process for production
main() {
    log "🏗️  Starting Dev Coach PRODUCTION build process..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SERVER_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
    
    log "📁 Script directory: $SCRIPT_DIR"
    log "📁 Server directory: $SERVER_DIR"
    
    # Step 1: Install dependencies
    if ! run_command "Installing Python dependencies" "pip install -r $SERVER_DIR/requirements.txt"; then
        log "❌ Failed to install dependencies - stopping build"
        exit 1
    fi
    
    # Step 2: Run database migrations
    if ! run_command "Running database migrations" "cd $SERVER_DIR && python manage.py migrate"; then
        log "❌ Failed to run migrations - stopping build"
        exit 1
    fi
    
    # Step 3: Collect static files
    if ! run_command "Collecting static files" "cd $SERVER_DIR && python manage.py collectstatic --noinput"; then
        log "❌ Failed to collect static files - stopping build"
        exit 1
    fi
    
    # Step 4: Copy prompts from staging to production
    log "📋 Starting prompt synchronization for PRODUCTION..."
    if run_command "Copy prompts from staging to production" "cd $SERVER_DIR && python manage.py copy_prompts_to_production --force"; then
        log "✅ Production prompts updated successfully from staging"
    else
        log "⚠️  Production prompt copy failed, but continuing deployment"
    fi
    
    log "🎉 PRODUCTION build process completed successfully!"
    log "🚀 Dev Coach PRODUCTION is ready to deploy!"
}

# Run main function
main "$@"
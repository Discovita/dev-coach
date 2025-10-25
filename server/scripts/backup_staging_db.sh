#!/bin/bash

# Backup the staging database to the local backups/staging directory.
# Usage: ./backup_db.sh [output_file]
# Example: ./backup_db.sh my_backup.sql

# Database credentials - STAGING
DB_HOST="dpg-d360k77fte5s739b8dj0-a.oregon-postgres.render.com"
DB_NAME="staging_coach_database"
DB_USER="staging_coach_database_user"
DB_PASSWORD="mwINn3AqfsluUHX2VXZSPWtIkMPffsIY"

# Output file
OUTPUT_FILE=${1:-"backups/staging/staging_coach_database_backup_$(date +%Y%m%d_%H%M%S).sql"}

# Run the backup
export PGPASSWORD="$DB_PASSWORD"
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -F c -b -v -f "$OUTPUT_FILE"

# Unset password for security
unset PGPASSWORD

echo "Backup complete: $OUTPUT_FILE"

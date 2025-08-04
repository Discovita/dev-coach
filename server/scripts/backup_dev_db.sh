#!/bin/bash

# Usage: ./backup_db.sh [output_file]
# Example: ./backup_db.sh my_backup.sql

# Database credentials
DB_HOST="dpg-d0doal95pdvs739dklo0-a.oregon-postgres.render.com"
DB_NAME="dev_coach_database"
DB_USER="dev_coach_database_user"
DB_PASSWORD="UxRZ75YUsR2wFL6B3JnUDWN8XDyriY3v"

# Output file
OUTPUT_FILE=${1:-"backups/dev/dev_coach_dev_database_backup_$(date +%Y%m%d_%H%M%S).sql"}

# Run the backup
export PGPASSWORD="$DB_PASSWORD"
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -F c -b -v -f "$OUTPUT_FILE"

# Unset password for security
unset PGPASSWORD

echo "Backup complete: $OUTPUT_FILE"

#!/bin/bash

# Usage: ./restore_prod_db_from_dev_backup.sh [dump_file]
# Example: ./restore_prod_db_from_dev_backup.sh backups/dev/dev_coach_dev_database_backup_20250703_170048.sql
# If no dump_file is provided, the script will use the most recent file in backups/dev/

# Dev database credentials
PROD_DB_HOST="dpg-d360k77fte5s739b8dj0-a.oregon-postgres.render.com"
PROD_DB_NAME="staging_coach_database"
PROD_DB_USER="staging_coach_database_user"
PROD_DB_PASSWORD="mwINn3AqfsluUHX2VXZSPWtIkMPffsIY"

# Find the dump file to use
# Gets the most recent file in backups/dev/
if [ -n "$1" ]; then
  DUMP_FILE="$1"
else
  DUMP_FILE=$(ls -t backups/dev/dev_coach_dev_database_backup_*.sql 2>/dev/null | head -n 1)
fi

if [ ! -f "$DUMP_FILE" ]; then
  echo "Error: Dump file not found: $DUMP_FILE"
  echo "Available local backups:"
  ls -la backups/local/dev_coach_dev_database_backup_*.sql 2>/dev/null || echo "No local backups found"
  exit 1
fi

echo "WARNING: This will completely overwrite the staging database!"
echo "Source file: $DUMP_FILE"
echo "Target database: $PROD_DB_NAME on $PROD_DB_HOST"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Restore cancelled."
  exit 0
fi

# Export password so pg_restore doesn't prompt
export PGPASSWORD="$PROD_DB_PASSWORD"

# Restore the database
echo "Restoring $DUMP_FILE to staging database $PROD_DB_NAME..."
pg_restore --clean --no-owner \
  --host="$PROD_DB_HOST" \
  --username="$PROD_DB_USER" \
  --dbname="$PROD_DB_NAME" \
  "$DUMP_FILE"

if [ $? -eq 0 ]; then
  echo "Staging database restore complete."
else
  echo "Staging database restore failed."
  exit 1
fi

# Unset password for security
unset PGPASSWORD 
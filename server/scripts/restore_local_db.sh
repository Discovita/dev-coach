#!/bin/bash

# Usage: ./restore_local_db.sh [dump_file]
# Example: ./restore_local_db.sh backups/dev_coach_database_backup_20250703_170048.sql
# If no dump_file is provided, the script will use the most recent file in backups/

# Local database connection info
LOCAL_DB_NAME="local_dev_coach"
LOCAL_DB_USER="dev_coach_database_user"
LOCAL_DB_HOST="localhost"
LOCAL_DB_PORT="5432"
LOCAL_DB_PASSWORD="UxRZ75YUsR2wFL6B3JnUDWN8XDyriY3v"

# Find the dump file to use
if [ -n "$1" ]; then
  DUMP_FILE="$1"
else
  DUMP_FILE=$(ls -t backups/dev_coach_database_backup_*.sql 2>/dev/null | head -n 1)
fi

if [ ! -f "$DUMP_FILE" ]; then
  echo "Error: Dump file not found: $DUMP_FILE"
  exit 1
fi

# Export password so pg_restore doesn't prompt
export PGPASSWORD="$LOCAL_DB_PASSWORD"

# Restore the database
echo "Restoring $DUMP_FILE to local database $LOCAL_DB_NAME..."
pg_restore --clean --no-owner \
  --host="$LOCAL_DB_HOST" \
  --port="$LOCAL_DB_PORT" \
  --username="$LOCAL_DB_USER" \
  --dbname="$LOCAL_DB_NAME" \
  "$DUMP_FILE"

if [ $? -eq 0 ]; then
  echo "Restore complete."
else
  echo "Restore failed."
fi 
#!/bin/bash

# Usage: ./restore_dev_db_from_local_backup.sh [dump_file]
# Example: ./restore_dev_db_from_local_backup.sh backups/local/dev_coach_local_database_backup_20250703_170048.sql
# If no dump_file is provided, the script will use the most recent file in backups/local/

# Dev database credentials
DEV_DB_HOST="dpg-d0doal95pdvs739dklo0-a.oregon-postgres.render.com"
DEV_DB_NAME="dev_coach_database"
DEV_DB_USER="dev_coach_database_user"
DEV_DB_PASSWORD="UxRZ75YUsR2wFL6B3JnUDWN8XDyriY3v"

# Find the dump file to use
if [ -n "$1" ]; then
  DUMP_FILE="$1"
else
  DUMP_FILE=$(ls -t backups/local/dev_coach_local_database_backup_*.sql 2>/dev/null | head -n 1)
fi

if [ ! -f "$DUMP_FILE" ]; then
  echo "Error: Dump file not found: $DUMP_FILE"
  echo "Available local backups:"
  ls -la backups/local/dev_coach_local_database_backup_*.sql 2>/dev/null || echo "No local backups found"
  exit 1
fi

echo "WARNING: This will completely overwrite the dev database!"
echo "Source file: $DUMP_FILE"
echo "Target database: $DEV_DB_NAME on $DEV_DB_HOST"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Restore cancelled."
  exit 0
fi

# Export password so psql doesn't prompt
export PGPASSWORD="$DEV_DB_PASSWORD"

# First, truncate all tables to clear existing data
echo "Clearing existing data from database $DEV_DB_NAME..."
psql -h "$DEV_DB_HOST" -U "$DEV_DB_USER" -d "$DEV_DB_NAME" -c "
DO \$\$
DECLARE
    r RECORD;
BEGIN
    -- Disable all triggers temporarily
    SET session_replication_role = replica;
    
    -- Truncate all tables in the public schema
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'TRUNCATE TABLE public.' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
    
    -- Re-enable triggers
    SET session_replication_role = DEFAULT;
END \$\$;
"

# Restore the database using psql (for plain SQL format)
echo "Restoring $DUMP_FILE to dev database $DEV_DB_NAME..."
psql -h "$DEV_DB_HOST" -U "$DEV_DB_USER" -d "$DEV_DB_NAME" -f "$DUMP_FILE"

if [ $? -eq 0 ]; then
  echo "Dev database restore complete."
else
  echo "Dev database restore failed."
  exit 1
fi

# Unset password for security
unset PGPASSWORD 
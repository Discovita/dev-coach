"""
Copy all prompts from local to staging database.
Uses pg_dump/psql for a clean table copy.
"""

import subprocess
import os
import tempfile
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Copy all prompts from local to staging database (OVERWRITES staging prompts)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be copied without making changes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompts (use with caution)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        # Local DB config (from environment)
        local_db = {
            'host': os.environ.get('LOCAL_DB_HOST', 'db'),
            'port': os.environ.get('LOCAL_DB_PORT', '5432'),
            'name': os.environ.get('LOCAL_DB_NAME'),
            'user': os.environ.get('LOCAL_DB_USER'),
            'password': os.environ.get('LOCAL_DB_PASSWORD'),
        }

        # Staging DB config (from environment)
        staging_db = {
            'host': os.environ.get('STAGING_DB_HOST'),
            'port': os.environ.get('STAGING_DB_PORT', '5432'),
            'name': os.environ.get('STAGING_DB_NAME'),
            'user': os.environ.get('STAGING_DB_USER'),
            'password': os.environ.get('STAGING_DB_PASSWORD'),
        }

        # Validate required env vars
        missing = []
        for key in ['name', 'user', 'password']:
            if not local_db[key]:
                missing.append(f'LOCAL_DB_{key.upper()}')
            if not staging_db[key]:
                missing.append(f'STAGING_DB_{key.upper()}')
        if not staging_db['host']:
            missing.append('STAGING_DB_HOST')
        
        if missing:
            raise CommandError(f"Missing required environment variables: {', '.join(missing)}")

        self.stdout.write("🔄 Copying prompts from LOCAL to STAGING...")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Step 1: Count local prompts
        self.stdout.write("\n1. Counting local prompts...")
        local_env = os.environ.copy()
        local_env['PGPASSWORD'] = local_db['password']
        
        count_cmd = [
            'psql',
            '-h', local_db['host'],
            '-p', local_db['port'],
            '-U', local_db['user'],
            '-d', local_db['name'],
            '-t', '-c', 'SELECT COUNT(*) FROM prompts_prompt;'
        ]
        
        result = subprocess.run(count_cmd, capture_output=True, text=True, env=local_env)
        if result.returncode != 0:
            raise CommandError(f"Failed to count local prompts: {result.stderr}")
        
        local_count = result.stdout.strip()
        self.stdout.write(f"Found {local_count} prompts in local database")

        if not force and not dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  This will DELETE ALL existing prompts in staging "
                    f"and replace them with {local_count} prompts from local"
                )
            )
            response = input('\nType "YES" to confirm: ')
            if response != 'YES':
                raise CommandError('Copy cancelled')

        if dry_run:
            self.stdout.write("\nDRY RUN: Would copy all prompts from local to staging")
            return

        # Step 2: Dump local prompts table to file
        self.stdout.write("\n2. Dumping local prompts table...")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            dump_file = f.name

        dump_cmd = [
            'pg_dump',
            '-h', local_db['host'],
            '-p', local_db['port'],
            '-U', local_db['user'],
            '-d', local_db['name'],
            '-t', 'prompts_prompt',
            '--data-only',
            '--column-inserts',
            '-f', dump_file
        ]
        
        result = subprocess.run(dump_cmd, capture_output=True, text=True, env=local_env)
        if result.returncode != 0:
            raise CommandError(f"Failed to dump local prompts: {result.stderr}")
        
        self.stdout.write(f"✅ Dumped to {dump_file}")

        # Step 3: Clear staging table and restore
        self.stdout.write("\n3. Clearing staging prompts and restoring...")
        
        staging_env = os.environ.copy()
        staging_env['PGPASSWORD'] = staging_db['password']

        # Delete existing prompts
        delete_cmd = [
            'psql',
            '-h', staging_db['host'],
            '-p', staging_db['port'],
            '-U', staging_db['user'],
            '-d', staging_db['name'],
            '-c', 'DELETE FROM prompts_prompt;'
        ]
        
        result = subprocess.run(delete_cmd, capture_output=True, text=True, env=staging_env)
        if result.returncode != 0:
            raise CommandError(f"Failed to clear staging prompts: {result.stderr}")
        
        self.stdout.write("✅ Cleared staging prompts")

        # Restore from dump
        restore_cmd = [
            'psql',
            '-h', staging_db['host'],
            '-p', staging_db['port'],
            '-U', staging_db['user'],
            '-d', staging_db['name'],
            '-f', dump_file
        ]
        
        result = subprocess.run(restore_cmd, capture_output=True, text=True, env=staging_env)
        if result.returncode != 0:
            raise CommandError(f"Failed to restore prompts: {result.stderr}")
        
        self.stdout.write("✅ Restored prompts to staging")

        # Step 4: Verify
        self.stdout.write("\n4. Verifying...")
        
        verify_cmd = [
            'psql',
            '-h', staging_db['host'],
            '-p', staging_db['port'],
            '-U', staging_db['user'],
            '-d', staging_db['name'],
            '-t', '-c', 'SELECT COUNT(*) FROM prompts_prompt;'
        ]
        
        result = subprocess.run(verify_cmd, capture_output=True, text=True, env=staging_env)
        staging_count = result.stdout.strip()
        
        self.stdout.write(f"✅ Staging now has {staging_count} prompts (was {local_count} locally)")

        # Cleanup
        try:
            os.unlink(dump_file)
        except:
            pass

        self.stdout.write(self.style.SUCCESS("\n✅ Done!"))

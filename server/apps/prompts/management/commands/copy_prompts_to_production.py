"""
Copy all prompts from staging to production database.
Uses pg_dump/psql for a clean table copy.
"""

import subprocess
import os
import tempfile
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Copy all prompts from staging to production database (OVERWRITES production prompts)'

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

        # Staging DB config (from environment)
        staging_db = {
            'host': os.environ.get('STAGING_DB_HOST'),
            'port': os.environ.get('STAGING_DB_PORT', '5432'),
            'name': os.environ.get('STAGING_DB_NAME'),
            'user': os.environ.get('STAGING_DB_USER'),
            'password': os.environ.get('STAGING_DB_PASSWORD'),
        }

        # Production DB config (from environment)
        prod_db = {
            'host': os.environ.get('PROD_DB_HOST'),
            'port': os.environ.get('PROD_DB_PORT', '5432'),
            'name': os.environ.get('PROD_DB_NAME'),
            'user': os.environ.get('PROD_DB_USER'),
            'password': os.environ.get('PROD_DB_PASSWORD'),
        }

        # Validate required env vars
        missing = []
        for key in ['host', 'name', 'user', 'password']:
            if not staging_db[key]:
                missing.append(f'STAGING_DB_{key.upper()}')
            if not prod_db[key]:
                missing.append(f'PROD_DB_{key.upper()}')
        
        if missing:
            raise CommandError(f"Missing required environment variables: {', '.join(missing)}")

        self.stdout.write("🔄 Copying prompts from STAGING to PRODUCTION...")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Step 1: Count staging prompts
        self.stdout.write("\n1. Counting staging prompts...")
        staging_env = os.environ.copy()
        staging_env['PGPASSWORD'] = staging_db['password']
        
        count_cmd = [
            'psql',
            '-h', staging_db['host'],
            '-p', staging_db['port'],
            '-U', staging_db['user'],
            '-d', staging_db['name'],
            '-t', '-c', 'SELECT COUNT(*) FROM prompts_prompt;'
        ]
        
        result = subprocess.run(count_cmd, capture_output=True, text=True, env=staging_env)
        if result.returncode != 0:
            raise CommandError(f"Failed to count staging prompts: {result.stderr}")
        
        staging_count = result.stdout.strip()
        self.stdout.write(f"Found {staging_count} prompts in staging database")

        if not force and not dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  This will DELETE ALL existing prompts in PRODUCTION "
                    f"and replace them with {staging_count} prompts from staging"
                )
            )
            response = input('\nType "YES" to confirm: ')
            if response != 'YES':
                raise CommandError('Copy cancelled')

        if dry_run:
            self.stdout.write("\nDRY RUN: Would copy all prompts from staging to production")
            return

        # Step 2: Dump staging prompts table to file
        self.stdout.write("\n2. Dumping staging prompts table...")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            dump_file = f.name

        dump_cmd = [
            'pg_dump',
            '-h', staging_db['host'],
            '-p', staging_db['port'],
            '-U', staging_db['user'],
            '-d', staging_db['name'],
            '-t', 'prompts_prompt',
            '--data-only',
            '--column-inserts',
            '-f', dump_file
        ]
        
        result = subprocess.run(dump_cmd, capture_output=True, text=True, env=staging_env)
        if result.returncode != 0:
            raise CommandError(f"Failed to dump staging prompts: {result.stderr}")
        
        self.stdout.write(f"✅ Dumped to {dump_file}")

        # Step 3: Clear production table and restore
        self.stdout.write("\n3. Clearing production prompts and restoring...")
        
        prod_env = os.environ.copy()
        prod_env['PGPASSWORD'] = prod_db['password']

        # Delete existing prompts
        delete_cmd = [
            'psql',
            '-h', prod_db['host'],
            '-p', prod_db['port'],
            '-U', prod_db['user'],
            '-d', prod_db['name'],
            '-c', 'DELETE FROM prompts_prompt;'
        ]
        
        result = subprocess.run(delete_cmd, capture_output=True, text=True, env=prod_env)
        if result.returncode != 0:
            raise CommandError(f"Failed to clear production prompts: {result.stderr}")
        
        self.stdout.write("✅ Cleared production prompts")

        # Restore from dump
        restore_cmd = [
            'psql',
            '-h', prod_db['host'],
            '-p', prod_db['port'],
            '-U', prod_db['user'],
            '-d', prod_db['name'],
            '-f', dump_file
        ]
        
        result = subprocess.run(restore_cmd, capture_output=True, text=True, env=prod_env)
        if result.returncode != 0:
            raise CommandError(f"Failed to restore prompts: {result.stderr}")
        
        self.stdout.write("✅ Restored prompts to production")

        # Step 4: Verify
        self.stdout.write("\n4. Verifying...")
        
        verify_cmd = [
            'psql',
            '-h', prod_db['host'],
            '-p', prod_db['port'],
            '-U', prod_db['user'],
            '-d', prod_db['name'],
            '-t', '-c', 'SELECT COUNT(*) FROM prompts_prompt;'
        ]
        
        result = subprocess.run(verify_cmd, capture_output=True, text=True, env=prod_env)
        prod_count = result.stdout.strip()
        
        self.stdout.write(f"✅ Production now has {prod_count} prompts (was {staging_count} in staging)")

        # Cleanup
        try:
            os.unlink(dump_file)
        except:
            pass

        self.stdout.write(self.style.SUCCESS("\n✅ Done!"))

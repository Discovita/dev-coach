"""
Copy all prompts from local to staging database.
This command connects directly to the staging database and overwrites all prompts.
"""

import subprocess
import os
import tempfile
from django.core.management.base import BaseCommand, CommandError
from apps.prompts.models import Prompt
from django.core.serializers.json import DjangoJSONEncoder
import json


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

        self.stdout.write("🔄 Copying prompts from LOCAL to STAGING...")
        self.stdout.write("This will OVERWRITE all prompts in staging with your local prompts.")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Get local prompts
        self.stdout.write("\n1. Getting prompts from local database...")
        local_prompts = list(Prompt.objects.all().order_by('coaching_phase', 'version'))
        self.stdout.write(f"Found {len(local_prompts)} prompts in local database")

        if not local_prompts:
            self.stdout.write(self.style.WARNING("No prompts found in local database"))
            return

        # Show confirmation
        if not force and not dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  This will DELETE ALL existing prompts in staging "
                    f"and replace them with {len(local_prompts)} prompts from local"
                )
            )
            response = input('\nAre you sure you want to OVERWRITE ALL PROMPTS in staging? Type "YES" to confirm: ')
            if response != 'YES':
                raise CommandError('Copy cancelled - confirmation not provided')
        elif force:
            self.stdout.write(self.style.WARNING("⚠️  FORCE mode: Skipping confirmation"))

        if dry_run:
            self.stdout.write("\nDRY RUN: Would copy the following prompts:")
            for prompt in local_prompts:
                self.stdout.write(f"  - {prompt.coaching_phase} v{prompt.version}: {prompt.name or 'Unnamed'}")
            return

        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            prompts_data = []
            for prompt in local_prompts:
                prompt_data = {
                    'coaching_phase': prompt.coaching_phase,
                    'version': prompt.version,
                    'name': prompt.name,
                    'description': prompt.description,
                    'body': prompt.body,
                    'required_context_keys': prompt.required_context_keys,
                    'allowed_actions': prompt.allowed_actions,
                    'prompt_type': prompt.prompt_type,
                    'is_active': prompt.is_active,
                }
                prompts_data.append(prompt_data)
            
            json.dump(prompts_data, f, indent=2, cls=DjangoJSONEncoder, ensure_ascii=False)
            temp_file = f.name

        try:
            # Use psql to connect to staging database and execute SQL
            self.stdout.write("\n2. Copying prompts to staging database...")
            
            # Test connection first
            self.stdout.write("Testing connection to staging database...")
            test_cmd = [
                'psql',
                '-h', 'dpg-d360k77fte5s739b8dj0-a.oregon-postgres.render.com',
                '-p', '5432',
                '-U', 'staging_coach_database_user',
                '-d', 'staging_coach_database',
                '-c', 'SELECT COUNT(*) FROM prompts_prompt;'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = 'mwINn3AqfsluUHX2VXZSPWtIkMPffsIY'
            
            test_result = subprocess.run(test_cmd, capture_output=True, text=True, env=env)
            if test_result.returncode == 0:
                self.stdout.write(f"✅ Connection successful. Current prompts in staging: {test_result.stdout.strip()}")
            else:
                self.stdout.write(f"❌ Connection failed: {test_result.stderr}")
                raise CommandError(f"Failed to connect to staging database: {test_result.stderr}")
            
            # Create SQL script
            sql_script = f'''
-- Delete all existing prompts
DELETE FROM prompts_prompt;

-- Insert new prompts
'''
            
            for prompt_data in prompts_data:
                # Escape single quotes in text fields
                name = prompt_data.get('name', '').replace("'", "''") if prompt_data.get('name') else ''
                description = prompt_data.get('description', '').replace("'", "''") if prompt_data.get('description') else ''
                body = prompt_data['body'].replace("'", "''")
                
                # Convert lists to PostgreSQL array format
                required_context_keys = prompt_data.get("required_context_keys", [])
                allowed_actions = prompt_data.get("allowed_actions", [])
                
                # Format as PostgreSQL array: ARRAY['item1','item2'] or ARRAY[]::text[] for empty arrays
                if required_context_keys:
                    required_context_keys_array = "ARRAY[" + ",".join([f"'{key}'" for key in required_context_keys]) + "]"
                else:
                    required_context_keys_array = "ARRAY[]::text[]"
                
                if allowed_actions:
                    allowed_actions_array = "ARRAY[" + ",".join([f"'{action}'" for action in allowed_actions]) + "]"
                else:
                    allowed_actions_array = "ARRAY[]::text[]"
                
                sql_script += f'''
INSERT INTO prompts_prompt (
    id, coaching_phase, version, name, description, body, 
    required_context_keys, allowed_actions, prompt_type, is_active, 
    created_at, updated_at
) VALUES (
    gen_random_uuid(), 
    '{prompt_data["coaching_phase"]}', 
    {prompt_data["version"]}, 
    {f"'{name}'" if name else 'NULL'}, 
    {f"'{description}'" if description else 'NULL'}, 
    '{body}', 
    {required_context_keys_array}, 
    {allowed_actions_array}, 
    '{prompt_data.get("prompt_type", "COACH")}', 
    {str(prompt_data.get("is_active", True)).lower()}, 
    NOW(), 
    NOW()
);
'''

            # Write SQL script to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as sql_file:
                sql_file.write(sql_script)
                sql_script_file = sql_file.name

            # Execute SQL on staging database
            psql_cmd = [
                'psql',
                '-h', 'dpg-d360k77fte5s739b8dj0-a.oregon-postgres.render.com',
                '-p', '5432',
                '-U', 'staging_coach_database_user',
                '-d', 'staging_coach_database',
                '-f', sql_script_file
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = 'mwINn3AqfsluUHX2VXZSPWtIkMPffsIY'
            
            # Debug: Show the SQL script being executed
            self.stdout.write(f"\n3. Executing SQL script ({len(prompts_data)} prompts)...")
            self.stdout.write(f"SQL script length: {len(sql_script)} characters")
            
            result = subprocess.run(psql_cmd, capture_output=True, text=True, env=env, check=True)
            
            self.stdout.write(f"✅ Successfully copied {len(prompts_data)} prompts to staging database!")
            if result.stdout:
                self.stdout.write("SQL Output:")
                self.stdout.write(result.stdout)
            if result.stderr:
                self.stdout.write("SQL Errors:")
                self.stdout.write(result.stderr)
            
            # Verify the copy worked
            self.stdout.write("\n4. Verifying copy...")
            verify_cmd = [
                'psql',
                '-h', 'dpg-d360k77fte5s739b8dj0-a.oregon-postgres.render.com',
                '-p', '5432',
                '-U', 'staging_coach_database_user',
                '-d', 'staging_coach_database',
                '-c', 'SELECT COUNT(*) FROM prompts_prompt;'
            ]
            
            verify_result = subprocess.run(verify_cmd, capture_output=True, text=True, env=env)
            if verify_result.returncode == 0:
                count = verify_result.stdout.strip()
                self.stdout.write(f"✅ Verification: {count} prompts now in staging database")
                if count == "0":
                    self.stdout.write(self.style.ERROR("❌ WARNING: No prompts found in staging after copy!"))
            else:
                self.stdout.write(f"❌ Verification failed: {verify_result.stderr}")

        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to copy prompts: {e.stderr}"))
            raise CommandError(f"Failed to copy prompts: {e.stderr}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to copy prompts: {e}"))
            raise CommandError(f"Failed to copy prompts: {e}")
        finally:
            # Clean up temp files
            try:
                os.unlink(temp_file)
                os.unlink(sql_script_file)
            except:
                pass

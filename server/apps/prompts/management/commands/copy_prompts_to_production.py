"""
Copy all prompts from staging to production database.
This command connects to staging database, gets the prompts, then overwrites production prompts.
"""

import subprocess
import os
import tempfile
from django.core.management.base import BaseCommand, CommandError
import json


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

        self.stdout.write("🔄 Copying prompts from STAGING to PRODUCTION...")
        self.stdout.write("This will OVERWRITE all prompts in production with staging prompts.")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Get prompts from staging database
        self.stdout.write("\n1. Getting prompts from staging database...")
        
        # Create SQL query to get prompts from staging
        staging_query = '''
SELECT json_agg(
    json_build_object(
        'coaching_phase', coaching_phase,
        'version', version,
        'name', name,
        'description', description,
        'body', body,
        'required_context_keys', required_context_keys,
        'allowed_actions', allowed_actions,
        'prompt_type', prompt_type,
        'is_active', is_active
    ) ORDER BY coaching_phase, version
) FROM prompts_prompt;
'''

        try:
            # Query staging database
            staging_cmd = [
                '/opt/homebrew/bin/psql',
                '-h', 'dpg-d360k77fte5s739b8dj0-a.oregon-postgres.render.com',
                '-p', '5432',
                '-U', 'staging_coach_database_user',
                '-d', 'staging_coach_database',
                '-t', '-A'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = 'mwINn3AqfsluUHX2VXZSPWtIkMPffsIY'
            
            result = subprocess.run(staging_cmd, input=staging_query, capture_output=True, text=True, env=env, check=True)
            
            # Debug: Show raw output
            self.stdout.write(f"Raw staging query output: {repr(result.stdout)}")
            self.stdout.write(f"Raw staging query stderr: {repr(result.stderr)}")
            
            if not result.stdout.strip():
                self.stdout.write(self.style.WARNING("No prompts found in staging database"))
                return
            
            # Parse the JSON results
            import json
            prompts_data = []
            if result.stdout.strip():
                try:
                    # Parse the JSON array
                    json_data = json.loads(result.stdout.strip())
                    if json_data:
                        for i, prompt in enumerate(json_data):
                            self.stdout.write(f"Processing prompt {i + 1}: {prompt.get('name', 'Unknown')}")
                            
                            prompt_data = {
                                'coaching_phase': prompt.get('coaching_phase'),
                                'version': prompt.get('version', 1),
                                'name': prompt.get('name'),
                                'description': prompt.get('description'),
                                'body': prompt.get('body'),
                                'required_context_keys': prompt.get('required_context_keys', []),
                                'allowed_actions': prompt.get('allowed_actions', []),
                                'prompt_type': prompt.get('prompt_type', 'COACH'),
                                'is_active': prompt.get('is_active', True),
                            }
                            prompts_data.append(prompt_data)
                    else:
                        self.stdout.write("No prompts found in JSON response")
                except json.JSONDecodeError as e:
                    self.stdout.write(f"Failed to parse JSON: {e}")
                    self.stdout.write(f"Raw output: {result.stdout[:200]}...")
                    return
            
            self.stdout.write(f"Found {len(prompts_data)} prompts in staging database")

            if not prompts_data:
                self.stdout.write(self.style.WARNING("No prompts found in staging database"))
                return

            # Show confirmation
            if not force and not dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n⚠️  This will DELETE ALL existing prompts in production "
                        f"and replace them with {len(prompts_data)} prompts from staging"
                    )
                )
                response = input('\nAre you sure you want to OVERWRITE ALL PROMPTS in production? Type "YES" to confirm: ')
                if response != 'YES':
                    raise CommandError('Copy cancelled - confirmation not provided')

            if dry_run:
                self.stdout.write("\nDRY RUN: Would copy the following prompts:")
                for prompt_data in prompts_data:
                    name = prompt_data.get('name') or 'Unnamed'
                    phase = prompt_data.get('coaching_phase') or 'None'
                    version = prompt_data.get('version', 1)
                    self.stdout.write(f"  - {phase} v{version}: {name}")
                return

            # Create SQL script for production
            self.stdout.write("\n2. Copying prompts to production database...")
            
            sql_script = '''
-- Delete all existing prompts
DELETE FROM prompts_prompt;

-- Insert new prompts
'''
            
            for prompt_data in prompts_data:
                # Escape single quotes in text fields
                name = prompt_data.get('name', '').replace("'", "''") if prompt_data.get('name') else ''
                description = prompt_data.get('description', '').replace("'", "''") if prompt_data.get('description') else ''
                body = prompt_data['body'].replace("'", "''")
                
                sql_script += f'''
INSERT INTO prompts_prompt (
    id, coaching_phase, version, name, description, body, 
    required_context_keys, allowed_actions, prompt_type, is_active, 
    created_at, updated_at
) VALUES (
    gen_random_uuid(), 
    {f"'{prompt_data['coaching_phase']}'" if prompt_data.get('coaching_phase') else 'NULL'}, 
    {prompt_data.get('version', 1)}, 
    {f"'{name}'" if name else 'NULL'}, 
    {f"'{description}'" if description else 'NULL'}, 
    '{body}', 
    {repr(prompt_data.get("required_context_keys", []))}, 
    {repr(prompt_data.get("allowed_actions", []))}, 
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

            # Execute SQL on production database
            prod_cmd = [
                '/opt/homebrew/bin/psql',
                '-h', 'dpg-d360ammr433s73ag30kg-a.oregon-postgres.render.com',
                '-p', '5432',
                '-U', 'prod_coach_database_user',
                '-d', 'prod_coach_database',
                '-f', sql_script_file
            ]
            
            # Set password via environment variable
            env['PGPASSWORD'] = 'RMPGY6BH2FAIMnAPyApngz9Usky3voHQ'
            
            result = subprocess.run(prod_cmd, capture_output=True, text=True, env=env, check=True)
            
            self.stdout.write(f"✅ Successfully copied {len(prompts_data)} prompts from staging to production!")
            if result.stdout:
                self.stdout.write(result.stdout)

        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to copy prompts: {e.stderr}"))
            raise CommandError(f"Failed to copy prompts: {e.stderr}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to copy prompts: {e}"))
            raise CommandError(f"Failed to copy prompts: {e}")
        finally:
            # Clean up temp files
            try:
                if 'sql_script_file' in locals():
                    os.unlink(sql_script_file)
            except:
                pass

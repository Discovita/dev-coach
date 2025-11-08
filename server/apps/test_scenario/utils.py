"""
Utility functions for test scenario image handling.
"""
import boto3
import os
import uuid
import urllib.parse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime
from services.logger import configure_logging

log = configure_logging(__name__, log_level="INFO")


def duplicate_s3_image(source_image_field, new_upload_to_path=None):
    """
    Duplicate an image in S3 by copying the object within S3.
    
    Args:
        source_image_field: Django VersatileImageField instance with existing image
        new_upload_to_path: Optional custom path, otherwise uses UUID-based path
        
    Returns:
        S3 key (path) for the duplicated image, or None if duplication fails
    """
    if not source_image_field or not source_image_field.name:
        log.warning("Source image field is empty, cannot duplicate")
        return None
    
    try:
        # Get bucket name and region from STORAGES
        bucket_name = None
        region_name = None
        if hasattr(settings, 'STORAGES') and 'default' in settings.STORAGES:
            bucket_name = settings.STORAGES['default']['OPTIONS'].get('bucket_name')
            region_name = settings.STORAGES['default']['OPTIONS'].get('region_name', 'us-east-1')
        
        if not bucket_name:
            log.error("Could not determine bucket name from STORAGES settings")
            return None
        
        # Get S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=region_name,
        )
        source_key = source_image_field.name
        
        # Generate destination path
        if new_upload_to_path:
            # Use provided path
            dest_path = new_upload_to_path
            filename = os.path.basename(source_key)
            dest_key = os.path.join(dest_path, filename).replace("\\", "/")
        else:
            # Use UUID-based path (compatible with VersatileImageField)
            filename = os.path.basename(source_key)
            uuid_dir = str(uuid.uuid4())
            dest_key = os.path.join("media", uuid_dir, filename).replace("\\", "/")
        
        # Copy object within S3
        copy_source = {
            'Bucket': bucket_name,
            'Key': source_key
        }
        
        log.info(f"Duplicating S3 image from {source_key} to {dest_key}")
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=bucket_name,
            Key=dest_key
        )
        
        # Return the destination key (path) so caller can use it
        return dest_key
        
    except Exception as e:
        log.error(f"Error duplicating S3 image: {str(e)}", exc_info=True)
        return None


def copy_image_from_url(image_url, upload_to_path=None):
    """
    Copy an image from a URL (S3 or external) to a new S3 location using UUID-based paths.
    
    Args:
        image_url: URL of the source image (S3 URL or external URL)
        upload_to_path: Optional custom path (defaults to UUID-based path via uuid_upload_path)
        
    Returns:
        S3 key (path) for the copied image, or None if copy fails
    """
    if not image_url:
        return None
    
    try:
        # Get bucket name and custom domain from STORAGES
        bucket_name = None
        s3_custom_domain = None
        if hasattr(settings, 'STORAGES') and 'default' in settings.STORAGES:
            bucket_name = settings.STORAGES['default']['OPTIONS'].get('bucket_name')
            s3_custom_domain = settings.STORAGES['default']['OPTIONS'].get('custom_domain')
        
        if not bucket_name:
            log.error("Could not determine bucket name from STORAGES settings")
            return None
        
        s3_domain = f"{bucket_name}.s3.amazonaws.com"
        
        is_s3_url = False
        source_key = None
        
        # Check if URL is from our S3 bucket
        if s3_domain in image_url or (s3_custom_domain and s3_custom_domain in image_url):
            is_s3_url = True
            # Extract key from URL
            # URL format: https://bucket.s3.amazonaws.com/media/identities/2024/01/01/image.jpg
            # or: https://bucket.s3.amazonaws.com/identities/2024/01/01/image.jpg
            # or: https://custom-domain/media/identities/2024/01/01/image.jpg
            source_key = None
            if '/media/' in image_url:
                source_key = image_url.split('/media/')[1].split('?')[0]  # Remove query params
            elif f"{bucket_name}.s3.amazonaws.com" in image_url:
                # Extract after bucket domain
                parts = image_url.split(f"{bucket_name}.s3.amazonaws.com/")
                if len(parts) > 1:
                    source_key = parts[1].split('?')[0]  # Remove query params
            elif s3_custom_domain and s3_custom_domain in image_url:
                # Extract from custom domain URL
                parts = image_url.split(f"{s3_custom_domain}/")
                if len(parts) > 1:
                    source_key = parts[1].split('?')[0]  # Remove query params
            
            # URL decode the key in case it has encoded characters (e.g., %20 for spaces)
            if source_key:
                source_key = urllib.parse.unquote(source_key)
        
        if is_s3_url and source_key:
            # Try to use Django's storage backend to get the actual key
            # This is more reliable than trying to extract it from the URL
            try:
                # Use default_storage to normalize the path
                # If the URL was generated by default_storage.url(), we can reverse it
                # by checking what key corresponds to the URL
                # default_storage automatically uses STORAGES['default']
                # Try to get the actual key by checking if the path exists
                # The storage backend might have a location prefix
                normalized_key = source_key
                # Remove leading slash if present
                if normalized_key.startswith('/'):
                    normalized_key = normalized_key[1:]
            except Exception as e:
                log.warning(f"Could not normalize key using storage backend: {str(e)}")
                normalized_key = source_key
            # Use S3 copy (most efficient)
            # Get region from STORAGES config or fall back to AWS_REGION
            region_name = None
            if hasattr(settings, 'STORAGES') and 'default' in settings.STORAGES:
                region_name = settings.STORAGES['default']['OPTIONS'].get('region_name')
            if not region_name:
                region_name = getattr(settings, 'AWS_REGION', 'us-east-1')
            
            # Try both with and without 'media/' prefix since django-storages might store with or without it
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=region_name,
            )
            
            # Try to find the actual key - check both with and without media/ prefix
            # Also try the normalized key
            actual_source_key = None
            possible_keys = [
                normalized_key,  # Normalized key
                source_key,  # As extracted (e.g., identities/2025/11/08/image.jpg)
                f"media/{source_key}",  # With media/ prefix
                f"media/{normalized_key}",  # Normalized with media/ prefix
            ]
            # Remove duplicates while preserving order
            possible_keys = list(dict.fromkeys(possible_keys))
            
            # Check which key actually exists in S3
            for key_to_check in possible_keys:
                try:
                    s3_client.head_object(Bucket=bucket_name, Key=key_to_check)
                    actual_source_key = key_to_check
                    log.info(f"Found image in S3 at key: {actual_source_key}")
                    break
                except s3_client.exceptions.ClientError as e:
                    if e.response['Error']['Code'] != '404':
                        raise
                    continue
            
            if not actual_source_key:
                log.error(f"Image not found in S3 with any of these keys: {possible_keys}")
                return None
            
            # Generate destination path using UUID-based upload path
            if upload_to_path:
                # Use provided path
                now = datetime.now()
                if '%Y' in upload_to_path:
                    dest_path = now.strftime(upload_to_path)
                else:
                    dest_path = upload_to_path
                filename = os.path.basename(actual_source_key)
                dest_key = os.path.join(dest_path, filename).replace("\\", "/")
            else:
                # Use UUID-based path (compatible with VersatileImageField)
                filename = os.path.basename(actual_source_key)
                # Generate a UUID-based path manually (same format as uuid_upload_path)
                uuid_dir = str(uuid.uuid4())
                dest_key = os.path.join("media", uuid_dir, filename).replace("\\", "/")
            
            # Copy object within S3
            copy_source = {
                'Bucket': bucket_name,
                'Key': actual_source_key
            }
            
            log.info(f"Copying image within S3 from {actual_source_key} to {dest_key}")
            s3_client.copy_object(
                CopySource=copy_source,
                Bucket=bucket_name,
                Key=dest_key
            )
            
            # Return the destination key (path) so caller can use it
            return dest_key
        else:
            # Download from external URL and upload to S3
            import requests
            
            log.info(f"Downloading image from external URL: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Extract filename from URL or generate one
            filename = os.path.basename(image_url.split('?')[0])  # Remove query params
            if not filename or '.' not in filename:
                # Generate filename with extension based on content type
                content_type = response.headers.get('content-type', 'image/jpeg')
                ext = content_type.split('/')[-1] if '/' in content_type else 'jpg'
                filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            
            # Generate destination path using UUID-based upload path
            if upload_to_path:
                # Use provided path
                now = datetime.now()
                if '%Y' in upload_to_path:
                    dest_path = now.strftime(upload_to_path)
                else:
                    dest_path = upload_to_path
                dest_key = os.path.join(dest_path, filename).replace("\\", "/")
            else:
                # Use UUID-based path (compatible with VersatileImageField)
                # Note: Don't include "media" prefix - storage backend adds it via location setting
                uuid_dir = str(uuid.uuid4())
                dest_key = os.path.join(uuid_dir, filename).replace("\\", "/")
            
            # Save to S3 using default_storage (automatically uses STORAGES['default'])
            content_file = ContentFile(response.content)
            saved_path = default_storage.save(dest_key, content_file)
            
            # Return the saved path so caller can use it
            return saved_path
            
    except Exception as e:
        log.error(f"Error copying image from URL {image_url}: {str(e)}", exc_info=True)
        return None


"""
Utility functions for test scenario image handling.
"""
import boto3
import os
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
        source_image_field: Django ImageField instance with existing image
        new_upload_to_path: Optional custom path, otherwise uses Identity model's upload_to pattern
        
    Returns:
        Django File instance with duplicated image, or None if duplication fails
    """
    if not source_image_field or not source_image_field.name:
        log.warning("Source image field is empty, cannot duplicate")
        return None
    
    try:
        # Get S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        source_key = source_image_field.name
        
        # Generate destination path
        if new_upload_to_path:
            # Use provided path
            dest_path = new_upload_to_path
        else:
            # Use Identity model's upload_to pattern: identities/%Y/%m/%d/
            now = datetime.now()
            dest_path = f"identities/{now.year}/{now.month:02d}/{now.day:02d}/"
        
        # Extract filename from source
        filename = os.path.basename(source_key)
        dest_key = os.path.join(dest_path, filename).replace("\\", "/")
        
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


def copy_image_from_url(image_url, upload_to_path="identities/%Y/%m/%d/"):
    """
    Copy an image from a URL (S3 or external) to a new S3 location.
    
    Args:
        image_url: URL of the source image (S3 URL or external URL)
        upload_to_path: Path pattern for upload (supports strftime formatting)
        
    Returns:
        Django File instance with copied image, or None if copy fails
    """
    if not image_url:
        return None
    
    try:
        # Check if it's an S3 URL in the same bucket
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3_domain = f"{bucket_name}.s3.amazonaws.com"
        s3_custom_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
        
        is_s3_url = False
        source_key = None
        
        # Check if URL is from our S3 bucket
        if s3_domain in image_url or (s3_custom_domain and s3_custom_domain in image_url):
            is_s3_url = True
            # Extract key from URL
            # URL format: https://bucket.s3.amazonaws.com/media/identities/2024/01/01/image.jpg
            # or: https://bucket.s3.amazonaws.com/identities/2024/01/01/image.jpg
            # or: https://custom-domain/media/identities/2024/01/01/image.jpg
            if '/media/' in image_url:
                source_key = image_url.split('/media/')[1].split('?')[0]  # Remove query params
            elif f"{bucket_name}.s3.amazonaws.com" in image_url:
                # Extract after bucket domain
                parts = image_url.split(f"{bucket_name}.s3.amazonaws.com/")
                if len(parts) > 1:
                    source_key = parts[1].split('?')[0]  # Remove query params
                else:
                    source_key = None
            elif s3_custom_domain and s3_custom_domain in image_url:
                # Extract from custom domain URL
                parts = image_url.split(f"{s3_custom_domain}/")
                if len(parts) > 1:
                    source_key = parts[1].split('?')[0]  # Remove query params
                else:
                    source_key = None
            else:
                source_key = None
        
        if is_s3_url and source_key:
            # Use S3 copy (most efficient)
            log.info(f"Copying image within S3 from {source_key}")
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )
            
            # Generate destination path
            now = datetime.now()
            if '%Y' in upload_to_path:
                dest_path = now.strftime(upload_to_path)
            else:
                dest_path = upload_to_path
            
            filename = os.path.basename(source_key)
            dest_key = os.path.join(dest_path, filename).replace("\\", "/")
            
            # Copy object within S3
            copy_source = {
                'Bucket': bucket_name,
                'Key': source_key
            }
            
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
            
            # Generate destination path
            now = datetime.now()
            if '%Y' in upload_to_path:
                dest_path = now.strftime(upload_to_path)
            else:
                dest_path = upload_to_path
            
            # Extract filename from URL or generate one
            filename = os.path.basename(image_url.split('?')[0])  # Remove query params
            if not filename or '.' not in filename:
                # Generate filename with extension based on content type
                content_type = response.headers.get('content-type', 'image/jpeg')
                ext = content_type.split('/')[-1] if '/' in content_type else 'jpg'
                filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            
            dest_key = os.path.join(dest_path, filename).replace("\\", "/")
            
            # Save to S3 using Django storage
            content_file = ContentFile(response.content)
            saved_path = default_storage.save(dest_key, content_file)
            
            # Return the saved path so caller can use it
            return saved_path
            
    except Exception as e:
        log.error(f"Error copying image from URL {image_url}: {str(e)}", exc_info=True)
        return None


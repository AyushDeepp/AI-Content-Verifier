"""
Cloudflare R2 Storage Service
Handles file uploads to R2 bucket with S3-compatible API.
Falls back to local storage if R2 is not configured.
"""
import boto3
import logging
import uuid
from io import BytesIO
from core.config import settings

logger = logging.getLogger(__name__)

_s3_client = None


def _get_client():
    """Lazy-init the S3 client for R2."""
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name=settings.R2_REGION or "auto",
        )
    return _s3_client


def is_r2_configured() -> bool:
    """Check if R2 credentials are set."""
    return all([
        settings.R2_ACCOUNT_ID,
        settings.R2_ACCESS_KEY_ID,
        settings.R2_SECRET_ACCESS_KEY,
        settings.R2_BUCKET_NAME,
        settings.R2_PUBLIC_URL,
    ])


def upload_to_r2(file_data: bytes, file_name: str, content_type: str = "application/octet-stream") -> str:
    """
    Upload file to Cloudflare R2 and return the public URL.
    
    Args:
        file_data: Raw file bytes
        file_name: Filename to use in the bucket (e.g. "abc123.png")
        content_type: MIME type of the file
    
    Returns:
        Public URL of the uploaded file
    """
    try:
        client = _get_client()
        
        # Upload with a key under "ai-verifier/" prefix
        key = f"ai-verifier/{file_name}"
        
        client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
            Body=file_data,
            ContentType=content_type,
        )
        
        # Build public URL
        public_url = f"{settings.R2_PUBLIC_URL.rstrip('/')}/{key}"
        logger.info(f"R2 UPLOAD: {file_name} -> {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"R2 upload failed: {e}")
        raise


def delete_from_r2(file_url: str) -> bool:
    """Delete a file from R2 by its public URL."""
    try:
        # Extract key from URL
        prefix = f"{settings.R2_PUBLIC_URL.rstrip('/')}/"
        if file_url.startswith(prefix):
            key = file_url[len(prefix):]
        else:
            # Might be an old /uploads/ path — skip
            return False
        
        client = _get_client()
        client.delete_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=key,
        )
        logger.info(f"R2 DELETE: {key}")
        return True
    except Exception as e:
        logger.warning(f"R2 delete failed: {e}")
        return False

"""
Cloudflare R2 storage client for video uploads.
R2 is S3-compatible, so we use boto3.
"""
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from typing import Optional
import uuid
import logging

from config import get_settings

logger = logging.getLogger(__name__)


class StorageClient:
    """Cloudflare R2 S3-compatible storage client."""
    
    _instance: Optional['StorageClient'] = None
    _s3_client: Optional[boto3.client] = None
    _bucket_name: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._s3_client is None:
            settings = get_settings()
            self._bucket_name = settings.r2_bucket_name
            
            if settings.r2_endpoint_url and settings.r2_access_key_id:
                try:
                    self._s3_client = boto3.client(
                        's3',
                        endpoint_url=settings.r2_endpoint_url,
                        aws_access_key_id=settings.r2_access_key_id,
                        aws_secret_access_key=settings.r2_secret_access_key,
                        region_name=settings.r2_region,
                        config=Config(
                            signature_version='s3v4',
                            retries={'max_attempts': 3}
                        )
                    )
                    logger.info("R2 storage client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize R2 client: {e}")
            else:
                logger.warning("R2 credentials not configured")
    
    @property
    def client(self) -> Optional[boto3.client]:
        """Get the S3 client instance."""
        return self._s3_client
    
    @property
    def bucket_name(self) -> str:
        """Get the bucket name."""
        return self._bucket_name or "deposafety-videos"
    
    def generate_video_key(self, scan_id: str, filename: str) -> str:
        """Generate a unique key for video storage."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        # Sanitize filename
        safe_filename = filename.replace(" ", "_").lower()
        return f"scans/{scan_id}/{timestamp}_{unique_id}_{safe_filename}"
    
    async def generate_upload_url(
        self, 
        key: str, 
        content_type: str = "video/mp4",
        expires_in: int = 3600
    ) -> Optional[str]:
        """Generate a presigned URL for direct video upload."""
        if not self._s3_client:
            logger.error("S3 client not initialized")
            return None
        
        try:
            url = self._s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key,
                    'ContentType': content_type
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating upload URL: {e}")
            return None
    
    async def generate_download_url(
        self, 
        key: str, 
        expires_in: int = 3600
    ) -> Optional[str]:
        """Generate a presigned URL for video download/viewing."""
        if not self._s3_client:
            return None
        
        try:
            url = self._s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating download URL: {e}")
            return None
    
    async def delete_video(self, key: str) -> bool:
        """Delete a video from storage."""
        if not self._s3_client:
            return False
        
        try:
            self._s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"Deleted video: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting video: {e}")
            return False
    
    async def get_video_metadata(self, key: str) -> Optional[dict]:
        """Get metadata for a stored video."""
        if not self._s3_client:
            return None
        
        try:
            response = self._s3_client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return {
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag')
            }
        except ClientError as e:
            logger.error(f"Error getting video metadata: {e}")
            return None
    
    async def list_videos(self, prefix: str = "", max_keys: int = 100) -> list:
        """List videos in storage with optional prefix."""
        if not self._s3_client:
            return []
        
        try:
            response = self._s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"Error listing videos: {e}")
            return []
    
    def get_public_url(self, key: str) -> str:
        """Get the public URL for a video (if bucket is public)."""
        settings = get_settings()
        # R2 public URLs typically use the custom domain or account URL
        base_url = settings.r2_endpoint_url.rstrip('/')
        return f"{base_url}/{self.bucket_name}/{key}"


# Global storage client instance
storage = StorageClient()

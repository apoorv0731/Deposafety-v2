#!/usr/bin/env python3
"""
API Client for DepoSafety V2 Backend Webhooks
Handles notifications for 3DGS processing status
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class WebhookClient:
    """Client for sending webhook notifications to backend"""
    
    def __init__(self, 
                 base_url: str,
                 api_key: Optional[str] = None,
                 timeout: int = 30,
                 max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key or os.getenv('DEPO_API_KEY')
        self.timeout = timeout
        
        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth if available"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DepoSafety-ML-Pipeline/1.0'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            headers['X-API-Key'] = self.api_key
        return headers
        
    def send_notification(self, 
                         endpoint: str,
                         payload: Dict[str, Any]) -> bool:
        """Send notification to backend"""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        try:
            response = self.session.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Webhook sent successfully: {url}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook failed: {e}")
            return False
            
    def notify_processing_started(self,
                                  job_id: str,
                                  video_path: str,
                                  metadata: Optional[Dict] = None) -> bool:
        """Notify backend that processing has started"""
        payload = {
            'event': 'processing_started',
            'job_id': job_id,
            'video_path': video_path,
            'timestamp': self._get_timestamp(),
            'metadata': metadata or {}
        }
        return self.send_notification('/api/v1/ml/webhook/processing-started', payload)
        
    def notify_progress(self,
                       job_id: str,
                       stage: str,
                       progress: float,
                       message: Optional[str] = None) -> bool:
        """Send progress update"""
        payload = {
            'event': 'processing_progress',
            'job_id': job_id,
            'stage': stage,
            'progress': progress,
            'message': message,
            'timestamp': self._get_timestamp()
        }
        return self.send_notification('/api/v1/ml/webhook/progress', payload)
        
    def notify_processing_complete(self,
                                  job_id: str,
                                  status: str,
                                  models: Optional[Dict[str, str]] = None,
                                  error: Optional[str] = None,
                                  r2_urls: Optional[Dict[str, str]] = None) -> bool:
        """Notify backend that processing is complete"""
        payload = {
            'event': 'processing_complete',
            'job_id': job_id,
            'status': status,  # 'completed' or 'failed'
            'timestamp': self._get_timestamp(),
            'models': models or {},
            'r2_urls': r2_urls or {}
        }
        
        if error:
            payload['error'] = error
            
        return self.send_notification('/api/v1/ml/webhook/processing-complete', payload)
        
    @staticmethod
    def _get_timestamp() -> str:
        """Get ISO format timestamp"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


# Convenience functions for standalone usage
def notify_processing_complete(webhook_url: str,
                               job_id: str,
                               status: str,
                               models: Optional[Dict[str, str]] = None,
                               error: Optional[str] = None,
                               api_key: Optional[str] = None) -> bool:
    """
    Standalone function to notify backend of processing completion.
    
    Args:
        webhook_url: Backend webhook URL
        job_id: Unique job identifier
        status: 'completed' or 'failed'
        models: Dict with 'ply' and 'splat' file paths
        error: Error message if failed
        api_key: Optional API key for authentication
    """
    client = WebhookClient(webhook_url, api_key=api_key)
    return client.notify_processing_complete(
        job_id=job_id,
        status=status,
        models=models,
        error=error
    )


def notify_processing_started(webhook_url: str,
                              job_id: str,
                              video_path: str,
                              api_key: Optional[str] = None) -> bool:
    """Standalone function to notify processing start"""
    client = WebhookClient(webhook_url, api_key=api_key)
    return client.notify_processing_started(
        job_id=job_id,
        video_path=video_path
    )


class R2Uploader:
    """Upload models to Cloudflare R2"""
    
    def __init__(self,
                 account_id: str,
                 access_key_id: str,
                 secret_access_key: str,
                 bucket_name: str):
        self.account_id = account_id
        self.bucket_name = bucket_name
        
        # R2 uses S3-compatible API
        import boto3
        self.s3 = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )
        
    def upload_file(self, 
                   local_path: str,
                   remote_key: str,
                   content_type: Optional[str] = None) -> Optional[str]:
        """Upload file to R2 and return public URL"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
                
            self.s3.upload_file(
                local_path,
                self.bucket_name,
                remote_key,
                ExtraArgs=extra_args
            )
            
            # Build public URL
            public_url = f"https://{self.account_id}.r2.cloudflarestorage.com/{self.bucket_name}/{remote_key}"
            logger.info(f"Uploaded to R2: {public_url}")
            return public_url
            
        except Exception as e:
            logger.error(f"R2 upload failed: {e}")
            return None
            
    def upload_models(self,
                     job_id: str,
                     ply_path: Optional[str] = None,
                     splat_path: Optional[str] = None) -> Dict[str, str]:
        """Upload both model files and return URLs"""
        urls = {}
        
        if ply_path and os.path.exists(ply_path):
            key = f"models/{job_id}/model.ply"
            url = self.upload_file(ply_path, key, 'application/octet-stream')
            if url:
                urls['ply'] = url
                
        if splat_path and os.path.exists(splat_path):
            key = f"models/{job_id}/model.splat"
            url = self.upload_file(splat_path, key, 'application/octet-stream')
            if url:
                urls['splat'] = url
                
        return urls


def create_r2_uploader_from_env() -> Optional[R2Uploader]:
    """Create R2 uploader from environment variables"""
    account_id = os.getenv('R2_ACCOUNT_ID')
    access_key = os.getenv('R2_ACCESS_KEY_ID')
    secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
    bucket = os.getenv('R2_BUCKET_NAME')
    
    if all([account_id, access_key, secret_key, bucket]):
        return R2Uploader(account_id, access_key, secret_key, bucket)
    
    logger.warning("R2 credentials not found in environment")
    return None


if __name__ == "__main__":
    # Test webhook
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--webhook", required=True, help="Webhook URL")
    parser.add_argument("--job-id", default="test-job", help="Job ID")
    parser.add_argument("--status", default="completed", help="Status")
    parser.add_argument("--api-key", help="API key")
    
    args = parser.parse_args()
    
    success = notify_processing_complete(
        webhook_url=args.webhook,
        job_id=args.job_id,
        status=args.status,
        models={'ply': '/path/to/model.ply', 'splat': '/path/to/model.splat'},
        api_key=args.api_key
    )
    
    print(f"Notification {'sent' if success else 'failed'}")

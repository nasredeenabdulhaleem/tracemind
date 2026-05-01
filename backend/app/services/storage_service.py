"""Cloudflare R2 storage service for repository management"""

import boto3
from botocore.exceptions import ClientError
import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class RepoStorageService:
    """Service for managing repository storage in Cloudflare R2"""
    
    def __init__(self):
        """Initialize S3 client configured for Cloudflare R2"""
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key,
            aws_secret_access_key=settings.r2_secret_key,
            region_name='auto'  # R2 uses 'auto' for region
        )
        self.bucket = settings.r2_bucket
        self.temp_dir = Path(settings.temp_dir)
        
        # Ensure temp directory exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_repo(self, local_path: str, object_key: str) -> bool:
        """
        Compress and upload repository to R2
        
        Args:
            local_path: Path to local repository directory
            object_key: R2 object key (e.g., 'user_id/project_id.zip')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create temporary zip file
            zip_path = self.temp_dir / f"{object_key.replace('/', '_')}"
            
            logger.info(f"Compressing repository: {local_path}")
            self._compress_directory(local_path, str(zip_path))
            
            # Upload to R2
            logger.info(f"Uploading to R2: {object_key}")
            with open(zip_path, 'rb') as file_data:
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=object_key,
                    Body=file_data,
                    ContentType='application/zip'
                )
            
            # Clean up temp zip file
            zip_path.unlink()
            
            logger.info(f"Successfully uploaded: {object_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload repo: {e}")
            return False
    
    def download_repo(self, object_key: str, extract_to: Optional[str] = None) -> Optional[str]:
        """
        Download and extract repository from R2
        
        Args:
            object_key: R2 object key
            extract_to: Optional path to extract to (creates temp dir if None)
            
        Returns:
            Path to extracted directory or None if failed
        """
        try:
            # Create temp directory for download
            if extract_to is None:
                extract_to = tempfile.mkdtemp(dir=self.temp_dir)
            else:
                os.makedirs(extract_to, exist_ok=True)
            
            # Download from R2
            zip_path = Path(extract_to) / "repo.zip"
            logger.info(f"Downloading from R2: {object_key}")
            
            self.s3_client.download_file(
                Bucket=self.bucket,
                Key=object_key,
                Filename=str(zip_path)
            )
            
            # Extract zip file
            logger.info(f"Extracting to: {extract_to}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            # Remove zip file
            zip_path.unlink()
            
            logger.info(f"Successfully downloaded and extracted: {object_key}")
            return extract_to
            
        except ClientError as e:
            logger.error(f"Failed to download repo: {e}")
            return None
    
    def delete_repo(self, object_key: str) -> bool:
        """
        Delete repository from R2
        
        Args:
            object_key: R2 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Deleting from R2: {object_key}")
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=object_key
            )
            logger.info(f"Successfully deleted: {object_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete repo: {e}")
            return False
    
    def repo_exists(self, object_key: str) -> bool:
        """
        Check if repository exists in R2
        
        Args:
            object_key: R2 object key
            
        Returns:
            True if exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket,
                Key=object_key
            )
            return True
        except ClientError:
            return False
    
    def get_repo_size(self, object_key: str) -> Optional[int]:
        """
        Get repository size in bytes
        
        Args:
            object_key: R2 object key
            
        Returns:
            Size in bytes or None if not found
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket,
                Key=object_key
            )
            return response['ContentLength']
        except ClientError:
            return None
    
    def cleanup_temp_dir(self, path: str) -> bool:
        """
        Clean up temporary directory
        
        Args:
            path: Path to directory to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                logger.info(f"Cleaned up temp directory: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup temp dir: {e}")
            return False
    
    @staticmethod
    def _compress_directory(source_dir: str, output_path: str) -> None:
        """
        Compress directory to zip file
        
        Args:
            source_dir: Directory to compress
            output_path: Output zip file path
        """
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            source_path = Path(source_dir)
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    # Skip common files that shouldn't be uploaded
                    if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'node_modules', '.env']):
                        continue
                    
                    arcname = file_path.relative_to(source_path.parent)
                    zipf.write(file_path, arcname)
    
    def generate_object_key(self, user_id: str, project_id: str) -> str:
        """
        Generate R2 object key for a project
        
        Args:
            user_id: User UUID
            project_id: Project UUID
            
        Returns:
            Object key string
        """
        return f"{user_id}/{project_id}.zip"

# Made with Bob
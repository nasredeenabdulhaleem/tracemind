"""Repository ingestion service for GitHub and ZIP uploads"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple
import logging
from git import Repo, GitCommandError
from fastapi import UploadFile, HTTPException, status

from app.services.storage_service import RepoStorageService
from app.config import settings

logger = logging.getLogger(__name__)


class RepoIngestionService:
    """Service for ingesting repositories from GitHub or ZIP uploads"""
    
    def __init__(self):
        self.storage_service = RepoStorageService()
        self.temp_dir = Path(settings.temp_dir)
        self.max_upload_size = settings.max_upload_size
    
    async def ingest_github_repo(
        self,
        repo_url: str,
        user_id: str,
        project_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Clone GitHub repository and upload to R2
        
        Args:
            repo_url: GitHub repository URL
            user_id: User UUID
            project_id: Project UUID
            
        Returns:
            Tuple of (success, r2_object_key, error_message)
        """
        temp_clone_dir = None
        
        try:
            # Validate GitHub URL
            if not self._is_valid_github_url(repo_url):
                return False, None, "Invalid GitHub URL"
            
            # Create temp directory for cloning
            temp_clone_dir = tempfile.mkdtemp(dir=self.temp_dir)
            logger.info(f"Cloning repository: {repo_url}")
            
            # Clone repository (shallow clone for speed)
            try:
                Repo.clone_from(
                    repo_url,
                    temp_clone_dir,
                    depth=1,  # Shallow clone
                    single_branch=True
                )
            except GitCommandError as e:
                logger.error(f"Git clone failed: {e}")
                return False, None, f"Failed to clone repository: {str(e)}"
            
            # Generate R2 object key
            object_key = self.storage_service.generate_object_key(user_id, project_id)
            
            # Upload to R2
            success = self.storage_service.upload_repo(temp_clone_dir, object_key)
            
            if success:
                logger.info(f"Successfully ingested GitHub repo: {repo_url}")
                return True, object_key, None
            else:
                return False, None, "Failed to upload to storage"
                
        except Exception as e:
            logger.error(f"Failed to ingest GitHub repo: {e}")
            return False, None, str(e)
            
        finally:
            # Cleanup temp directory
            if temp_clone_dir and os.path.exists(temp_clone_dir):
                self.storage_service.cleanup_temp_dir(temp_clone_dir)
    
    async def ingest_zip_upload(
        self,
        file: UploadFile,
        user_id: str,
        project_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process ZIP file upload and upload to R2
        
        Args:
            file: Uploaded ZIP file
            user_id: User UUID
            project_id: Project UUID
            
        Returns:
            Tuple of (success, r2_object_key, error_message)
        """
        temp_extract_dir = None
        temp_zip_path = None
        
        try:
            # Validate file
            validation_error = self._validate_zip_file(file)
            if validation_error:
                return False, None, validation_error
            
            # Create temp directory
            temp_extract_dir = tempfile.mkdtemp(dir=self.temp_dir)
            temp_zip_path = Path(temp_extract_dir) / "upload.zip"
            
            # Save uploaded file
            logger.info(f"Saving uploaded ZIP file")
            with open(temp_zip_path, "wb") as buffer:
                content = await file.read()
                
                # Check file size
                if len(content) > self.max_upload_size:
                    return False, None, f"File too large. Max size: {self.max_upload_size / 1024 / 1024}MB"
                
                buffer.write(content)
            
            # Extract ZIP
            logger.info(f"Extracting ZIP file")
            import zipfile
            try:
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract_dir)
            except zipfile.BadZipFile:
                return False, None, "Invalid ZIP file"
            
            # Remove the uploaded zip file
            temp_zip_path.unlink()
            
            # Find the actual repo directory (handle single root folder)
            repo_dir = self._find_repo_root(temp_extract_dir)
            
            # Generate R2 object key
            object_key = self.storage_service.generate_object_key(user_id, project_id)
            
            # Upload to R2
            success = self.storage_service.upload_repo(repo_dir, object_key)
            
            if success:
                logger.info(f"Successfully ingested ZIP upload")
                return True, object_key, None
            else:
                return False, None, "Failed to upload to storage"
                
        except Exception as e:
            logger.error(f"Failed to ingest ZIP upload: {e}")
            return False, None, str(e)
            
        finally:
            # Cleanup temp directory
            if temp_extract_dir and os.path.exists(temp_extract_dir):
                self.storage_service.cleanup_temp_dir(temp_extract_dir)
    
    def _is_valid_github_url(self, url: str) -> bool:
        """
        Validate GitHub URL format
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid GitHub URL
        """
        valid_patterns = [
            'github.com/',
            'https://github.com/',
            'http://github.com/',
            'git@github.com:'
        ]
        return any(pattern in url for pattern in valid_patterns)
    
    def _validate_zip_file(self, file: UploadFile) -> Optional[str]:
        """
        Validate uploaded ZIP file
        
        Args:
            file: Uploaded file
            
        Returns:
            Error message if invalid, None if valid
        """
        # Check file extension
        if not file.filename or not file.filename.endswith('.zip'):
            return "File must be a ZIP archive"
        
        # Check content type
        if file.content_type not in ['application/zip', 'application/x-zip-compressed']:
            return "Invalid file type. Must be a ZIP archive"
        
        return None
    
    def _find_repo_root(self, extract_dir: str) -> str:
        """
        Find the actual repository root directory
        
        Some ZIP files have a single root folder, this finds the actual content
        
        Args:
            extract_dir: Directory where ZIP was extracted
            
        Returns:
            Path to repository root
        """
        extract_path = Path(extract_dir)
        
        # Check if there's a single directory at root
        items = list(extract_path.iterdir())
        
        # Filter out the upload.zip if it still exists
        items = [item for item in items if item.name != 'upload.zip']
        
        # If there's only one directory, use it as root
        if len(items) == 1 and items[0].is_dir():
            return str(items[0])
        
        # Otherwise, use the extract directory itself
        return extract_dir
    
    async def get_repo_stats(self, repo_path: str) -> dict:
        """
        Get statistics about a repository
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with repo statistics
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'languages': set()
        }
        
        repo_path_obj = Path(repo_path)
        
        for file_path in repo_path_obj.rglob('*'):
            if file_path.is_file():
                # Skip hidden and system files
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                
                stats['total_files'] += 1
                stats['total_size'] += file_path.stat().st_size
                
                # Track file extensions
                ext = file_path.suffix.lower()
                if ext:
                    stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                    
                    # Detect language
                    language = self._detect_language(ext)
                    if language:
                        stats['languages'].add(language)
        
        stats['languages'] = list(stats['languages'])
        return stats
    
    @staticmethod
    def _detect_language(extension: str) -> Optional[str]:
        """
        Detect programming language from file extension
        
        Args:
            extension: File extension (with dot)
            
        Returns:
            Language name or None
        """
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala'
        }
        return language_map.get(extension)

# Made with Bob
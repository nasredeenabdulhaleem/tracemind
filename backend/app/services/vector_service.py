"""Vector indexing service using FAISS"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk
from app.config import settings

logger = logging.getLogger(__name__)


class VectorIndexService:
    """Service for creating and managing FAISS vector indices"""
    
    # Model for generating embeddings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and efficient
    EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2
    
    def __init__(self):
        """Initialize embedding model and index storage"""
        self.model = None
        self.indices = {}  # Cache for loaded indices
        self.index_dir = Path(settings.temp_dir) / "indices"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model lazily
        self._init_model()
    
    def _init_model(self):
        """Initialize sentence transformer model (offline, from local cache)"""
        try:
            # Force offline mode so no network calls are made to huggingface.co
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            logger.info(f"Loading embedding model: {self.EMBEDDING_MODEL}")
            self.model = SentenceTransformer(self.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def create_index(self, project_id: str, db: Session) -> Tuple[int, str]:
        """
        Create FAISS index for a project's code chunks
        
        Args:
            project_id: Project UUID
            db: Database session
            
        Returns:
            Tuple of (chunks_indexed, index_path)
        """
        # Get all chunks for project
        chunks = db.query(CodeChunk).filter(
            CodeChunk.project_id == project_id
        ).all()
        
        if not chunks:
            raise ValueError("No code chunks found for project")
        
        logger.info(f"Creating index for {len(chunks)} chunks")
        
        # Generate embeddings
        texts = [self._prepare_chunk_text(chunk) for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        index = faiss.IndexFlatL2(self.EMBEDDING_DIM)
        index.add(embeddings.astype('float32'))
        
        # Create metadata mapping
        metadata = {
            i: {
                'chunk_id': str(chunk.id),
                'file_path': chunk.file_path,
                'start_line': chunk.start_line,
                'end_line': chunk.end_line,
                'language': chunk.language,
                'chunk_type': chunk.chunk_type
            }
            for i, chunk in enumerate(chunks)
        }
        
        # Save index and metadata
        index_path = self._save_index(project_id, index, metadata)
        
        # Cache in memory
        self.indices[project_id] = {
            'index': index,
            'metadata': metadata
        }
        
        logger.info(f"Index created and saved: {index_path}")
        return len(chunks), index_path
    
    def search_similar(
        self,
        project_id: str,
        query: str,
        top_k: int = 5,
        db: Session = None
    ) -> List[Dict]:
        """
        Search for similar code chunks using vector similarity
        
        Args:
            project_id: Project UUID
            query: Search query text
            top_k: Number of results to return
            db: Database session (optional, for loading index)
            
        Returns:
            List of similar chunks with scores
        """
        # Load index if not cached
        if project_id not in self.indices:
            if not self._load_index(project_id):
                raise ValueError(f"No index found for project {project_id}")
        
        index_data = self.indices[project_id]
        index = index_data['index']
        metadata = index_data['metadata']
        
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search
        distances, indices = index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            min(top_k, index.ntotal)
        )
        
        # Prepare results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for empty results
                continue
            
            chunk_meta = metadata[int(idx)]
            results.append({
                'rank': i + 1,
                'score': float(1 / (1 + dist)),  # Convert distance to similarity score
                'distance': float(dist),
                'chunk_id': chunk_meta['chunk_id'],
                'file_path': chunk_meta['file_path'],
                'start_line': chunk_meta['start_line'],
                'end_line': chunk_meta['end_line'],
                'language': chunk_meta['language'],
                'chunk_type': chunk_meta['chunk_type']
            })
        
        return results
    
    def get_chunk_content(self, chunk_id: str, db: Session) -> Optional[str]:
        """
        Get full content of a code chunk
        
        Args:
            chunk_id: Chunk UUID
            db: Database session
            
        Returns:
            Chunk content or None
        """
        chunk = db.query(CodeChunk).filter(CodeChunk.id == chunk_id).first()
        return chunk.content if chunk else None
    
    def delete_index(self, project_id: str) -> bool:
        """
        Delete index for a project
        
        Args:
            project_id: Project UUID
            
        Returns:
            True if deleted, False if not found
        """
        # Remove from cache
        if project_id in self.indices:
            del self.indices[project_id]
        
        # Delete files
        index_path = self.index_dir / f"{project_id}.index"
        metadata_path = self.index_dir / f"{project_id}.metadata"
        
        deleted = False
        if index_path.exists():
            index_path.unlink()
            deleted = True
        
        if metadata_path.exists():
            metadata_path.unlink()
            deleted = True
        
        return deleted
    
    def index_exists(self, project_id: str) -> bool:
        """
        Check if index exists for a project
        
        Args:
            project_id: Project UUID
            
        Returns:
            True if index exists
        """
        index_path = self.index_dir / f"{project_id}.index"
        return index_path.exists()
    
    def _prepare_chunk_text(self, chunk: CodeChunk) -> str:
        """
        Prepare chunk text for embedding
        
        Args:
            chunk: CodeChunk object
            
        Returns:
            Formatted text for embedding
        """
        # Include metadata for better context
        text = f"File: {chunk.file_path}\n"
        text += f"Language: {chunk.language}\n"
        text += f"Type: {chunk.chunk_type}\n"
        text += f"Lines: {chunk.start_line}-{chunk.end_line}\n\n"
        text += chunk.content
        
        return text
    
    def _save_index(self, project_id: str, index: faiss.Index, metadata: Dict) -> str:
        """
        Save FAISS index and metadata to disk
        
        Args:
            project_id: Project UUID
            index: FAISS index
            metadata: Chunk metadata
            
        Returns:
            Path to saved index
        """
        index_path = self.index_dir / f"{project_id}.index"
        metadata_path = self.index_dir / f"{project_id}.metadata"
        
        # Save FAISS index
        faiss.write_index(index, str(index_path))
        
        # Save metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        return str(index_path)
    
    def _load_index(self, project_id: str) -> bool:
        """
        Load FAISS index and metadata from disk
        
        Args:
            project_id: Project UUID
            
        Returns:
            True if loaded successfully
        """
        index_path = self.index_dir / f"{project_id}.index"
        metadata_path = self.index_dir / f"{project_id}.metadata"
        
        if not index_path.exists() or not metadata_path.exists():
            return False
        
        try:
            # Load FAISS index
            index = faiss.read_index(str(index_path))
            
            # Load metadata
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            # Cache in memory
            self.indices[project_id] = {
                'index': index,
                'metadata': metadata
            }
            
            logger.info(f"Index loaded for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def get_index_stats(self, project_id: str) -> Optional[Dict]:
        """
        Get statistics about an index
        
        Args:
            project_id: Project UUID
            
        Returns:
            Dictionary with index statistics or None
        """
        if project_id not in self.indices:
            if not self._load_index(project_id):
                return None
        
        index_data = self.indices[project_id]
        index = index_data['index']
        metadata = index_data['metadata']
        
        return {
            'total_vectors': index.ntotal,
            'dimension': index.d,
            'total_chunks': len(metadata),
            'index_type': type(index).__name__
        }

# Made with Bob
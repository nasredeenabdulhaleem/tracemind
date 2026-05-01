"""Code parsing service using tree-sitter"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from sqlalchemy.orm import Session

from app.models.code_chunk import CodeChunk
from app.models.project import Project

logger = logging.getLogger(__name__)


class CodeParserService:
    """Service for parsing code files and creating chunks"""
    
    # Chunk configuration
    MAX_CHUNK_LINES = 500
    CHUNK_OVERLAP = 50
    
    # Supported languages
    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript'
    }
    
    def __init__(self):
        """Initialize parsers for supported languages"""
        self.parsers = {}
        self._init_parsers()
    
    def _init_parsers(self):
        """Initialize tree-sitter parsers"""
        try:
            # Python parser
            PY_LANGUAGE = Language(tspython.language(), "python")
            py_parser = Parser()
            py_parser.set_language(PY_LANGUAGE)
            self.parsers['python'] = py_parser
            
            # JavaScript/TypeScript parser
            JS_LANGUAGE = Language(tsjavascript.language(), "javascript")
            js_parser = Parser()
            js_parser.set_language(JS_LANGUAGE)
            self.parsers['javascript'] = js_parser
            self.parsers['typescript'] = js_parser  # TypeScript uses JS parser
            
            logger.info("Tree-sitter parsers initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize parsers: {e}")
            raise
    
    def parse_repository(
        self,
        repo_path: str,
        project_id: str,
        db: Session
    ) -> Tuple[int, int]:
        """
        Parse all supported files in repository and create chunks
        
        Args:
            repo_path: Path to repository directory
            project_id: Project UUID
            db: Database session
            
        Returns:
            Tuple of (files_parsed, chunks_created)
        """
        files_parsed = 0
        chunks_created = 0
        
        repo_path_obj = Path(repo_path)
        
        # Find all supported files
        for file_path in repo_path_obj.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Skip hidden files and common directories
            if any(part.startswith('.') for part in file_path.parts):
                continue
            if any(skip in str(file_path) for skip in ['node_modules', '__pycache__', 'venv', 'dist', 'build']):
                continue
            
            # Check if file extension is supported
            ext = file_path.suffix.lower()
            if ext not in self.SUPPORTED_EXTENSIONS:
                continue
            
            try:
                # Parse file
                chunks = self.parse_file(str(file_path), repo_path)
                
                if chunks:
                    # Store chunks in database
                    relative_path = str(file_path.relative_to(repo_path_obj))
                    self._store_chunks(chunks, project_id, relative_path, db)
                    
                    files_parsed += 1
                    chunks_created += len(chunks)
                    
                    logger.debug(f"Parsed {relative_path}: {len(chunks)} chunks")
                    
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                continue
        
        logger.info(f"Parsing complete: {files_parsed} files, {chunks_created} chunks")
        return files_parsed, chunks_created
    
    def parse_file(self, file_path: str, repo_root: str) -> List[Dict]:
        """
        Parse a single file and create chunks
        
        Args:
            file_path: Path to file
            repo_root: Repository root path
            
        Returns:
            List of chunk dictionaries
        """
        # Detect language
        ext = Path(file_path).suffix.lower()
        language = self.SUPPORTED_EXTENSIONS.get(ext)
        
        if not language or language not in self.parsers:
            return []
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse with tree-sitter
            parser = self.parsers[language]
            tree = parser.parse(bytes(content, 'utf8'))
            
            # Extract functions/classes
            definitions = self._extract_definitions(tree.root_node, content, language)
            
            # Create chunks
            chunks = self._create_chunks(content, definitions, language)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return []
    
    def _extract_definitions(self, node, content: str, language: str) -> List[Dict]:
        """
        Extract function and class definitions from AST
        
        Args:
            node: Tree-sitter node
            content: File content
            language: Programming language
            
        Returns:
            List of definition dictionaries
        """
        definitions = []
        
        # Node types to extract based on language
        target_types = {
            'python': ['function_definition', 'class_definition'],
            'javascript': ['function_declaration', 'class_declaration', 'method_definition'],
            'typescript': ['function_declaration', 'class_declaration', 'method_definition']
        }
        
        types = target_types.get(language, [])
        
        def traverse(n):
            if n.type in types:
                start_line = n.start_point[0]
                end_line = n.end_point[0]
                
                # Get definition name
                name = self._get_definition_name(n, content)
                
                definitions.append({
                    'type': n.type,
                    'name': name,
                    'start_line': start_line,
                    'end_line': end_line
                })
            
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return definitions
    
    def _get_definition_name(self, node, content: str) -> str:
        """Extract name from function/class definition"""
        for child in node.children:
            if child.type == 'identifier':
                start = child.start_byte
                end = child.end_byte
                return content[start:end]
        return "anonymous"
    
    def _create_chunks(
        self,
        content: str,
        definitions: List[Dict],
        language: str
    ) -> List[Dict]:
        """
        Create code chunks with overlap
        
        Args:
            content: File content
            definitions: List of function/class definitions
            language: Programming language
            
        Returns:
            List of chunk dictionaries
        """
        lines = content.split('\n')
        total_lines = len(lines)
        chunks = []
        chunk_index = 0
        
        # If file is small, create single chunk
        if total_lines <= self.MAX_CHUNK_LINES:
            chunks.append({
                'content': content,
                'start_line': 0,
                'end_line': total_lines - 1,
                'chunk_index': 0,
                'language': language,
                'chunk_type': 'full_file'
            })
            return chunks
        
        # Create overlapping chunks
        start_line = 0
        
        while start_line < total_lines:
            end_line = min(start_line + self.MAX_CHUNK_LINES, total_lines)
            
            # Extract chunk content
            chunk_lines = lines[start_line:end_line]
            chunk_content = '\n'.join(chunk_lines)
            
            # Determine chunk type
            chunk_type = self._determine_chunk_type(start_line, end_line, definitions)
            
            chunks.append({
                'content': chunk_content,
                'start_line': start_line,
                'end_line': end_line - 1,
                'chunk_index': chunk_index,
                'language': language,
                'chunk_type': chunk_type
            })
            
            chunk_index += 1
            
            # Move to next chunk with overlap
            if end_line >= total_lines:
                break
            
            start_line = end_line - self.CHUNK_OVERLAP
        
        return chunks
    
    def _determine_chunk_type(
        self,
        start_line: int,
        end_line: int,
        definitions: List[Dict]
    ) -> str:
        """Determine the type of code in chunk"""
        # Check if chunk contains any definitions
        for defn in definitions:
            if defn['start_line'] >= start_line and defn['end_line'] < end_line:
                return defn['type']
        
        return 'code_block'
    
    def _store_chunks(
        self,
        chunks: List[Dict],
        project_id: str,
        file_path: str,
        db: Session
    ):
        """
        Store code chunks in database
        
        Args:
            chunks: List of chunk dictionaries
            project_id: Project UUID
            file_path: Relative file path
            db: Database session
        """
        for chunk_data in chunks:
            chunk = CodeChunk(
                project_id=project_id,
                file_path=file_path,
                chunk_index=chunk_data['chunk_index'],
                content=chunk_data['content'],
                start_line=chunk_data['start_line'],
                end_line=chunk_data['end_line'],
                language=chunk_data['language'],
                chunk_type=chunk_data['chunk_type']
            )
            db.add(chunk)
        
        db.commit()
    
    def get_parsing_stats(self, project_id: str, db: Session) -> Dict:
        """
        Get parsing statistics for a project
        
        Args:
            project_id: Project UUID
            db: Database session
            
        Returns:
            Dictionary with parsing statistics
        """
        chunks = db.query(CodeChunk).filter(CodeChunk.project_id == project_id).all()
        
        stats = {
            'total_chunks': len(chunks),
            'languages': {},
            'chunk_types': {},
            'files': set()
        }
        
        for chunk in chunks:
            # Count by language
            stats['languages'][chunk.language] = stats['languages'].get(chunk.language, 0) + 1
            
            # Count by type
            stats['chunk_types'][chunk.chunk_type] = stats['chunk_types'].get(chunk.chunk_type, 0) + 1
            
            # Track unique files
            stats['files'].add(chunk.file_path)
        
        stats['total_files'] = len(stats['files'])
        stats['files'] = list(stats['files'])
        
        return stats

# Made with Bob
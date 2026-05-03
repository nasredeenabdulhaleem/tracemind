"""Code Retrieval Agent - Uses vector search to find relevant code"""

from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent


class CodeRetrievalAgent(BaseAgent):
    """Agent for retrieving relevant code chunks using vector search"""
    
    def __init__(self):
        # This agent primarily uses vector search, not LLM generation
        super().__init__(model_id="meta-llama/llama-3-3-70b-instruct")
    
    def build_prompt(self, **kwargs) -> str:
        """Not used for this agent"""
        return ""
    
    def process(
        self,
        bug_info: Dict[str, Any],
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process search results and select most relevant code chunks
        
        Args:
            bug_info: Structured bug information from BugUnderstandingAgent
            search_results: Vector search results from VectorIndexService
            
        Returns:
            Selected relevant code chunks
        """
        # Filter and rank results
        relevant_chunks = []
        
        for result in search_results[:5]:  # Top 5 results
            relevant_chunks.append({
                "file_path": result["file_path"],
                "start_line": result["start_line"],
                "end_line": result["end_line"],
                "language": result["language"],
                "content": result.get("content", ""),
                "relevance_score": result["score"]
            })
        
        return {
            "relevant_chunks": relevant_chunks,
            "total_chunks": len(relevant_chunks),
            "search_query": bug_info.get("summary", "")
        }

# Made with Bob
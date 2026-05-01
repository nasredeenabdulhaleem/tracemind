"""Root Cause Agent - Analyzes code to identify bug root cause"""

from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent


class RootCauseAgent(BaseAgent):
    """Agent for identifying root cause of bugs"""
    
    def __init__(self):
        super().__init__(model_id="ibm/granite-13b-chat-v2")
    
    def build_prompt(
        self,
        bug_info: Dict[str, Any],
        code_chunks: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for root cause analysis"""
        
        # Format code chunks
        code_context = ""
        for i, chunk in enumerate(code_chunks, 1):
            code_context += f"\n--- File {i}: {chunk['file_path']} (lines {chunk['start_line']}-{chunk['end_line']}) ---\n"
            code_context += chunk['content']
            code_context += "\n"
        
        return f"""You are an expert software engineer performing root cause analysis.

Bug Summary: {bug_info.get('summary', 'Unknown')}
Bug Type: {bug_info.get('bug_type', 'Unknown')}
Affected Components: {', '.join(bug_info.get('affected_components', []))}

Relevant Code:
{code_context}

Analyze the code and identify the root cause of the bug. Provide:
1. Root Cause: Clear explanation of what's causing the bug
2. Affected Code: Specific file and line numbers
3. Why It Happens: Technical explanation
4. Impact: What problems this causes

Respond in a structured format."""
    
    def process(
        self,
        bug_info: Dict[str, Any],
        code_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze code and identify root cause
        
        Args:
            bug_info: Structured bug information
            code_chunks: Relevant code chunks
            
        Returns:
            Root cause analysis
        """
        prompt = self.build_prompt(bug_info, code_chunks)
        response = self.generate_with_retry(prompt)
        
        if not response:
            return {
                "root_cause": "Unable to determine root cause",
                "affected_files": [chunk["file_path"] for chunk in code_chunks],
                "explanation": "Analysis failed",
                "confidence": "low"
            }
        
        return {
            "root_cause": response,
            "affected_files": [chunk["file_path"] for chunk in code_chunks],
            "explanation": response,
            "confidence": "medium"
        }

# Made with Bob
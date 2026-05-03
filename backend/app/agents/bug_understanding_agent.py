"""Bug Understanding Agent - Extracts intent from bug descriptions"""

from typing import Dict, Any
import json
from app.agents.base_agent import BaseAgent


class BugUnderstandingAgent(BaseAgent):
    """Agent for understanding and structuring bug descriptions"""
    
    def __init__(self):
        super().__init__(model_id="meta-llama/llama-3-3-70b-instruct")
    
    def build_prompt(self, bug_description: str) -> str:
        """Build prompt for bug understanding"""
        return f"""You are an expert software engineer analyzing a bug report.

Bug Description:
{bug_description}

Extract and structure the following information in JSON format:
1. summary: A concise one-line summary of the bug
2. affected_components: List of likely affected components/modules
3. bug_type: Type of bug (e.g., logic error, null pointer, race condition, etc.)
4. severity: Estimated severity (low, medium, high, critical)
5. keywords: Key technical terms related to the bug

Respond ONLY with valid JSON, no additional text.

JSON:"""
    
    def process(self, bug_description: str) -> Dict[str, Any]:
        """
        Process bug description and extract structured information
        
        Args:
            bug_description: Raw bug description from user
            
        Returns:
            Structured bug information
        """
        prompt = self.build_prompt(bug_description)
        response = self.generate_with_retry(prompt)
        
        if not response:
            return {
                "summary": bug_description[:100],
                "affected_components": [],
                "bug_type": "unknown",
                "severity": "medium",
                "keywords": []
            }
        
        try:
            # Parse JSON response
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "summary": bug_description[:100],
                "affected_components": [],
                "bug_type": "unknown",
                "severity": "medium",
                "keywords": [],
                "raw_response": response
            }

# Made with Bob
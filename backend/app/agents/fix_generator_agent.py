"""Fix Generator Agent - Generates code fixes for bugs"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent


class FixGeneratorAgent(BaseAgent):
    """Agent for generating code fixes"""
    
    def __init__(self):
        super().__init__(model_id="ibm/granite-20b-code-instruct")
    
    def build_prompt(
        self,
        bug_info: Dict[str, Any],
        root_cause: Dict[str, Any],
        affected_code: str
    ) -> str:
        """Build prompt for fix generation"""
        
        return f"""You are an expert software engineer generating a code fix.

Bug Summary: {bug_info.get('summary', 'Unknown')}
Root Cause: {root_cause.get('root_cause', 'Unknown')}

Affected Code:
{affected_code}

Generate a fix for this bug. Provide:
1. Fixed Code: The corrected code
2. Explanation: What was changed and why
3. Testing Notes: How to verify the fix works

Format your response clearly with sections."""
    
    def process(
        self,
        bug_info: Dict[str, Any],
        root_cause: Dict[str, Any],
        affected_code: str
    ) -> Dict[str, Any]:
        """
        Generate code fix
        
        Args:
            bug_info: Structured bug information
            root_cause: Root cause analysis
            affected_code: Code that needs fixing
            
        Returns:
            Generated fix
        """
        prompt = self.build_prompt(bug_info, root_cause, affected_code)
        response = self.generate_with_retry(prompt)
        
        if not response:
            return {
                "suggested_fix": "Unable to generate fix",
                "explanation": "Fix generation failed",
                "confidence": "low"
            }
        
        return {
            "suggested_fix": response,
            "explanation": response,
            "confidence": "medium"
        }

# Made with Bob
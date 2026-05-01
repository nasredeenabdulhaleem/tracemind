"""Test Generator Agent - Generates regression tests"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent


class TestGeneratorAgent(BaseAgent):
    """Agent for generating regression tests"""
    
    def __init__(self):
        super().__init__(model_id="ibm/granite-20b-code-instruct")
    
    def build_prompt(
        self,
        bug_info: Dict[str, Any],
        fixed_code: str,
        language: str = "python"
    ) -> str:
        """Build prompt for test generation"""
        
        test_framework = "pytest" if language == "python" else "jest"
        
        return f"""You are an expert software engineer writing regression tests.

Bug Summary: {bug_info.get('summary', 'Unknown')}
Language: {language}
Test Framework: {test_framework}

Fixed Code:
{fixed_code}

Generate a comprehensive regression test that:
1. Tests the bug scenario to ensure it's fixed
2. Tests edge cases related to the bug
3. Includes clear test descriptions
4. Uses appropriate assertions

Provide complete, runnable test code."""
    
    def process(
        self,
        bug_info: Dict[str, Any],
        fixed_code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Generate regression test
        
        Args:
            bug_info: Structured bug information
            fixed_code: The fixed code
            language: Programming language
            
        Returns:
            Generated test code
        """
        prompt = self.build_prompt(bug_info, fixed_code, language)
        response = self.generate_with_retry(prompt)
        
        if not response:
            return {
                "generated_test": "# Unable to generate test",
                "test_framework": "pytest" if language == "python" else "jest",
                "confidence": "low"
            }
        
        return {
            "generated_test": response,
            "test_framework": "pytest" if language == "python" else "jest",
            "language": language,
            "confidence": "medium"
        }

# Made with Bob
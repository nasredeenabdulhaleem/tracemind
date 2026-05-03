"""Test Generator Agent - Generates regression tests"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams


class TestGeneratorAgent(BaseAgent):
    """Agent for generating regression tests"""
    
    def __init__(self):
        params = {
            GenParams.MAX_NEW_TOKENS: 2048,
            GenParams.TEMPERATURE: 0.2,
            GenParams.TOP_P: 0.9,
        }
        super().__init__(model_id="meta-llama/llama-3-3-70b-instruct", params=params)
    
    def build_prompt(
        self,
        bug_info: Dict[str, Any],
        fixed_code: str,
        language: str = "python"
    ) -> str:
        """Build prompt for test generation"""
        test_framework = "pytest" if language == "python" else "jest"
        if len(fixed_code) > 2000:
            fixed_code = fixed_code[:2000] + "\n# ... (truncated)"

        return f"""You are an expert software engineer writing regression tests.

Bug Fixed: {bug_info.get('summary', 'Unknown')}
Language: {language}
Framework: {test_framework}

Fixed Code:
```{language}
{fixed_code}
```

Write a complete, runnable regression test file using {test_framework} that:
1. Tests the exact bug scenario to prove it is fixed
2. Tests relevant edge cases
3. Uses descriptive test function names
4. Includes only code — no prose, no markdown, no explanations

Output only the test code:"""
    
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

        framework = "pytest" if language == "python" else "jest"

        if not response:
            return {
                "generated_test": f"# Unable to generate test — AI agent did not return a response.",
                "test_framework": framework,
                "confidence": "low",
            }

        # Strip any markdown code fences the model might add
        code = response.strip()
        for fence in [f"```{language}", "```python", "```javascript", "```typescript", "```"]:
            if code.startswith(fence):
                code = code[len(fence):]
                break
        if code.endswith("```"):
            code = code[:-3]

        return {
            "generated_test": code.strip(),
            "test_framework": framework,
            "language": language,
            "confidence": "high",
        }

# Made with Bob
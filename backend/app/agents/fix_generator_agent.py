"""Fix Generator Agent - Generates code fixes for bugs"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams


class FixGeneratorAgent(BaseAgent):
    """Agent for generating code fixes"""
    
    def __init__(self):
        params = {
            GenParams.MAX_NEW_TOKENS: 2048,
            GenParams.TEMPERATURE: 0.3,
            GenParams.TOP_P: 0.9,
        }
        super().__init__(model_id="meta-llama/llama-3-3-70b-instruct", params=params)
    
    def build_prompt(
        self,
        bug_info: Dict[str, Any],
        root_cause: Dict[str, Any],
        affected_code: str
    ) -> str:
        """Build prompt for fix generation"""
        root_cause_text = root_cause.get('root_cause', 'Unknown')
        # Trim to prevent context overflow
        if len(root_cause_text) > 800:
            root_cause_text = root_cause_text[:800] + "..."
        if len(affected_code) > 2000:
            affected_code = affected_code[:2000] + "\n# ... (truncated)"

        return f"""You are an expert software engineer. Analyze this bug and generate a complete fix.

Bug Summary: {bug_info.get('summary', 'Unknown')}
Bug Type: {bug_info.get('bug_type', 'unknown')}
Root Cause: {root_cause_text}

Affected Code:
```
{affected_code}
```

Respond using EXACTLY these four section headers (no extra text before or between sections):

##FIXED_CODE##
[The complete corrected code]

##EXPLANATION##
[Technical explanation of what changed and why]

##SIMPLE_EXPLANATION##
[2-3 sentences in plain English that a non-programmer can understand]

##TESTING_NOTES##
[How to verify the fix works]"""

    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse sectioned response into a dictionary."""
        sections = {
            "fixed_code": "",
            "explanation": "",
            "simple_explanation": "",
            "testing_notes": "",
        }
        markers = {
            "##FIXED_CODE##": "fixed_code",
            "##EXPLANATION##": "explanation",
            "##SIMPLE_EXPLANATION##": "simple_explanation",
            "##TESTING_NOTES##": "testing_notes",
        }
        current_key = None
        buffer = []
        for line in response.splitlines():
            stripped = line.strip()
            if stripped in markers:
                if current_key and buffer:
                    sections[current_key] = "\n".join(buffer).strip()
                current_key = markers[stripped]
                buffer = []
            else:
                if current_key:
                    buffer.append(line)
        if current_key and buffer:
            sections[current_key] = "\n".join(buffer).strip()
        return sections

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
                "explanation": "Fix generation failed — AI agent did not return a response.",
                "simple_explanation": "The AI was unable to generate a fix at this time. Try again with a more detailed bug description.",
                "confidence": "low",
            }

        parsed = self._parse_response(response)

        # Fall back to full response if parsing missed sections
        fix_code = parsed["fixed_code"] or response
        explanation = parsed["explanation"] or response
        simple = parsed["simple_explanation"] or "See the technical explanation above."

        return {
            "suggested_fix": fix_code,
            "explanation": explanation,
            "simple_explanation": simple,
            "testing_notes": parsed["testing_notes"],
            "confidence": "high",
        }

# Made with Bob
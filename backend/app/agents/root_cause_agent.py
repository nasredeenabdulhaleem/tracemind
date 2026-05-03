"""Root Cause Agent - Analyzes code to identify bug root cause"""

from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent


class RootCauseAgent(BaseAgent):
    """Agent for identifying root cause of bugs"""
    
    def __init__(self):
        super().__init__(model_id="meta-llama/llama-3-3-70b-instruct")
    
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

Analyze the code and identify the root cause of the bug.

Respond using EXACTLY these four section headers:

##ROOT_CAUSE##
[Clear technical explanation of what is causing the bug]

##AFFECTED_CODE##
[Specific file names and line numbers involved]

##WHY_IT_HAPPENS##
[Detailed technical explanation of the mechanism]

##SIMPLE_EXPLANATION##
[2-3 sentences in plain English for a non-programmer]"""
    
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
                "simple_explanation": "The AI was unable to determine the root cause. Try providing more context in your bug description.",
                "confidence": "low",
            }

        parsed = self._parse_response(response)

        # Build a combined markdown root cause for display
        root_cause_md = ""
        if parsed["root_cause"]:
            root_cause_md += f"## Root Cause\n{parsed['root_cause']}\n\n"
        if parsed["affected_code"]:
            root_cause_md += f"## Affected Code\n{parsed['affected_code']}\n\n"
        if parsed["why_it_happens"]:
            root_cause_md += f"## Why It Happens\n{parsed['why_it_happens']}"
        if not root_cause_md:
            root_cause_md = response

        return {
            "root_cause": root_cause_md,
            "affected_files": [chunk["file_path"] for chunk in code_chunks],
            "explanation": parsed["why_it_happens"] or response,
            "simple_explanation": parsed["simple_explanation"] or "",
            "confidence": "high",
        }

    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse sectioned response into a dictionary."""
        sections = {
            "root_cause": "",
            "affected_code": "",
            "why_it_happens": "",
            "simple_explanation": "",
        }
        markers = {
            "##ROOT_CAUSE##": "root_cause",
            "##AFFECTED_CODE##": "affected_code",
            "##WHY_IT_HAPPENS##": "why_it_happens",
            "##SIMPLE_EXPLANATION##": "simple_explanation",
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

# Made with Bob
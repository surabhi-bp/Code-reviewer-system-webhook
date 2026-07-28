"""
Filename: app/services/ai_engine.py
Description: AI Review Engine service orchestrating the parsing and verification of code patches.
"""

import re
import json
from typing import List, Dict
from app.services.ai.base import AIProvider

class AIEngineService:
    """Service coordinates AI-driven code reviews and structures output findings."""

    def analyze_code(self, file_path: str, patch_content: str, provider: AIProvider) -> List[Dict]:
        """
        Analyze code patch using the given AI Provider strategy.
        
        Args:
            file_path: The file path being reviewed.
            patch_content: The patch content lines.
            provider: The AIProvider strategy implementation.
            
        Returns:
            List[Dict]: Parsed list of issues (keys: category, severity, line_number, message).
        """
        prompt = self._build_prompt(file_path, patch_content)
        
        try:
            raw_response = provider.analyze(prompt)
        except Exception:
            return []
            
        return self._parse_response(raw_response)

    def _build_prompt(self, file_path: str, patch_content: str) -> str:
        """Construct the prompt layout instructing the AI provider output structure."""
        return f"""You are a professional automated code auditor.
Analyze the following code changes for file '{file_path}'.

Check for bugs, security vulnerabilities, lint/style problems, and performance issues.

Response schema constraints:
Return your response exclusively as a JSON array of objects wrapped in a markdown ```json and ``` block.
Each object in the array MUST strictly have these keys:
- "category": Type of issue ('bug', 'security', 'lint', 'performance')
- "severity": Severity level ('low', 'medium', 'high', 'critical')
- "line_number": The specific file line number where the issue occurs
- "message": A clear explanation of the issue and suggested fix

Example:
```json
[
  {{
    "category": "security",
    "severity": "high",
    "line_number": 42,
    "message": "Prevent SQL injection by parameterized statements."
  }}
]
```

Here are the code changes to analyze:
{patch_content}
"""

    def _parse_response(self, raw_response: str) -> List[Dict]:
        """Extract the JSON block from response markdown wrapper and load it safely."""
        if not raw_response:
            return []
            
        # Try extracting standard ```json ... ``` markdown block
        json_pattern = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)
        match = json_pattern.search(raw_response)
        
        json_str = ""
        if match:
            json_str = match.group(1).strip()
        else:
            # Fallback 1: Simple string partitioning if markdown markers are slightly modified
            if "```json" in raw_response:
                try:
                    json_str = raw_response.split("```json")[1].split("```")[0].strip()
                except IndexError:
                    pass
            # Fallback 2: Use raw response directly
            if not json_str:
                json_str = raw_response.strip()
                
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass
            
        return []

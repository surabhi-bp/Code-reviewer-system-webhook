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
        return f"""You are a strict, highly critical Senior Staff Engineer conducting an uncompromising code review.
Your job is to thoroughly inspect code patches and flag every bug, defect, language misuse, or security risk.

File under review: '{file_path}'

CODE PATCH TO REVIEW:
```diff
{patch_content}
```

CORE CHECKS YOU MUST ENFORCE:

Language-Specific Syntax & API Errors: Flag syntax errors or invalid function calls for the target language (e.g., using C-style printf("...") in a Python file instead of print(...)).

Security Vulnerabilities: Flag SQL injections, XSS, command injection, path traversal, hardcoded credentials, API keys, or secret tokens.

Bad Architectural Practices & Anti-Patterns: Flag poor error handling, unhandled edge cases, resource leaks, and severe performance degradation.

STRICT OUTPUT FORMAT RULES:

Respond ONLY with a valid JSON array of issue objects wrapped in a markdown ```json ... ``` code block.

DO NOT include any conversational filler, introductory prose, notes, or explanations outside the JSON block.

If NO defects, bugs, or security risks are found, you MUST respond with an empty JSON array: [].

Each object in the array MUST contain exactly these keys:

"category": String ('bug', 'security', 'lint', 'performance')

"severity": String ('low', 'medium', 'high', 'critical')

"line_number": Integer (the line number in the patch/file where the issue occurs)

"message": String (clear explanation of the issue and suggested fix)

EXAMPLE REQUIREMENT:
If reviewing a Python file with printf("hello"):

```json
[
  {{
    "category": "bug",
    "severity": "high",
    "line_number": 10,
    "message": "Syntax/API Error: C-style `printf` used in Python. Replace with `print(\"hello\")`."
  }}
]
```"""

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

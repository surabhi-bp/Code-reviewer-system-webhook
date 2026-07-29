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

        print(f"\n=== DEBUG: PATCH SENT TO GEMINI ===\n{patch_content}\n===================================\n")
        
        try:
            raw_response = provider.analyze(prompt)
            print(f"\n=== DEBUG: RAW GEMINI RESPONSE ===\n{raw_response}\n==================================\n")
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

        cleaned_text = raw_response.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        try:
            parsed = json.loads(cleaned_text)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

        # Secondary fallback: Extract array [ ... ] via regex if LLM included outer explanation
        json_pattern = re.compile(r"\[\s*\{.*\}\s*\]", re.DOTALL)
        match = json_pattern.search(cleaned_text)
        if match:
            try:
                parsed = json.loads(match.group(0).strip())
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass

        return []

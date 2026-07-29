# AI Review Engine and Code Parser Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Code Parser Service, Strategy Pattern AI Providers (Ollama), and the AI Review Engine Service.

**Architecture:** Use Strategy Pattern for extensible AI backends, a unified diff parser using regex, and robust extraction for markdown-wrapped JSON payloads.

**Tech Stack:** Python, Flask, requests, unittest.mock, pytest.

## Global Constraints
* No hardcoded secrets. Always read from `current_app.config`.
* Thin Controllers: Do not place AI/requests inference logic in Flask routes/controllers.
* Strictly follow PEP-8 and include type hints and docstrings.
* Mock all external network calls in unit tests.

---

### Task 1: Code Parser Service

**Files:**
- Create: `app/services/code_parser.py`
- Create: `tests/test_code_parser.py`

**Interfaces:**
- Produces: `CodeParserService.parse_diff(raw_diff: str) -> list[dict]`

- [ ] **Step 1: Write tests for CodeParserService**

Create `tests/test_code_parser.py`:
```python
import pytest
from app.services.code_parser import CodeParserService

def test_parse_diff_single_file():
    diff_text = """diff --git a/app/main.py b/app/main.py
index 1234567..89abcde 100644
--- a/app/main.py
+++ b/app/main.py
@@ -1,3 +1,4 @@
 def hello():
-    return "world"
+    return "hello world"
"""
    parser = CodeParserService()
    results = parser.parse_diff(diff_text)
    assert len(results) == 1
    assert results[0]["file_path"] == "app/main.py"
    assert "def hello():" in results[0]["patch"]

def test_parse_diff_empty_or_malformed():
    parser = CodeParserService()
    assert parser.parse_diff("") == []
    assert parser.parse_diff("hello world") == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_code_parser.py`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

Create `app/services/code_parser.py`:
```python
"""
Filename: app/services/code_parser.py
Description: Service for parsing unified git diff content into file-by-file patches.
"""

import re
from typing import List, Dict

class CodeParserService:
    """Service to parse raw git diffs and extract file patches."""

    def parse_diff(self, raw_diff: str) -> List[Dict[str, str]]:
        """
        Parse a unified git diff into a list of file paths and patch details.
        
        Args:
            raw_diff: Raw unified diff content as a string.
            
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing 'file_path' and 'patch' keys.
        """
        if not raw_diff:
            return []
            
        parsed_files: List[Dict[str, str]] = []
        current_file: str = ""
        current_patch_lines: List[str] = []
        
        # Split raw_diff into lines
        lines = raw_diff.splitlines()
        
        for line in lines:
            # Detect file headers
            if line.startswith("+++ b/"):
                # If there's an ongoing file, save it
                if current_file and current_patch_lines:
                    parsed_files.append({
                        "file_path": current_file,
                        "patch": "\n".join(current_patch_lines)
                    })
                current_file = line[6:]
                current_patch_lines = []
            elif line.startswith("+++ "):
                # Fallback check for paths that may not start with b/
                if current_file and current_patch_lines:
                    parsed_files.append({
                        "file_path": current_file,
                        "patch": "\n".join(current_patch_lines)
                    })
                current_file = line[4:]
                current_patch_lines = []
            elif line.startswith("--- ") or line.startswith("diff ") or line.startswith("index "):
                # Skip diff header metadata lines
                continue
            else:
                # If we've started tracking a file, accumulate lines
                if current_file:
                    current_patch_lines.append(line)
                    
        # Append final file if it exists
        if current_file and current_patch_lines:
            parsed_files.append({
                "file_path": current_file,
                "patch": "\n".join(current_patch_lines)
            })
            
        return parsed_files
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_code_parser.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/code_parser.py tests/test_code_parser.py
git commit -m "feat(services): implement CodeParserService and unit tests"
```

---

### Task 2: Extensible AI Providers (Strategy Pattern)

**Files:**
- Create: `app/services/ai/__init__.py`
- Create: `app/services/ai/base.py`
- Create: `app/services/ai/ollama_provider.py`
- Modify: `tests/test_ai_engine.py` (add provider checks)

**Interfaces:**
- Produces: Abstract class `AIProvider` with `analyze(prompt: str) -> str`
- Produces: Concrete class `OllamaProvider(AIProvider)`

- [ ] **Step 1: Write test for OllamaProvider**

Create/Modify `tests/test_ai_engine.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.services.ai.ollama_provider import OllamaProvider

def test_ollama_provider_success():
    app = Flask("test_app")
    app.config["OLLAMA_BASE_URL"] = "http://localhost:11434"
    app.config["MODEL_NAME"] = "codellama:python"
    
    with app.app_context():
        provider = OllamaProvider()
        
        with patch("app.services.ai.ollama_provider.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = MagicMock(return_value={"response": "llm output code here"})
            mock_post.return_value = mock_response
            
            res = provider.analyze("hello prompt")
            assert res == "llm output code here"
            mock_post.assert_called_once_with(
                "http://localhost:11434/api/generate",
                json={
                    "model": "codellama:python",
                    "prompt": "hello prompt",
                    "stream": False
                },
                timeout=60
            )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ai_engine.py`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

Create `app/services/ai/__init__.py` (empty file).

Create `app/services/ai/base.py`:
```python
"""
Filename: app/services/ai/base.py
Description: Abstract Base Class for AI Provider Strategy.
"""

from abc import ABC, abstractmethod

class AIProvider(ABC):
    """Abstract class defining interface for AI completion/generation providers."""

    @abstractmethod
    def analyze(self, prompt: str) -> str:
        """
        Analyze the given prompt and return the model's text response.
        
        Args:
            prompt: Formatted prompt text for the AI.
            
        Returns:
            str: Raw textual output from the model.
        """
        pass
```

Create `app/services/ai/ollama_provider.py`:
```python
"""
Filename: app/services/ai/ollama_provider.py
Description: Ollama concrete implementation of the AIProvider Strategy.
"""

import requests
from flask import current_app
from app.services.ai.base import AIProvider

class OllamaProvider(AIProvider):
    """Concrete provider strategy for communicating with a local Ollama server."""

    def analyze(self, prompt: str) -> str:
        """
        Generate analysis using the local Ollama daemon.
        
        Args:
            prompt: Structured request prompt.
            
        Returns:
            str: Raw text generated by Ollama.
        """
        base_url = current_app.config.get("OLLAMA_BASE_URL", "http://localhost:11434")
        model = current_app.config.get("MODEL_NAME", "codellama:python")
        
        url = f"{base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API request failed: {str(e)}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ai_engine.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/ai/tests/test_ai_engine.py
git commit -m "feat(ai-provider): implement Strategy base and OllamaProvider strategy"
```

---

### Task 3: AI Engine Service

**Files:**
- Create: `app/services/ai_engine.py`
- Modify: `tests/test_ai_engine.py` (add AIEngineService checks)

**Interfaces:**
- Consumes: `AIProvider.analyze(prompt: str) -> str`
- Produces: `AIEngineService.analyze_code(file_path: str, patch_content: str, provider: AIProvider) -> list[dict]`

- [ ] **Step 1: Write test for AIEngineService**

Append tests to `tests/test_ai_engine.py`:
```python
import json
from app.services.ai_engine import AIEngineService
from app.services.ai.base import AIProvider

class MockProvider(AIProvider):
    def __init__(self, response_text: str):
        self.response_text = response_text
    def analyze(self, prompt: str) -> str:
        return self.response_text

def test_ai_engine_parse_markdown_json():
    mock_json = [
        {
            "category": "security",
            "severity": "high",
            "line_number": 5,
            "message": "Vulnerability warning"
        }
    ]
    response_text = f"Here is the feedback:\n```json\n{json.dumps(mock_json)}\n```\nEnd of output."
    provider = MockProvider(response_text)
    
    engine = AIEngineService()
    results = engine.analyze_code("main.py", "patch info here", provider)
    
    assert len(results) == 1
    assert results[0]["category"] == "security"
    assert results[0]["message"] == "Vulnerability warning"

def test_ai_engine_parse_fallback_raw_json():
    mock_json = [
        {
            "category": "performance",
            "severity": "medium",
            "line_number": 12,
            "message": "Optimize query"
        }
    ]
    provider = MockProvider(json.dumps(mock_json))
    
    engine = AIEngineService()
    results = engine.analyze_code("db.py", "patch info here", provider)
    
    assert len(results) == 1
    assert results[0]["category"] == "performance"

def test_ai_engine_parse_failure_returns_empty():
    provider = MockProvider("Invalid unstructured output that is not JSON at all")
    engine = AIEngineService()
    results = engine.analyze_code("db.py", "patch info here", provider)
    assert results == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_ai_engine.py`
Expected: FAIL (AIEngineService import error)

- [ ] **Step 3: Write minimal implementation**

Create `app/services/ai_engine.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_ai_engine.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/services/ai_engine.py tests/test_ai_engine.py
git commit -m "feat(ai-engine): implement AIEngineService and JSON extraction parser"
```

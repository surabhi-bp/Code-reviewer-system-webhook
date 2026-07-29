# Design Specification: AI Review Engine and Code Parser Service

This document outlines the architecture and implementation details for the Code Parser and Strategy-based AI Provider services.

## 1. Code Parser Service (`app/services/code_parser.py`)
Parses raw git diff strings to identify files and their corresponding hunks/patches.

### Specifications
* **Class**: `CodeParserService`
* **Method**: `parse_diff(raw_diff: str) -> list[dict]`
* **Expected Output Format**:
  ```python
  [
      {
          "file_path": "app/utils/security.py",
          "patch": "@@ -1,3 +1,4 @@\n..."
      }
  ]
  ```
* **Parsing Strategy**:
  1. Scan line-by-line.
  2. Detect files via target marker: `+++ b/` (indicating the new file path).
  3. When a new file is detected, aggregate all subsequent lines until the next file header starts.
  4. Only include files with valid patch hunks (starting with `@@`).

---

## 2. Strategy Pattern AI Provider Module (`app/services/ai/`)
Creates an extensible abstraction layer for different AI backends.

### Abstract Base Provider (`app/services/ai/base.py`)
* **Class**: `AIProvider(abc.ABC)`
* **Abstract Method**: `analyze(self, prompt: str) -> str`

### Ollama Provider (`app/services/ai/ollama_provider.py`)
* **Class**: `OllamaProvider(AIProvider)`
* **Inputs**: Constructor parameters or dynamic retrieval of settings from `current_app.config`.
* **API Details**:
  - URL: `{OLLAMA_BASE_URL}/api/generate`
  - Payload:
    ```json
    {
      "model": "model-name",
      "prompt": "prompt-string",
      "stream": false
    }
    ```
  - Headers: `Content-Type: application/json`

---

## 3. AI Engine Service (`app/services/ai_engine.py`)
Orchestrates the prompt construction, LLM provider query, and JSON parsing.

### Specifications
* **Class**: `AIEngineService`
* **Method**: `analyze_code(file_path: str, patch_content: str, provider: AIProvider) -> list[dict]`
* **Prompt Construction**:
  - System instructions: Wrap output inside a ` ```json ... ``` ` markdown block.
  - JSON schema detail: List of objects containing `category`, `severity`, `line_number`, and `message`.
* **JSON Extraction & Fallbacks**:
  - Regex: `r"```json\s*(.*?)\s*```"` with `re.DOTALL`.
  - Fallback 1: Extract block using simple string partition or split if regex fails.
  - Fallback 2: Parse raw string if no markdown block exists.
  - Fallback 3: Return empty list `[]` on parsing failures.

---

## 4. Verification Plan
* Unit tests in `tests/test_code_parser.py` covering various diff cases.
* Unit tests in `tests/test_ai_engine.py` mocking Ollama REST responses and validating extraction parsing logic.

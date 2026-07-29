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

def test_ai_engine_build_prompt_contains_patch_content():
    engine = AIEngineService()
    file_path = "app/main.py"
    patch_content = "+ print('hello world')"
    prompt = engine._build_prompt(file_path, patch_content)
    
    assert patch_content in prompt
    assert file_path in prompt
    assert "Senior Staff Engineer" in prompt
    assert "CORE CHECKS YOU MUST ENFORCE:" in prompt
    assert "STRICT OUTPUT FORMAT RULES:" in prompt

def test_ai_engine_parse_empty_array_json():
    provider = MockProvider("```json\n[]\n```")
    engine = AIEngineService()
    results = engine.analyze_code("clean.py", "patch info here", provider)
    assert results == []



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

import os
import pytest
from unittest.mock import patch, MagicMock
from app.services.ai.gemini_provider import GeminiProvider

def test_gemini_provider_init():
    with patch("google.generativeai.configure") as mock_configure, \
         patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
        provider = GeminiProvider(model_name="gemini-1.5-flash")
        mock_configure.assert_called_once_with(api_key="test-api-key")
        assert provider.model_name == "gemini-1.5-flash"

def test_gemini_provider_analyze_success():
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated code review"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model_instance

        provider = GeminiProvider()
        result = provider.analyze("Test prompt")

        assert result == "Generated code review"
        mock_model_cls.assert_called_once_with("gemini-1.5-flash")
        mock_model_instance.generate_content.assert_called_once_with("Test prompt")

def test_gemini_provider_analyze_empty_response():
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = None
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model_instance

        provider = GeminiProvider()
        result = provider.analyze("Test prompt")

        assert result == ""

def test_gemini_provider_generate_alias():
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Alias result"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_cls.return_value = mock_model_instance

        provider = GeminiProvider()
        result = provider.generate("Test prompt")

        assert result == "Alias result"
        mock_model_instance.generate_content.assert_called_once_with("Test prompt")

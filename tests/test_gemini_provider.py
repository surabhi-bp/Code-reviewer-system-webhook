import os
import pytest
from unittest.mock import patch, MagicMock
from app.services.ai.gemini_provider import GeminiProvider


def test_gemini_provider_init():
    with patch("google.genai.Client") as mock_client_cls, \
         patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
        mock_client_instance = MagicMock()
        mock_client_cls.return_value = mock_client_instance
        provider = GeminiProvider(model_name="gemini-2.5-flash")
        assert provider.model_name == "gemini-2.5-flash"
        provider.analyze("test")
        mock_client_cls.assert_called_once_with(api_key="test-api-key")
        mock_client_instance.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash",
            contents="test"
        )


def test_gemini_provider_analyze_success():
    with patch("google.genai.Client") as mock_client_cls, \
         patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Generated code review"
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client_instance

        provider = GeminiProvider()
        result = provider.analyze("Test prompt")

        assert result == "Generated code review"
        mock_client_cls.assert_called_once_with(api_key="test-api-key")
        mock_client_instance.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash",
            contents="Test prompt"
        )


def test_gemini_provider_analyze_empty_response():
    with patch("google.genai.Client") as mock_client_cls, \
         patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = None
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client_instance

        provider = GeminiProvider()
        result = provider.analyze("Test prompt")

        assert result == ""


def test_gemini_provider_generate_alias():
    with patch("google.genai.Client") as mock_client_cls, \
         patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Alias result"
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client_instance

        provider = GeminiProvider()
        result = provider.generate("Test prompt")

        assert result == "Alias result"
        mock_client_instance.models.generate_content.assert_called_once_with(
            model="gemini-2.5-flash",
            contents="Test prompt"
        )


def test_gemini_provider_no_api_key():
    with patch("google.genai.Client") as mock_client_cls, \
         patch.dict(os.environ, {}, clear=True):
        mock_client_instance = MagicMock()
        mock_client_cls.return_value = mock_client_instance

        provider = GeminiProvider()
        provider.analyze("Test prompt")

        mock_client_cls.assert_called_once_with()

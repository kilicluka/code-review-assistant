"""Tests for llm_client module."""

import pytest

from agent.llm_client import LLMProvider, create_client


class TestLLMProvider:
    def test_supported_returns_implemented_providers(self):
        supported = LLMProvider.supported()

        assert LLMProvider.ANTHROPIC in supported
        assert LLMProvider.OPENAI in supported
        assert LLMProvider.GEMINI not in supported

    def test_is_supported_for_implemented_providers(self):
        assert LLMProvider.is_supported(LLMProvider.ANTHROPIC) is True
        assert LLMProvider.is_supported(LLMProvider.OPENAI) is True

    def test_is_supported_for_unimplemented_providers(self):
        assert LLMProvider.is_supported(LLMProvider.GEMINI) is False

    def test_enum_values(self):
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.GEMINI.value == "gemini"


class TestCreateClient:
    def test_creates_anthropic_client(self):
        client = create_client(
            LLMProvider.ANTHROPIC,
            api_key="test-key",
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
        )

        assert client is not None
        assert hasattr(client, "chat")

    def test_creates_openai_client(self):
        client = create_client(
            LLMProvider.OPENAI,
            api_key="test-key",
            model="gpt-4o",
            max_tokens=1000,
        )

        assert client is not None
        assert hasattr(client, "chat")

    def test_raises_for_unsupported_provider(self):
        with pytest.raises(ValueError) as exc_info:
            create_client(
                LLMProvider.GEMINI,
                api_key="test-key",
                model="gemini-pro",
                max_tokens=1000,
            )

        assert "not yet implemented" in str(exc_info.value)
        assert "gemini" in str(exc_info.value)

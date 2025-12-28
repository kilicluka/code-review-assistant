"""Tests for reviewer module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from agent.reviewer import CodeReviewer


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = Mock()
    client.chat.return_value = "This is a mock review response."
    return client


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "main.py").write_text("print('hello')")
        (root / "utils.py").write_text("def helper(): pass")
        yield str(root)


class TestCodeReviewer:
    def test_review_calls_llm(self, mock_llm_client, temp_codebase):
        reviewer = CodeReviewer(temp_codebase, mock_llm_client)

        response = reviewer.review("Review this code")

        assert response == "This is a mock review response."
        assert mock_llm_client.chat.called

    def test_review_with_filter(self, mock_llm_client, temp_codebase):
        reviewer = CodeReviewer(temp_codebase, mock_llm_client)

        response = reviewer.review("Review", filter_pattern="main")

        assert response == "This is a mock review response."

    def test_review_no_files_found(self, mock_llm_client, temp_codebase):
        reviewer = CodeReviewer(temp_codebase, mock_llm_client)

        response = reviewer.review("Review", filter_pattern="nonexistent")

        assert "No source files found" in response
        assert not mock_llm_client.chat.called

    def test_ask_calls_llm(self, mock_llm_client, temp_codebase):
        reviewer = CodeReviewer(temp_codebase, mock_llm_client)

        response = reviewer.ask("What is this code doing?")

        assert response == "This is a mock review response."
        assert mock_llm_client.chat.called

    def test_conversation_history_maintained(self, mock_llm_client, temp_codebase):
        reviewer = CodeReviewer(temp_codebase, mock_llm_client)

        reviewer.ask("First question")
        reviewer.ask("Second question")

        # 2 user messages + 2 assistant messages
        assert len(reviewer.conversation_history) == 4

    def test_clear_history(self, mock_llm_client, temp_codebase):
        reviewer = CodeReviewer(temp_codebase, mock_llm_client)
        reviewer.ask("A question")

        reviewer.clear_history()

        assert len(reviewer.conversation_history) == 0

    def test_get_summary(self, mock_llm_client, temp_codebase):
        reviewer = CodeReviewer(temp_codebase, mock_llm_client)

        summary = reviewer.get_summary()

        assert "Found 2 source files" in summary

"""Integration tests for main CLI."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from main import main


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "main.py").write_text("print('hello')")
        (root / "auth").mkdir()
        (root / "auth" / "login.py").write_text("def login(): pass")
        yield str(root)


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = Mock()
    client.chat.return_value = "Mock review response."
    return client


class TestMainIntegration:
    def test_review_command(self, temp_codebase, mock_llm_client):
        """Test that 'review' command triggers LLM call."""
        user_inputs = iter(["review", "exit"])

        with (
            patch("main.input", side_effect=user_inputs),
            patch("main.create_client", return_value=mock_llm_client),
            patch("main.LLM_API_KEY", "test-key"),
            patch("sys.argv", ["main.py", temp_codebase]),
        ):
            main()

        assert mock_llm_client.chat.called

    def test_review_with_filter(self, temp_codebase, mock_llm_client):
        """Test that 'review --filter' only includes matching files."""
        user_inputs = iter(["review --filter auth", "exit"])

        with (
            patch("main.input", side_effect=user_inputs),
            patch("main.create_client", return_value=mock_llm_client),
            patch("main.LLM_API_KEY", "test-key"),
            patch("sys.argv", ["main.py", temp_codebase]),
        ):
            main()

        call_args = mock_llm_client.chat.call_args
        prompt_content = str(call_args)
        assert "login.py" in prompt_content
        assert "main.py" not in prompt_content

    def test_exit_command(self, temp_codebase, mock_llm_client, capsys):
        """Test that 'exit' command exits gracefully."""
        user_inputs = iter(["exit"])

        with (
            patch("main.input", side_effect=user_inputs),
            patch("main.create_client", return_value=mock_llm_client),
            patch("main.LLM_API_KEY", "test-key"),
            patch("sys.argv", ["main.py", temp_codebase]),
        ):
            main()

        captured = capsys.readouterr()
        assert "Goodbye!" in captured.out

    def test_help_command(self, temp_codebase, mock_llm_client, capsys):
        """Test that 'help' command shows help text."""
        user_inputs = iter(["help", "exit"])

        with (
            patch("main.input", side_effect=user_inputs),
            patch("main.create_client", return_value=mock_llm_client),
            patch("main.LLM_API_KEY", "test-key"),
            patch("sys.argv", ["main.py", temp_codebase]),
        ):
            main()

        captured = capsys.readouterr()
        assert "Available commands:" in captured.out

    def test_summary_command(self, temp_codebase, mock_llm_client, capsys):
        """Test that 'summary' command shows file summary."""
        user_inputs = iter(["summary", "exit"])

        with (
            patch("main.input", side_effect=user_inputs),
            patch("main.create_client", return_value=mock_llm_client),
            patch("main.LLM_API_KEY", "test-key"),
            patch("sys.argv", ["main.py", temp_codebase]),
        ):
            main()

        captured = capsys.readouterr()
        assert "Found 2 source files" in captured.out

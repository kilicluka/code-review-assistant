"""Tests for file_loader module."""

import tempfile
from pathlib import Path

import pytest

from agent.file_loader import (
    format_files_for_prompt,
    get_codebase_summary,
    load_codebase,
)


@pytest.fixture
def temp_codebase():
    """Create a temporary codebase structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        (root / "main.py").write_text("print('hello')")
        (root / "utils.py").write_text("def helper(): pass")

        (root / "auth").mkdir()
        (root / "auth" / "login.py").write_text("def login(): pass")
        (root / "auth" / "logout.py").write_text("def logout(): pass")

        (root / "script.js").write_text("console.log('test');")

        # Create a file that should be ignored (wrong extension)
        (root / "notes.txt").write_text("some notes")

        yield root


class TestLoadCodebase:
    def test_loads_all_source_files(self, temp_codebase):
        files = load_codebase(str(temp_codebase))

        assert len(files) == 5
        assert "main.py" in files
        assert "utils.py" in files
        assert "script.js" in files
        assert "notes.txt" not in files

    def test_filter_pattern_matches_directory(self, temp_codebase):
        files = load_codebase(str(temp_codebase), filter_pattern="auth")

        assert len(files) == 2
        for path in files:
            assert "auth" in path.lower()

    def test_filter_pattern_matches_filename(self, temp_codebase):
        files = load_codebase(str(temp_codebase), filter_pattern="login")
        file_paths = files.keys()

        assert len(files) == 1
        for path in file_paths:
            assert "auth" in path.lower()
            assert "login" in path.lower()

    def test_filter_pattern_case_insensitive(self, temp_codebase):
        files = load_codebase(str(temp_codebase), filter_pattern="AUTH")

        assert len(files) == 2

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = load_codebase(tmpdir)
            assert files == {}

    def test_no_matching_filter(self, temp_codebase):
        files = load_codebase(str(temp_codebase), filter_pattern="nonexistent")

        assert files == {}


class TestFormatFilesForPrompt:
    def test_formats_single_file(self):
        files = {"main.py": "print('hello')"}
        result = format_files_for_prompt(files)

        assert "=== main.py ===" in result
        assert "print('hello')" in result

    def test_formats_multiple_files(self):
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
        }
        result = format_files_for_prompt(files)

        assert "=== main.py ===" in result
        assert "=== utils.py ===" in result
        assert "print('hello')" in result
        assert "def helper(): pass" in result

    def test_empty_files_dict(self):
        result = format_files_for_prompt({})

        assert result == "(No files found)"


class TestGetCodebaseSummary:
    def test_summarizes_codebase(self, temp_codebase):
        summary = get_codebase_summary(str(temp_codebase))

        assert "Found 5 source files" in summary
        assert ".py: 4 files" in summary
        assert ".js: 1 files" in summary

    def test_empty_codebase(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = get_codebase_summary(tmpdir)
            assert "Found 0 source files" in summary

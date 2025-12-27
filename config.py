"""
Configuration for the Code Review Assistant.
"""

import os

# LLM Configuration
LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL", "claude-sonnet-4-20250514")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic")
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "8192"))

# File Processing Configuration
SUPPORTED_EXTENSIONS = [
    ".py",  # Python
    ".js",  # JavaScript
    ".ts",  # TypeScript
    ".jsx",  # React JSX
    ".tsx",  # React TSX
    ".java",  # Java
    ".go",  # Go
    ".rb",  # Ruby
    ".rs",  # Rust
    ".c",  # C
    ".cpp",  # C++
    ".h",  # C/C++ headers
]

# Directories to skip during traversal
IGNORED_DIRECTORIES = [
    "__pycache__",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    ".next",
    "target",
    ".pytest_cache",
    ".mypy_cache",
]

# File size limits (in characters)
MAX_FILE_SIZE = 50_000  # Skip files larger than this
MAX_TOTAL_CONTEXT = 100_000  # Warn if total context exceeds this

# Traversal safety limits
MAX_DEPTH = 20  # Maximum directory nesting depth
MAX_FILES = 500  # Maximum number of files to process

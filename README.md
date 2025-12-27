# Code Review Assistant

An AI-powered CLI tool for automated code review.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export LLM_API_KEY='your-anthropic-api-key'

# Run the assistant
python main.py /path/to/your/codebase
```

## Configuration

All configuration is via environment variables:

| Variable         | Default                    | Description                            |
|------------------|----------------------------|----------------------------------------|
| `LLM_API_KEY`    | (required)                 | API key for the LLM provider           |
| `LLM_MODEL`      | `claude-sonnet-4-20250514` | Model to use                           |
| `LLM_PROVIDER`   | `anthropic`                | LLM provider (`anthropic` or `openai`) |
| `LLM_MAX_TOKENS` | `8192`                     | Maximum tokens for LLM responses       |

## Usage

```bash
# Using Anthropic (default)
python main.py /path/to/project

# Using a different Anthropic model
python main.py /path/to/project --model claude-opus-4-20250514

# Using OpenAI
python main.py /path/to/project --provider openai --model gpt-4o
```

**CLI flags:**

| Flag         | Description                                                                                   |
|--------------|-----------------------------------------------------------------------------------------------|
| `--provider` | LLM provider (`anthropic` or `openai`). Overrides `LLM_PROVIDER` env var.                     |
| `--model`    | Model identifier (e.g., `claude-sonnet-4-20250514`, `gpt-4o`). Overrides `LLM_MODEL` env var. |

**Interactive commands:**

```
You: review                         # Review entire codebase
You: review --filter auth           # Review files matching 'auth'
You: review --filter src/utils/     # Review specific folder

You: How should I fix that issue?   # Follow-up question (no file reload)
You: What's wrong with this code?   # Ask about pasted snippets
    <paste code here>

You: summary                        # Show codebase structure
You: clear                          # Clear conversation history
You: help                           # Show available commands
You: exit                           # Exit
```

## Design Decisions

### Architecture

The assistant follows a modular design with clear separation of concerns:

- **`llm_client.py`**: Protocol-based abstraction for LLM providers. New providers can be added by implementing the
  `LLMClient` protocol and updating the `create_client` factory.
- **`file_loader.py`**: Handles file system traversal with safety limits (max depth, max files, symlink skipping).
- **`reviewer.py`**: Core logic that combines file loading with LLM calls. Maintains conversation history for follow-up
  questions.
- **`main.py`**: CLI entry point using argparse. Routes between `review` (loads files) and `ask` (uses existing
  context).

Dependency injection is used for the LLM client, making testing and provider swapping straightforward.

### LLM Selection

Supports both **Anthropic Claude** and **OpenAI GPT** models. Claude Sonnet is the default due to strong code
understanding and reasonable cost. Users can switch via `--provider openai` flag.

### Code Analysis Strategy

Simple file traversal approach: read all matching files, concatenate, send to LLM. This works well for small-to-medium
projects that fit within context limits.

**Trade-offs:**

- ✅ Simple, no preprocessing required
- ✅ LLM sees full context, can identify cross-file issues
- ❌ Doesn't scale to very large codebases
- ❌ No semantic understanding of code structure

For production, consider embedding-based retrieval or AST parsing (see Future Improvements).

### Prompt Engineering

The system prompt instructs the LLM to evaluate code across five dimensions: security, performance, code quality,
maintainability, and best practices. Key guidelines:

- Reference specific files and line numbers
- Prioritize high-impact issues
- Be constructive, suggest fixes
- Acknowledge good patterns

## Future Improvements

### LLM Provider Rotation / Fallback

Currently the assistant uses a single LLM provider. A production system could implement automatic fallback:

- Detect rate limits or API errors
- Rotate to backup providers (OpenAI, Google, open-source models)
- Track usage across providers to optimize cost

This would require:

- Multiple API keys configured
- Retry logic with provider rotation
- Rate limit tracking per provider

### Embedding-based Code Retrieval

For large codebases that exceed context limits:

- Chunk code into semantic units
- Create embeddings for each chunk
- Use vector similarity to retrieve relevant code for each query
- Only send relevant chunks to the LLM

### AST-based Analysis

Parse code into Abstract Syntax Trees to:

- Extract function/class signatures for a "map" of the codebase
- Enable more targeted analysis (e.g., "review all functions that handle user input")
- Detect patterns without sending full code to LLM

## Security Considerations

**Path Traversal**: The tool reads files from a user-specified directory. Since this is a local CLI tool, the user
already has access to any files they point it at. Symlinks are skipped to prevent escaping the target directory during
traversal. For a web service deployment, additional path boundary validation would be recommended.

**API Keys**: Keys are read from environment variables, not stored in code.

## Known Limitations

- **Context limits**: Large codebases may exceed LLM context window
- **No caching**: Each request re-reads files and calls the LLM
- **Basic filtering**: Path-based file filtering only, not semantic

## Project Structure

```
code-review-assistant/
├── main.py                  # CLI entry point
├── config.py                # Configuration (env vars)
├── requirements.txt         # Dependencies
├── pyproject.toml           # Ruff configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
├── .python-version          # Python version (pyenv)
├── .gitignore
├── README.md
└── agent/
    ├── __init__.py
    ├── reviewer.py          # Core review logic
    ├── file_loader.py       # File traversal and loading
    ├── prompts.py           # Prompt templates
    └── llm_client.py        # LLM abstraction layer
```

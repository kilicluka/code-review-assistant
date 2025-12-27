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

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_KEY` | (required) | API key for the LLM provider |
| `LLM_MODEL` | `claude-sonnet-4-20250514` | Model to use |
| `LLM_PROVIDER` | `anthropic` | LLM provider (currently only anthropic) |

## Usage

```
You: Review this project
You: What could be improved in the auth module?
You: Are there any security issues?
You: help
You: exit
```

## Design Decisions

### Architecture

TODO: Document architecture choices

### LLM Selection

TODO: Document why Claude/Anthropic

### Code Analysis Strategy

TODO: Document file traversal approach and tradeoffs

### Prompt Engineering

TODO: Document prompt design

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

## Known Limitations

- **Context limits**: Large codebases may exceed LLM context window
- **Single provider**: Currently only supports Anthropic
- **No caching**: Each request re-reads files and calls the LLM
- **Basic filtering**: Keyword-based file filtering, not semantic

## Project Structure

```
code-review-assistant/
├── main.py              # CLI entry point
├── config.py            # Configuration (env vars)
├── agent/
│   ├── reviewer.py      # Core review logic
│   ├── file_loader.py   # File traversal and loading
│   ├── prompts.py       # Prompt templates
│   └── llm_client.py    # LLM abstraction layer
├── requirements.txt
└── README.md
```

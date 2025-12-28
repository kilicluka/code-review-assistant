"""
Code Review Assistant - CLI Entry Point

An AI-powered tool for automated code review.
"""

import argparse
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from agent.llm_client import LLMProvider, create_client
from agent.reviewer import CodeReviewer
from config import LLM_API_KEY, LLM_MAX_TOKENS, LLM_MODEL, LLM_PROVIDER


@dataclass
class ReviewSession:
    """Configuration and state for an active review session."""

    reviewer: CodeReviewer
    provider: LLMProvider
    codebase_path: Path
    model: str


class Command(StrEnum):
    """Available CLI commands."""

    EXIT = "exit"
    QUIT = "quit"
    HELP = "help"
    SUMMARY = "summary"
    CLEAR = "clear"
    REVIEW = "review"


def main() -> None:
    """Main entry point."""
    args = _parse_args()
    session = _create_session(args)
    _run_interactive_session(session)


def _parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-powered code review assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py /path/to/project
  python main.py /path/to/project --provider anthropic
  python main.py /path/to/project --provider openai --model gpt-4o
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        help="Path to the codebase to review",
    )

    parser.add_argument(
        "--provider",
        choices=[p.value for p in LLMProvider],
        default=LLM_PROVIDER,
        help=f"LLM provider to use (default: {LLM_PROVIDER})",
    )

    parser.add_argument(
        "--model",
        default=LLM_MODEL,
        help=f"Model to use (default: {LLM_MODEL})",
    )

    return parser.parse_args()


def _create_session(args: argparse.Namespace) -> ReviewSession:
    """
    Set up and return a configured review session.

    Validates configuration, creates LLM client, and initializes the reviewer.
    """
    if not LLM_API_KEY:
        print("Error: LLM_API_KEY environment variable not set.")
        print("Please set it with: export LLM_API_KEY='your-api-key'")
        sys.exit(1)

    if args.path:
        codebase_path = args.path
    else:
        codebase_path = input("Enter path to codebase to review: ").strip()

    path = Path(codebase_path).resolve()
    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        sys.exit(1)
    if not path.is_dir():
        print(f"Error: Path is not a directory: {path}")
        sys.exit(1)

    try:
        provider = LLMProvider(args.provider)
        llm_client = create_client(
            provider, api_key=LLM_API_KEY, model=args.model, max_tokens=LLM_MAX_TOKENS
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    reviewer = CodeReviewer(str(path), llm_client)
    return ReviewSession(
        reviewer=reviewer,
        provider=provider,
        codebase_path=path,
        model=args.model,
    )


def _run_interactive_session(session: ReviewSession) -> None:
    """Run the main CLI interaction loop."""
    print("\nCode Review Assistant")
    print(f"Provider: {session.provider.value} | Model: {session.model}")
    print(f"Codebase: {session.codebase_path}\n")
    print(session.reviewer.get_summary())
    print("\nType 'help' for available commands, or ask me to review your code.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        command_str = user_input.lower()

        if command_str in (Command.EXIT, Command.QUIT):
            print("Goodbye!")
            break

        if command_str == Command.HELP:
            _print_help()
            continue

        if command_str == Command.SUMMARY:
            print(session.reviewer.get_summary())
            continue

        if command_str == Command.CLEAR:
            session.reviewer.clear_history()
            print("Conversation history cleared.")
            continue

        if command_str.startswith(Command.REVIEW):
            query, filter_pattern = _parse_review_command(user_input)

            if filter_pattern:
                print(f"\nAnalyzing files matching '{filter_pattern}'...\n")
            else:
                print("\nAnalyzing code...\n")

            response = session.reviewer.review(query, filter_pattern)
        else:
            print("\nThinking...\n")
            response = session.reviewer.ask(user_input)

        print(f"Assistant:\n{response}\n")


def _parse_review_command(user_input: str) -> tuple[str, str | None]:
    """
    Parse user input for review command and optional filter.

    Supports:
      "review" or "Review this project" -> (query, None)
      "review --filter auth" -> ("review", "auth")
      "review --filter auth/ Check security" -> ("review Check security", "auth/")

    Returns (query, filter_pattern).
    """
    if "--filter" not in user_input:
        return user_input, None

    parts = user_input.split("--filter", 1)
    before_filter = parts[0].strip()
    after_filter = parts[1].strip()

    filter_parts = after_filter.split(maxsplit=1)
    filter_pattern = filter_parts[0] if filter_parts else None
    remaining_query = filter_parts[1] if len(filter_parts) > 1 else ""

    query = f"{before_filter} {remaining_query}".strip()
    return query, filter_pattern


def _print_help() -> None:
    """Print available commands."""
    print(
        """
Available commands:
  help          - Show this help message
  summary       - Show codebase structure summary
  clear         - Clear conversation history
  exit / quit   - Exit the assistant

To review code (loads files from codebase):
  review                         - Review entire codebase
  review --filter auth           - Review files matching 'auth'
  review --filter src/utils/     - Review files in specific folder

For follow-up questions (uses existing context):
  How should I fix the SQL injection?
  Can you explain the auth flow?
  What's wrong with this code? <paste snippet>
"""
    )


if __name__ == "__main__":
    main()

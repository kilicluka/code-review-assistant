"""
Core code review logic for the Code Review Assistant.
"""

from agent.file_loader import (
    format_files_for_prompt,
    get_codebase_summary,
    load_codebase,
)
from agent.llm_client import ChatMessage, LLMClient
from agent.prompts import SYSTEM_PROMPT, build_review_prompt
from config import MAX_TOTAL_CONTEXT


class CodeReviewer:
    """Main code review agent that analyzes codebases using an LLM."""

    def __init__(self, codebase_path: str, llm_client: LLMClient):
        """
        Initialize the reviewer with a path to the codebase.

        Args:
            codebase_path: Path to the directory containing source code
            llm_client: LLM client to use for generating reviews
        """
        self.codebase_path = codebase_path
        self.client = llm_client
        self.conversation_history: list[ChatMessage] = []

    def review(self, user_query: str, filter_pattern: str | None = None) -> str:
        """
        Perform a code review based on the user's query.

        Args:
            user_query: The user's review request or question
            filter_pattern: Optional pattern to filter which files to include

        Returns:
            The LLM's review response
        """
        files = load_codebase(self.codebase_path, filter_pattern)

        if not files:
            return (
                "No source files found matching your criteria. Try a different filter "
                "or check the path."
            )

        code_context = format_files_for_prompt(files)

        if len(code_context) > MAX_TOTAL_CONTEXT:
            file_count = len(files)
            return (
                f"Warning: The selected files ({file_count} files, "
                f"{len(code_context):,} characters) "
                f"exceed the recommended context size. Please use a filter to narrow "
                f"down the files.\n\n"
                f"Example: 'Review the auth module' or 'Focus on the utils folder'"
            )

        user_prompt = build_review_prompt(code_context, user_query)

        self.conversation_history.append({"role": "user", "content": user_prompt})
        assistant_message = self.client.chat(SYSTEM_PROMPT, self.conversation_history)
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )

        return assistant_message

    def ask(self, question: str) -> str:
        """
        Ask a question or send an ad-hoc query without reloading files.

        Uses existing conversation history for context (if any). Useful for:
        - Follow-up questions about a previous review
        - Asking about code snippets pasted by the user
        - General coding questions

        Args:
            question: The user's question

        Returns:
            The LLM's response
        """
        self.conversation_history.append({"role": "user", "content": question})
        assistant_message = self.client.chat(SYSTEM_PROMPT, self.conversation_history)
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )

        return assistant_message

    def get_summary(self) -> str:
        """Get a summary of the codebase structure."""
        return get_codebase_summary(self.codebase_path)

    def clear_history(self) -> None:
        """Clear conversation history to start fresh."""
        self.conversation_history = []

#!/usr/bin/env python3
"""
AstraChat: Interactive Terminal Chat Client.

Fixed Hygiene Issues:
1. Environment Variable Key Name: Replaced broken `os.getenv("")` with
   explicit `os.getenv("COARENA_API_KEY")` and `os.getenv("OPENAI_API_KEY")` fallbacks.
2. Location Hygiene: Lives at project root (outside ephemeral `venv/`), preventing
   loss upon virtual environment rebuilds.
3. Context / Token Trimming: Implemented sliding-window message history trimming
   (`trim_context()`) to prevent HTTP 400 Context Length Exceeded on long sessions,
   while retaining the original system prompt and `messages.pop()` rollback on API error.
4. Proxy Base URL Hygiene: Parameterized `base_url` through `COARENA_BASE_URL` with
   graceful fallback and `.env` loading via `python-dotenv`.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration & Environment Key Hygiene ---
COARENA_API_KEY = os.getenv("COARENA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_KEY = COARENA_API_KEY or OPENAI_API_KEY

BASE_URL = os.getenv("COARENA_BASE_URL", "https://coarena.ai/api/v1")
DEFAULT_MODEL = os.getenv("COARENA_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "10"))  # Keeps last 10 turns (20 messages)
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are Astra, an intelligent, helpful, and concise AI assistant.",
)


def get_client():
    """Initialize OpenAI client with validated credentials and proxy base_url."""
    try:
        from openai import OpenAI
    except ImportError:
        print("\n[Error] The 'openai' package is required.")
        print("Please install it via:\n  pip install openai python-dotenv\n")
        sys.exit(1)

    if not API_KEY:
        print("\n[Error] API key not found.")
        print("Please set COARENA_API_KEY or OPENAI_API_KEY in your .env file or environment.")
        print("Example:\n  COARENA_API_KEY=coarena_sk_...\n  COARENA_BASE_URL=https://coarena.ai/api/v1\n")
        sys.exit(1)

    return OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL if BASE_URL else None,
    )


def trim_context(
    messages: List[Dict[str, str]],
    max_turns: int = MAX_HISTORY_TURNS,
) -> List[Dict[str, str]]:
    """Trim conversation history using a sliding window to prevent context overflow (HTTP 400).

    Preserves the initial system prompt (if present) and retains the most recent
    `max_turns` conversational exchanges (user + assistant pairs).
    """
    if not messages:
        return []

    system_msgs = [m for m in messages if m.get("role") == "system"]
    dialogue_msgs = [m for m in messages if m.get("role") != "system"]

    max_messages = max_turns * 2
    if len(dialogue_msgs) > max_messages:
        dialogue_msgs = dialogue_msgs[-max_messages:]

    return system_msgs + dialogue_msgs


def main() -> None:
    """Run interactive terminal chat loop."""
    print("=" * 60)
    print("AstraChat — Interactive AI Terminal Client")
    print(f"Endpoint: {BASE_URL}")
    print(f"Model:    {DEFAULT_MODEL}")
    print("Type 'exit', 'quit', or ':q' to leave | 'clear' to reset history")
    print("=" * 60)

    client = get_client()

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user_input = input("\nYou > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting AstraChat. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", ":q"):
            print("Goodbye!")
            break

        if user_input.lower() in ("clear", "reset"):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("[Conversation history cleared]")
            continue

        # Add user message
        messages.append({"role": "user", "content": user_input})

        # Apply context trimming before API dispatch to avoid 400 context length errors
        trimmed_payload = trim_context(messages, max_turns=MAX_HISTORY_TURNS)

        try:
            print("\nAstra > ", end="", flush=True)
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=trimmed_payload,
                stream=True,
            )

            assistant_reply_chunks: List[str] = []
            for chunk in response:
                content = chunk.choices[0].delta.content if chunk.choices else None
                if content:
                    assistant_reply_chunks.append(content)
                    print(content, end="", flush=True)
            print()

            full_reply = "".join(assistant_reply_chunks)
            messages.append({"role": "assistant", "content": full_reply})

        except Exception as exc:
            # Revert the user message from history on failure so the state remains consistent
            if messages and messages[-1].get("role") == "user":
                messages.pop()
            print(f"\n[API Error]: {exc}")
            print("[Tip]: Verify network connection, base_url, or check token balance.")


if __name__ == "__main__":
    main()

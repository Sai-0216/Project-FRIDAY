"""
Project FRIDAY
Console Debug Filter

Normal mode hides development/debug chatter while keeping
real errors and important output visible.

Set FRIDAY_DEBUG=1 before starting FRIDAY to show everything.
"""

import builtins
import os


DEBUG = os.getenv(
    "FRIDAY_DEBUG",
    "0"
).strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)


_HIDDEN_EXACT = {
    "No command matched.",
    "No command matched.",
}

_HIDDEN_PREFIXES = (
    "You: ",
    "Normalized: ",
    "Command received:",
    "Calling Ollama...",
    "Returned from Ollama",
    "Raw Response:",
    "Parsed Intent:",
    "Direct ",
    "Detected Intent:",
    "Dispatcher Response:",
    "Sending response to speaker...",
    "Prefix: ",
    "Argument: ",
    "SPEAKER RECEIVED:",
    "Using microphone:",
    "🎤 ",
    "Recognizing...",
    "[AI] ",
    "[BRAIN] ",
    "[Speech] TTS attempt ",
    "[Speech] TTS audio created.",
    "Workflows loaded from:",
    "[FRIDAY] 20 plugins loaded.",
    "pygame ",
    "Hello from the pygame community.",
    "Confirmation heard:",
)


_original_print = builtins.print


def _should_hide(first_value):

    if DEBUG:

        return False

    text = str(
        first_value
    ).strip()

    if text in _HIDDEN_EXACT:

        return True

    return any(
        text.startswith(prefix)
        for prefix in _HIDDEN_PREFIXES
    )


def _filtered_print(
    *args,
    **kwargs
):

    if args and _should_hide(args[0]):

        return

    _original_print(
        *args,
        **kwargs
    )


def install():

    if DEBUG:

        _original_print(
            "[FRIDAY] Debug console enabled."
        )

    builtins.print = _filtered_print

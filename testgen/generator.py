"""Calls Claude to turn a user story or API spec into a structured test suite."""

import anthropic

from .models import TestSuite

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = """You are a senior QA engineer. Given a user story, requirement or API spec, \
design a test suite a manual or automation tester could execute directly.

Cover, where relevant:
- every stated acceptance criterion with at least one positive case
- negative cases: invalid, missing and boundary inputs
- edge cases: limits, empty states, concurrency, retries, timeouts
- security: authentication, authorization, injection, sensitive data exposure
- usability and performance only when the story implies them

Make steps concrete and executable, and use realistic test data values. \
Prefer fewer, sharper cases over many overlapping ones. Do not invent requirements: \
when the story is silent, record an assumption or an open question instead."""


class GenerationError(RuntimeError):
    pass


def generate_test_suite(
    requirement: str,
    *,
    effort: str = "medium",
    client: anthropic.Anthropic | None = None,
) -> TestSuite:
    client = client or anthropic.Anthropic()

    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        output_config={"effort": effort},
        messages=[{"role": "user", "content": f"<requirement>\n{requirement}\n</requirement>"}],
        output_format=TestSuite,
    )

    if response.stop_reason == "refusal":
        raise GenerationError("Claude declined to generate tests for this input.")
    if response.stop_reason == "max_tokens":
        raise GenerationError("Output was cut off. Try splitting the requirement into smaller stories.")
    if response.parsed_output is None:
        raise GenerationError(f"No structured output returned (stop_reason={response.stop_reason}).")

    return response.parsed_output

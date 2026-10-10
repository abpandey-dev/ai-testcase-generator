"""Command-line entry point: python -m testgen <story-file> [--format md|csv|json] [--out FILE]"""

import argparse
import sys
from pathlib import Path

import anthropic

from .exporters import EXPORTERS
from .generator import GenerationError, generate_test_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="testgen", description="Generate structured test cases from a user story or API spec using Claude."
    )
    parser.add_argument("input", help="Path to a text/markdown file with the requirement, or '-' for stdin")
    parser.add_argument("-f", "--format", choices=EXPORTERS, default="md", help="Output format (default: md)")
    parser.add_argument("-o", "--out", help="Write to this file instead of stdout")
    parser.add_argument(
        "--effort",
        choices=["low", "medium", "high", "xhigh", "max"],
        default="medium",
        help="How hard Claude thinks; higher is more thorough but slower and costlier (default: medium)",
    )
    args = parser.parse_args(argv)

    requirement = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    if not requirement.strip():
        parser.error("input is empty")

    print(f"Generating test cases with effort={args.effort}...", file=sys.stderr)
    try:
        suite = generate_test_suite(requirement, effort=args.effort)
    except GenerationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except anthropic.AuthenticationError:
        print("Error: no valid API key. Set ANTHROPIC_API_KEY (see README).", file=sys.stderr)
        return 1
    except anthropic.RateLimitError:
        print("Error: rate limited by the API. Wait a moment and retry.", file=sys.stderr)
        return 1
    except anthropic.APIConnectionError:
        print("Error: could not reach the Anthropic API. Check your connection.", file=sys.stderr)
        return 1
    except anthropic.APIStatusError as e:
        print(f"Error: API returned {e.status_code}: {e.message}", file=sys.stderr)
        return 1

    output = EXPORTERS[args.format](suite)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Wrote {len(suite.test_cases)} test cases to {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Render a TestSuite as Markdown, CSV or JSON."""

import csv
import io

from .models import TestSuite


def to_json(suite: TestSuite) -> str:
    return suite.model_dump_json(indent=2)


def to_csv(suite: TestSuite) -> str:
    """One row per test case, with steps on separate lines inside a cell (imports cleanly into Zephyr, Xray or Excel)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["ID", "Title", "Category", "Priority", "Preconditions", "Steps", "Test Data", "Expected Result", "Covers"]
    )
    for tc in suite.test_cases:
        writer.writerow(
            [
                tc.id,
                tc.title,
                tc.category,
                tc.priority,
                "\n".join(tc.preconditions),
                "\n".join(f"{i}. {s}" for i, s in enumerate(tc.steps, 1)),
                "\n".join(tc.test_data),
                tc.expected_result,
                tc.acceptance_criterion,
            ]
        )
    return buf.getvalue()


def to_markdown(suite: TestSuite) -> str:
    lines = [f"# Test Suite: {suite.feature}", "", suite.summary, ""]

    counts: dict[str, int] = {}
    for tc in suite.test_cases:
        counts[tc.category] = counts.get(tc.category, 0) + 1
    lines += ["| Category | Cases |", "|---|---|"]
    lines += [f"| {cat} | {n} |" for cat, n in sorted(counts.items())]
    lines += [f"| **Total** | **{len(suite.test_cases)}** |", ""]

    for tc in suite.test_cases:
        lines += [f"## {tc.id}: {tc.title}", "", f"**Category:** {tc.category} · **Priority:** {tc.priority}", ""]
        if tc.preconditions:
            lines += ["**Preconditions**", ""] + [f"- {p}" for p in tc.preconditions] + [""]
        lines += ["**Steps**", ""] + [f"{i}. {s}" for i, s in enumerate(tc.steps, 1)] + [""]
        if tc.test_data:
            lines += ["**Test data**", ""] + [f"- `{d}`" for d in tc.test_data] + [""]
        lines += [f"**Expected result:** {tc.expected_result}", "", f"**Covers:** {tc.acceptance_criterion}", ""]

    if suite.assumptions:
        lines += ["## Assumptions", ""] + [f"- {a}" for a in suite.assumptions] + [""]
    if suite.open_questions:
        lines += ["## Open questions", ""] + [f"- {q}" for q in suite.open_questions] + [""]
    return "\n".join(lines)


EXPORTERS = {"md": to_markdown, "csv": to_csv, "json": to_json}

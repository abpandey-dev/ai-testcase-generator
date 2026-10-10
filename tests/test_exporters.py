"""Offline tests: exporters and CLI wiring, with the Claude call stubbed out."""

import csv
import io
import json

import pytest

from testgen import cli
from testgen.exporters import to_csv, to_json, to_markdown
from testgen.models import TestCase, TestSuite


@pytest.fixture
def suite() -> TestSuite:
    return TestSuite(
        feature="Login with OTP",
        summary="Covers OTP delivery, expiry and lockout.",
        test_cases=[
            TestCase(
                id="TC-001",
                title="Valid OTP logs the user in",
                category="positive",
                priority="P0",
                preconditions=["User is registered"],
                steps=["Enter email", "Tap Send OTP", "Enter the OTP"],
                test_data=["user@example.com"],
                expected_result="Dashboard opens",
                acceptance_criterion="AC3",
            ),
            TestCase(
                id="TC-002",
                title="Account locks after 3 wrong OTPs",
                category="negative",
                priority="P1",
                preconditions=[],
                steps=["Enter a wrong OTP three times"],
                test_data=["000000"],
                expected_result="Account locked for 15 minutes",
                acceptance_criterion="AC4",
            ),
        ],
        assumptions=["OTP is numeric only"],
        open_questions=["Is the lockout per device or per account?"],
    )


def test_markdown_has_summary_cases_and_questions(suite):
    md = to_markdown(suite)
    assert md.startswith("# Test Suite: Login with OTP")
    assert "| **Total** | **2** |" in md
    assert "## TC-002: Account locks after 3 wrong OTPs" in md
    assert "1. Enter email\n2. Tap Send OTP\n3. Enter the OTP" in md
    assert "Is the lockout per device or per account?" in md


def test_csv_has_one_row_per_case_with_numbered_steps(suite):
    rows = list(csv.reader(io.StringIO(to_csv(suite))))
    assert rows[0][0] == "ID"
    assert len(rows) == 3
    assert rows[1][5] == "1. Enter email\n2. Tap Send OTP\n3. Enter the OTP"


def test_json_round_trips(suite):
    assert TestSuite.model_validate(json.loads(to_json(suite))) == suite


def test_cli_writes_requested_format(tmp_path, monkeypatch, suite):
    story = tmp_path / "story.md"
    story.write_text("As a user I want to log in")
    out = tmp_path / "out.csv"
    monkeypatch.setattr(cli, "generate_test_suite", lambda text, effort: suite)

    assert cli.main([str(story), "--format", "csv", "--out", str(out)]) == 0
    assert out.read_text().startswith("ID,Title")


def test_cli_rejects_empty_input(tmp_path):
    story = tmp_path / "empty.md"
    story.write_text("   ")
    with pytest.raises(SystemExit):
        cli.main([str(story)])

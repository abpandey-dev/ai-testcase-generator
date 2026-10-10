"""Schema for generated test suites. Claude's output is validated against these models."""

from typing import List, Literal

from pydantic import BaseModel, Field

Category = Literal["positive", "negative", "edge", "security", "usability", "performance"]
Priority = Literal["P0", "P1", "P2", "P3"]


class TestCase(BaseModel):
    __test__ = False  # stop pytest collecting this as a test class

    id: str = Field(description="Stable ID such as TC-001")
    title: str = Field(description="Short, specific name of what is being verified")
    category: Category
    priority: Priority = Field(description="P0 = release blocker, P3 = nice to have")
    preconditions: List[str]
    steps: List[str] = Field(description="Numbered-order actions a tester performs")
    test_data: List[str] = Field(description="Concrete input values used by the steps")
    expected_result: str
    acceptance_criterion: str = Field(
        description="The acceptance criterion this case covers, or 'implicit' if none was stated"
    )


class TestSuite(BaseModel):
    __test__ = False

    feature: str
    summary: str = Field(description="Two or three sentences on what the suite covers and why")
    test_cases: List[TestCase]
    assumptions: List[str] = Field(description="Things assumed because the story did not say")
    open_questions: List[str] = Field(description="Gaps or ambiguities to raise with the product owner")

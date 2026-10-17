"""Unit tests for the grading rules in the assignment."""

import pytest

from grades import average, grade


@pytest.mark.parametrize(
    ("score", "expected"),
    [(100, "A"), (80, "A"), (79, "B"), (70, "B"), (69, "C"), (60, "C"), (50, "D"), (49, "F"), (0, "F")],
)
def test_grade_boundaries(score: int, expected: str) -> None:
    assert grade(score) == expected


@pytest.mark.parametrize("score", [-1, 101])
def test_grade_rejects_out_of_range_scores(score: int) -> None:
    with pytest.raises(ValueError, match="between 0 and 100"):
        grade(score)


@pytest.mark.parametrize(
    ("scores", "expected"),
    [([80], 80.0), ([80, 70], 75.0), ([80, 81, 82], 81.0), ([100, 0, 0], 33.33)],
)
def test_average(scores: list[int], expected: float) -> None:
    assert average(scores) == expected


def test_average_rejects_empty_list() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        average([])

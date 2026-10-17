"""Small, reusable functions for the sample grade report."""


def grade(score: int) -> str:
    """Return the letter grade for a score from 0 to 100."""
    if not 0 <= score <= 100:
        raise ValueError("score must be between 0 and 100")
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def average(scores: list[int]) -> float:
    """Return the average score, rounded to two decimal places."""
    if not scores:
        raise ValueError("scores must not be empty")
    return round(sum(scores) / len(scores), 2)

"""Assessment scoring.

Computes a percentage score from a candidate's saved responses against the
assessment's questions. Only objectively gradable question types (currently
multiple-choice with a defined `correct_answer`) count toward the score.
Assessments with no gradable questions (e.g. personality/Likert scales) return
None, leaving the score unset rather than fabricating a number.
"""
from typing import Any, Iterable, Optional


def _extract_answer(value: Any) -> Any:
    """Responses are stored as JSON; accept a few common shapes."""
    if isinstance(value, dict):
        for key in ("answer", "value", "selected"):
            if key in value:
                return value[key]
        return None
    return value


def score_assessment(questions: Optional[list], responses: Iterable) -> Optional[float]:
    resp_map = {}
    for r in responses:
        resp_map[str(r.question_id)] = _extract_answer(r.response)

    gradable = 0
    correct = 0
    for q in questions or []:
        if not isinstance(q, dict):
            continue
        qtype = str(q.get("type", "")).lower()
        correct_answer = q.get("correct_answer")
        if qtype == "mcq" and correct_answer is not None:
            gradable += 1
            given = resp_map.get(str(q.get("id")))
            if given is not None and str(given).strip() == str(correct_answer).strip():
                correct += 1

    if gradable == 0:
        return None
    return round(correct / gradable * 100, 2)

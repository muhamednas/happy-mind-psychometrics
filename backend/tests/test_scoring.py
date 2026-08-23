from types import SimpleNamespace
from app.services.scoring import score_assessment


def _resp(question_id, answer):
    return SimpleNamespace(question_id=question_id, response={"answer": answer})


QUESTIONS = [
    {"id": "q1", "type": "mcq", "correct_answer": "30"},
    {"id": "q2", "type": "mcq", "correct_answer": "12"},
    {"id": "q3", "type": "open"},  # not gradable
]


def test_all_correct():
    responses = [_resp("q1", "30"), _resp("q2", "12"), _resp("q3", "essay")]
    assert score_assessment(QUESTIONS, responses) == 100.0


def test_half_correct():
    responses = [_resp("q1", "30"), _resp("q2", "11")]
    assert score_assessment(QUESTIONS, responses) == 50.0


def test_none_correct():
    responses = [_resp("q1", "1"), _resp("q2", "2")]
    assert score_assessment(QUESTIONS, responses) == 0.0


def test_no_gradable_questions_returns_none():
    questions = [{"id": "q1", "type": "likert"}, {"id": "q2", "type": "open"}]
    assert score_assessment(questions, [_resp("q1", 5)]) is None


def test_missing_answer_counts_wrong():
    responses = [_resp("q1", "30")]  # q2 unanswered
    assert score_assessment(QUESTIONS, responses) == 50.0

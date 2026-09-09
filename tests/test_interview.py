"""Guided fill-in for one catalog table. Not a symptom checker."""

from src.interview import next_interview_step


def test_headache_does_not_become_a_pain_scale() -> None:
    step = next_interview_step("heart_uci_pooled", {}, last_text="I have a headache")
    assert "1-10" in step["notice"]
    assert step["field"] == "age"
    assert step["kind"] == "number"


def test_heart_chest_pain_is_type_not_ten_point_pain() -> None:
    step = next_interview_step("heart_uci_pooled", {"age": 54, "sex": 1})
    assert step["field"] == "cp"
    assert step["kind"] == "choice"
    values = {item["value"] for item in step["choices"]}
    assert values == {0, 1, 2, 3}


def test_interview_advances_after_an_answer() -> None:
    step = next_interview_step("pima", {"Pregnancies": 2})
    assert step["field"] == "Glucose"
    assert step["filled_count"] == 1
    assert step["can_score"] is False

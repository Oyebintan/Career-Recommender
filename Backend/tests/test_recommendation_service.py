import pytest

from services.recommendation_service import RecommendationService


@pytest.fixture()
def engine():
    return RecommendationService()


def test_calculate_scores_sums_weighted_answers(engine):
    scores = engine.calculate_scores({1: 5, 2: 5})
    assert scores  # at least one career matched these questions
    assert all(isinstance(v, (int, float)) for v in scores.values())


def test_calculate_scores_empty_answers_returns_empty(engine):
    assert engine.calculate_scores({}) == {}


def test_normalize_scores_scales_top_score_to_100(engine):
    normalized = engine.normalize_scores({"A": 10, "B": 5, "C": 2})
    assert normalized["A"] == 100.0
    assert normalized["B"] == 50.0
    assert normalized["C"] == 20.0


def test_normalize_scores_handles_empty_input(engine):
    assert engine.normalize_scores({}) == {}


def test_normalize_scores_handles_all_zero_scores(engine):
    normalized = engine.normalize_scores({"A": 0, "B": 0})
    assert normalized == {"A": 0.0, "B": 0.0}


def test_get_top_careers_returns_sorted_results(engine):
    sample_answers = {1: 5, 2: 5, 9: 5, 10: 5, 11: 5, 12: 5, 4: 1, 5: 1, 17: 1}
    results = engine.get_top_careers(sample_answers, top_n=3)

    assert len(results) <= 3
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)
    for career, score in results:
        assert isinstance(career, str)
        assert 0 <= score <= 100


def test_get_top_careers_respects_top_n(engine):
    sample_answers = {1: 5, 2: 5, 9: 5, 10: 5}
    results = engine.get_top_careers(sample_answers, top_n=1)
    assert len(results) <= 1


def test_get_top_careers_no_answers_returns_empty(engine):
    assert engine.get_top_careers({}) == []

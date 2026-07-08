import pytest

from services.skill_gap_service import SkillGapService


@pytest.fixture()
def engine():
    return SkillGapService()


def test_get_required_skills_for_known_career(engine):
    skills = engine.get_required_skills("Software Engineer")
    assert "Python" in skills
    assert skills == sorted(skills)


def test_get_required_skills_for_unknown_career_is_empty(engine):
    assert engine.get_required_skills("Not A Real Career") == []


def test_analyze_skill_gap_exact_case_match(engine):
    result = engine.analyze_skill_gap("Software Engineer", ["Python", "Git", "SQL"])
    assert "Python" not in result["missing_skills"]
    assert "Git" not in result["missing_skills"]
    assert "SQL" not in result["missing_skills"]


def test_analyze_skill_gap_is_case_insensitive(engine):
    # Regression test: users naturally type skills in lowercase (or any
    # casing) and should still get credit for skills they already have.
    result = engine.analyze_skill_gap("Software Engineer", ["python", "GIT", "sql"])
    assert "Python" not in result["missing_skills"]
    assert "Git" not in result["missing_skills"]
    assert "SQL" not in result["missing_skills"]
    assert result["readiness_score"] > 0


def test_analyze_skill_gap_readiness_score_full_match(engine):
    required = engine.get_required_skills("Software Engineer")
    result = engine.analyze_skill_gap("Software Engineer", required)
    assert result["missing_skills"] == []
    assert result["readiness_score"] == 100.0


def test_analyze_skill_gap_readiness_score_no_match(engine):
    result = engine.analyze_skill_gap("Software Engineer", ["Nonexistent Skill"])
    required = engine.get_required_skills("Software Engineer")
    assert result["missing_skills"] == required
    assert result["readiness_score"] == 0.0


def test_analyze_skill_gap_unknown_career_has_zero_readiness(engine):
    result = engine.analyze_skill_gap("Not A Real Career", ["Python"])
    assert result["required_skills"] == []
    assert result["missing_skills"] == []
    assert result["readiness_score"] == 0.0


def test_analyze_skill_gap_strips_whitespace(engine):
    result = engine.analyze_skill_gap("Software Engineer", ["  Python  ", " Git"])
    assert result["user_skills"] == ["Python", "Git"]

# tests/test_skill_gap.py
"""
Run from the Backend/ directory:
    python tests/test_skill_gap.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.skill_gap_service import SkillGapService

engine = SkillGapService()
user_skills = ["Python", "Git", "SQL"]

result = engine.analyze_skill_gap("Software Engineer", user_skills)

print("\nCAREER")
print(result["career"])
print("\nREQUIRED SKILLS")
for skill in result["required_skills"]:
    print("-", skill)
print("\nUSER SKILLS")
for skill in result["user_skills"]:
    print("-", skill)
print("\nMISSING SKILLS")
for skill in result["missing_skills"]:
    print("-", skill)
print(f"\nREADINESS SCORE: {result['readiness_score']}%")
# tests/test_recommendation.py
"""
Run from the Backend/ directory:
    python tests/test_recommendation.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.recommendation_service import RecommendationService

engine = RecommendationService()

sample_answers = {
    1: 5, 2: 5, 9: 5, 10: 5, 11: 5, 12: 5,
    4: 1, 5: 1, 17: 1
}

results = engine.get_top_careers(sample_answers)

print("\nTOP CAREER RECOMMENDATIONS\n")
for rank, (career, score) in enumerate(results, start=1):
    print(f"{rank}. {career} - {score}%")
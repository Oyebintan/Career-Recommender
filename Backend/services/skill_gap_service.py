from services.dataset_loader import DatasetLoader


class SkillGapService:
    """
    Compares user skills with the skills
    required for a selected career.
    """

    def __init__(self):
        self.loader = DatasetLoader()

        self.skills_df = (
            self.loader.load_career_skills()
        )

    def get_required_skills(self, career_name):

        career_rows = self.skills_df[
            self.skills_df["career_name"] == career_name
        ]

        skills = career_rows["skill"].tolist()

        return sorted(list(set(skills)))

    def analyze_skill_gap(
        self,
        career_name,
        user_skills
    ):

        required_skills = self.get_required_skills(
            career_name
        )

        user_skills = [
            skill.strip()
            for skill in user_skills
        ]

        missing_skills = [
            skill
            for skill in required_skills
            if skill not in user_skills
        ]

        if required_skills:
            readiness_score = round(
                (
                    (len(required_skills) - len(missing_skills))
                    / len(required_skills)
                ) * 100,
                2
            )
        else:
            # No skills on record for this career — nothing to be
            # "missing", so treat readiness as undefined/0 instead
            # of raising a ZeroDivisionError.
            readiness_score = 0.0

        return {
            "career": career_name,
            "required_skills": required_skills,
            "user_skills": user_skills,
            "missing_skills": missing_skills,
            "readiness_score": readiness_score
        }
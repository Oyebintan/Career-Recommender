from services.dataset_loader import DatasetLoader


class RecommendationService:
    """
    Generates career recommendations based on assessment answers.
    """

    def __init__(self):
        self.loader = DatasetLoader()

        self.mapping_df = (
            self.loader.load_career_question_mapping()
        )

        self.career_df = (
            self.loader.load_career_profiles()
        )

    def calculate_scores(self, answers):
        """
        answers format:

        {
            1:5,
            2:4,
            3:3
        }
        """

        career_scores = {}

        for question_id, answer_value in answers.items():

            matching_rows = self.mapping_df[
                self.mapping_df["question_id"] == question_id
            ]

            for _, row in matching_rows.iterrows():

                career_name = row["career_name"]
                weight = row["weight"]

                score = answer_value * weight

                if career_name not in career_scores:
                    career_scores[career_name] = 0

                career_scores[career_name] += score

        return career_scores

    def normalize_scores(self, career_scores):

        if not career_scores:
            return {}

        max_score = max(career_scores.values())

        if max_score == 0:
            # Defensive guard: avoids a ZeroDivisionError if every
            # matched weight ever ends up being 0 for some reason.
            return {career: 0.0 for career in career_scores}

        normalized_scores = {}

        for career, score in career_scores.items():

            normalized_scores[career] = round(
                (score / max_score) * 100,
                2
            )

        return normalized_scores

    def get_top_careers(self, answers, top_n=3):

        raw_scores = self.calculate_scores(
            answers
        )

        normalized_scores = self.normalize_scores(
            raw_scores
        )

        ranked = sorted(
            normalized_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_n]
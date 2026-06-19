import pandas as pd
from pathlib import Path


class DatasetLoader:
    """
    Loads all datasets used by the career recommender system.
    """

    def __init__(self):
        # this file lives at:   <project_root>/Backend/services/dataset_loader.py
        # .parent      -> Backend/services
        # .parent.parent -> Backend
        # .parent.parent.parent -> <project_root>   (this is what we want)
        self.project_root = Path(__file__).resolve().parent.parent.parent

        self.custom_dataset_path = (
            self.project_root / "datasets" / "custom"
        )

        self.onet_dataset_path = (
            self.project_root / "datasets" / "onet"
        )

    def load_career_profiles(self):
        file_path = (
            self.custom_dataset_path /
            "career_profiles.csv"
        )

        return pd.read_csv(file_path)

    def load_career_skills(self):
        file_path = (
            self.custom_dataset_path /
            "career_skills.csv"
        )

        return pd.read_csv(file_path)

    def load_assessment_questions(self):
        file_path = (
            self.custom_dataset_path /
            "assessment_questions.csv"
        )

        return pd.read_csv(file_path)

    def load_career_question_mapping(self):
        file_path = (
            self.custom_dataset_path /
            "career_question_mapping.csv"
        )

        return pd.read_csv(file_path)

    def load_career_descriptions(self):
        file_path = (
            self.custom_dataset_path /
            "career_descriptions.csv"
        )

        return pd.read_csv(file_path)

    def load_all(self):
        return {
            "profiles": self.load_career_profiles(),
            "skills": self.load_career_skills(),
            "questions": self.load_assessment_questions(),
            "mappings": self.load_career_question_mapping(),
            "descriptions": self.load_career_descriptions()
        }
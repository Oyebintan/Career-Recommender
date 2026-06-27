import os
import pandas as pd
from pathlib import Path


class DatasetLoaderError(Exception):
    pass


class DatasetLoader:
    """
    Finds datasets/custom by walking upward from this file.
    Works on any hosting platform regardless of folder depth.
    Override with env var: DATASETS_DIR=/absolute/path/to/datasets/custom
    """

    def __init__(self):
        self.custom_dataset_path = self._locate()
        self.onet_dataset_path   = self.custom_dataset_path.parent / "onet"

    def _locate(self) -> Path:
        env = os.environ.get("DATASETS_DIR")
        if env:
            p = Path(env).resolve()
            if (p / "career_profiles.csv").exists():
                return p
            raise DatasetLoaderError(
                f"DATASETS_DIR='{p}' but career_profiles.csv not found there."
            )

        here = Path(__file__).resolve().parent
        for level in [here] + list(here.parents):
            candidate = level / "datasets" / "custom"
            if (candidate / "career_profiles.csv").exists():
                return candidate

        searched = [str(l / "datasets" / "custom") for l in [here] + list(here.parents)]
        raise DatasetLoaderError(
            "Cannot locate datasets/custom folder. Searched:\n"
            + "\n".join("  - " + p for p in searched)
            + "\n\nFix: set DATASETS_DIR env variable to the absolute path "
              "of the folder containing career_profiles.csv."
        )

    def load_career_profiles(self):
        return pd.read_csv(self.custom_dataset_path / "career_profiles.csv")

    def load_career_skills(self):
        return pd.read_csv(self.custom_dataset_path / "career_skills.csv")

    def load_assessment_questions(self):
        return pd.read_csv(self.custom_dataset_path / "assessment_questions.csv")

    def load_career_question_mapping(self):
        return pd.read_csv(self.custom_dataset_path / "career_question_mapping.csv")

    def load_career_descriptions(self):
        return pd.read_csv(self.custom_dataset_path / "career_descriptions.csv")

    def load_all(self):
        return {
            "profiles":     self.load_career_profiles(),
            "skills":       self.load_career_skills(),
            "questions":    self.load_assessment_questions(),
            "mappings":     self.load_career_question_mapping(),
            "descriptions": self.load_career_descriptions(),
        }
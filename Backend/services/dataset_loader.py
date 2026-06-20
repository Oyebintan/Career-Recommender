import os
import pandas as pd
from pathlib import Path


class DatasetLoaderError(Exception):
    """Raised when the datasets/custom folder can't be located anywhere."""
    pass


class DatasetLoader:
    """
    Loads all datasets used by the career recommender system.

    Path resolution is intentionally defensive: different hosting platforms
    (Hugging Face Spaces, Render, Railway, plain VPS, local machine) can lay
    out a deployed repo at different folder depths than your local copy.
    Instead of assuming a fixed "go up exactly 3 levels" path, this walks
    upward from this file looking for a real "datasets/custom" folder, and
    also honours an optional DATASETS_DIR environment variable as an
    explicit override for unusual deployments.
    """

    def __init__(self):
        self.custom_dataset_path = self._locate_dataset_dir()
        self.onet_dataset_path = self.custom_dataset_path.parent / "onet"

    def _locate_dataset_dir(self) -> Path:
        # 1. Explicit override always wins, if set.
        env_override = os.environ.get("DATASETS_DIR")
        if env_override:
            candidate = Path(env_override).resolve()
            if (candidate / "career_profiles.csv").exists():
                return candidate
            raise DatasetLoaderError(
                f"DATASETS_DIR is set to '{candidate}' but "
                f"'career_profiles.csv' was not found there."
            )

        # 2. Walk upward from this file's location, checking each level
        #    for a datasets/custom folder that actually has the data in it.
        here = Path(__file__).resolve().parent
        for level in [here] + list(here.parents):
            candidate = level / "datasets" / "custom"
            if (candidate / "career_profiles.csv").exists():
                return candidate

        # 3. Nothing found anywhere — fail loudly with a useful message
        #    instead of silently returning empty data.
        searched = [str(level / "datasets" / "custom") for level in [here] + list(here.parents)]
        raise DatasetLoaderError(
            "Could not locate the datasets/custom folder. Searched:\n"
            + "\n".join(f"  - {p}" for p in searched)
            + "\n\nIf your deployment uses a different folder layout, set the "
              "DATASETS_DIR environment variable to the absolute path of the "
              "'custom' datasets folder (the one containing career_profiles.csv)."
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
            "profiles": self.load_career_profiles(),
            "skills": self.load_career_skills(),
            "questions": self.load_assessment_questions(),
            "mappings": self.load_career_question_mapping(),
            "descriptions": self.load_career_descriptions(),
        }
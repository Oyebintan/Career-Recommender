from services.dataset_loader import DatasetLoader


def test_load_all_returns_every_dataset():
    datasets = DatasetLoader().load_all()

    assert set(datasets.keys()) == {
        "profiles", "skills", "questions", "mappings", "descriptions"
    }
    for name, df in datasets.items():
        assert not df.empty, f"{name} dataset should not be empty"


def test_career_profiles_columns():
    df = DatasetLoader().load_career_profiles()
    assert list(df.columns) == ["career_id", "career_name", "domain"]
    assert df["career_name"].duplicated().sum() == 0


def test_assessment_questions_columns():
    df = DatasetLoader().load_assessment_questions()
    assert list(df.columns) == ["question_id", "question", "category"]
    assert df["question_id"].duplicated().sum() == 0


def test_every_career_has_a_description_and_skills():
    loader = DatasetLoader()
    profile_names = set(loader.load_career_profiles()["career_name"])
    desc_names = set(loader.load_career_descriptions()["career_name"])
    skill_names = set(loader.load_career_skills()["career_name"])

    assert profile_names <= desc_names, \
        f"Careers missing descriptions: {profile_names - desc_names}"
    assert profile_names <= skill_names, \
        f"Careers missing skills: {profile_names - skill_names}"


def test_every_career_in_mapping_is_a_known_career():
    loader = DatasetLoader()
    profile_names = set(loader.load_career_profiles()["career_name"])
    mapping_names = set(loader.load_career_question_mapping()["career_name"])

    assert mapping_names <= profile_names, \
        f"Mapping references unknown careers: {mapping_names - profile_names}"


def test_every_mapped_question_id_exists():
    loader = DatasetLoader()
    question_ids = set(loader.load_assessment_questions()["question_id"])
    mapping_ids = set(loader.load_career_question_mapping()["question_id"])

    assert mapping_ids <= question_ids, \
        f"Mapping references unknown question ids: {mapping_ids - question_ids}"

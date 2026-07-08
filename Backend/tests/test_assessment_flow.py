import re

from services.dataset_loader import DatasetLoader


def _setup_profile(client):
    client.post("/profile/setup", data={
        "age": "25", "gender": "Female",
        "education_level": "Bachelor", "course_of_study": "Computer Science",
    })


def _all_question_ids():
    return DatasetLoader().load_assessment_questions()["question_id"].tolist()


def test_assessment_page_lists_every_question(registered_user):
    client, _, _ = registered_user
    _setup_profile(client)

    resp = client.get("/assessment")
    assert resp.status_code == 200
    body = resp.data.decode()
    for qid in _all_question_ids():
        assert f'name="q_{qid}"' in body


def test_submit_with_all_answers_redirects_to_results(registered_user):
    client, _, _ = registered_user
    _setup_profile(client)

    data = {f"q_{qid}": "3" for qid in _all_question_ids()}
    resp = client.post("/assessment/submit", data=data)
    assert resp.status_code == 302
    assert re.search(r"/results/\d+$", resp.headers["Location"])


def test_submit_with_missing_answer_redirects_back_to_assessment(registered_user):
    client, _, _ = registered_user
    _setup_profile(client)

    qids = _all_question_ids()
    data = {f"q_{qid}": "3" for qid in qids[:-1]}  # leave one unanswered
    resp = client.post("/assessment/submit", data=data, follow_redirects=True)
    assert b"answer all questions" in resp.data


def test_submit_with_out_of_range_answer_is_rejected(registered_user):
    client, _, _ = registered_user
    _setup_profile(client)

    qids = _all_question_ids()
    data = {f"q_{qid}": "3" for qid in qids}
    data[f"q_{qids[0]}"] = "9"  # out of the 1-5 Likert range
    resp = client.post("/assessment/submit", data=data, follow_redirects=True)
    assert b"Invalid answer detected" in resp.data


def test_results_page_shows_career_cards(registered_user):
    client, _, _ = registered_user
    _setup_profile(client)

    data = {f"q_{qid}": "5" for qid in _all_question_ids()}
    submit_resp = client.post("/assessment/submit", data=data)
    results_url = submit_resp.headers["Location"]

    resp = client.get(results_url)
    assert resp.status_code == 200
    assert b"Your Top 3 Career Matches" in resp.data or b"career" in resp.data.lower()


def test_skill_gap_case_insensitive_end_to_end(registered_user):
    client, _, _ = registered_user
    _setup_profile(client)

    data = {f"q_{qid}": "5" for qid in _all_question_ids()}
    submit_resp = client.post("/assessment/submit", data=data)
    assessment_id = re.search(r"/results/(\d+)$", submit_resp.headers["Location"]).group(1)

    resp = client.post(
        f"/skill-gap/{assessment_id}/Software Engineer",
        data={"user_skills": "python, git, sql"},
    )
    assert resp.status_code == 200
    body = resp.data.decode()
    assert '<span class="skill-pill missing">Python</span>' not in body
    assert '<span class="skill-pill missing">Git</span>' not in body
    assert '<span class="skill-pill missing">SQL</span>' not in body


def test_user_cannot_view_another_users_results(client):
    # User A submits an assessment.
    client.post("/register", data={
        "name": "User A", "email": "a@example.com",
        "password": "password123", "confirm_password": "password123",
    })
    _setup_profile(client)
    data = {f"q_{qid}": "3" for qid in _all_question_ids()}
    submit_resp = client.post("/assessment/submit", data=data)
    results_url = submit_resp.headers["Location"]
    client.get("/logout")

    # User B tries to view User A's results directly.
    client.post("/register", data={
        "name": "User B", "email": "b@example.com",
        "password": "password123", "confirm_password": "password123",
    })
    resp = client.get(results_url)
    assert resp.status_code == 404

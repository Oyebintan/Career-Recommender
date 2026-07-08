def test_profile_setup_requires_login(client):
    resp = client.get("/profile/setup")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_profile_setup_creates_profile_and_redirects_to_assessment(registered_user):
    client, _, _ = registered_user
    resp = client.post("/profile/setup", data={
        "age": "25",
        "gender": "Female",
        "education_level": "Bachelor",
        "course_of_study": "Computer Science",
    })
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/assessment")


def test_profile_setup_rejects_non_numeric_age(registered_user):
    client, _, _ = registered_user
    resp = client.post("/profile/setup", data={
        "age": "abc",
        "gender": "Female",
        "education_level": "Bachelor",
        "course_of_study": "Computer Science",
    })
    assert b"valid age" in resp.data


def test_profile_setup_rejects_out_of_range_age(registered_user):
    client, _, _ = registered_user
    resp = client.post("/profile/setup", data={
        "age": "5",
        "gender": "Female",
        "education_level": "Bachelor",
        "course_of_study": "Computer Science",
    })
    assert b"valid age" in resp.data


def test_profile_setup_rejects_missing_fields(registered_user):
    client, _, _ = registered_user
    resp = client.post("/profile/setup", data={
        "age": "25",
        "gender": "",
        "education_level": "Bachelor",
        "course_of_study": "Computer Science",
    })
    assert b"All fields are required" in resp.data


def test_profile_setup_updates_existing_profile(registered_user, app):
    client, _, _ = registered_user
    client.post("/profile/setup", data={
        "age": "25", "gender": "Female",
        "education_level": "Bachelor", "course_of_study": "CS",
    })
    resp = client.post("/profile/setup", data={
        "age": "30", "gender": "Male",
        "education_level": "Masters", "course_of_study": "Physics",
    }, follow_redirects=True)
    assert resp.status_code == 200

    from models.profile import Profile
    from models.user import User
    with app.app_context():
        user = User.query.filter_by(email="pytest-user@example.com").first()
        profile = Profile.query.filter_by(user_id=user.id).first()
        assert profile.age == 30
        assert profile.course_of_study == "Physics"

def test_register_creates_account_and_redirects_to_profile_setup(client):
    resp = client.post("/register", data={
        "name": "New User",
        "email": "new@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/profile/setup")


def test_register_rejects_mismatched_passwords(client):
    resp = client.post("/register", data={
        "name": "New User",
        "email": "new@example.com",
        "password": "password123",
        "confirm_password": "different",
    }, follow_redirects=True)
    assert b"Passwords do not match" in resp.data


def test_register_rejects_short_password(client):
    resp = client.post("/register", data={
        "name": "New User",
        "email": "new@example.com",
        "password": "abc",
        "confirm_password": "abc",
    }, follow_redirects=True)
    assert b"at least 6 characters" in resp.data


def test_register_rejects_duplicate_email(client):
    client.post("/register", data={
        "name": "First",
        "email": "dup@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    client.get("/logout")

    resp = client.post("/register", data={
        "name": "Second",
        "email": "dup@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)
    assert b"already exists" in resp.data


def test_login_with_correct_credentials_succeeds(client):
    client.post("/register", data={
        "name": "Login User",
        "email": "login@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    client.get("/logout")

    resp = client.post("/login", data={
        "email": "login@example.com",
        "password": "password123",
    })
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/dashboard")


def test_login_with_wrong_password_fails(client):
    client.post("/register", data={
        "name": "Login User",
        "email": "login2@example.com",
        "password": "password123",
        "confirm_password": "password123",
    })
    client.get("/logout")

    resp = client.post("/login", data={
        "email": "login2@example.com",
        "password": "wrong-password",
    }, follow_redirects=True)
    assert b"Invalid email or password" in resp.data


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_logout_then_protected_route_redirects_to_login(registered_user):
    client, _, _ = registered_user
    client.get("/logout")
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]

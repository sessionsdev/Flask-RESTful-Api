import json

from project.api.models import User


def test_add_user(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        "/users",
        data=json.dumps({"username": "jon", "email": "jon@sessionsdev.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 201
    assert "jon@sessionsdev.com was added!" in data["message"]


def test_add_user_invalid_json(test_app, test_database):
    client = test_app.test_client()
    resp = client.post("/users", data=json.dumps({}), content_type="application/json")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_invalid_json_keys(test_app, test_database):
    client = test_app.test_client()
    resp = client.post(
        "/users",
        data=json.dumps({"email": "jon@sessionsdev.com"}),
        content_type="application/json",
    )
    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Input payload validation failed" in data["message"]


def test_add_user_duplicate_email(test_app, test_database):
    client = test_app.test_client()
    client.post(
        "/users",
        data=json.dumps({"username": "jon", "email": "jon@sessionsdev.com"}),
        content_type="application/json",
    )
    resp = client.post(
        "/users",
        data=json.dumps({"username": "jon", "email": "jon@sessionsdev.com"}),
        content_type="application/json",
    )

    data = json.loads(resp.data.decode())
    assert resp.status_code == 400
    assert "Sorry.  That email already exists." in data["message"]


def test_single_user(test_app, test_database, add_user):
    user = add_user("jonny", "jonny@sessionsdev.com")
    client = test_app.test_client()
    resp = client.get(f"/users/{user.id}")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert "jonny" in data["username"]
    assert "jonny@sessionsdev.com" in data["email"]


def test_single_user_incorrect_id(test_app, test_database):
    client = test_app.test_client()
    resp = client.get("/users/999")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 404
    assert "User 999 does not exist" in data["message"]


def test_all_users(test_app, test_database, add_user):
    test_database.session.query(User).delete()
    add_user("kristen", "kristen@sessionsdev.com")
    add_user("jonny", "jonny@sessionsdev.com")
    client = test_app.test_client()
    resp = client.get("/users")
    data = json.loads(resp.data.decode())
    assert resp.status_code == 200
    assert len(data) == 2
    assert "kristen" in data[0]["username"]
    assert "kristen@sessionsdev.com" in data[0]["email"]
    assert "jonny" in data[1]["username"]
    assert "jonny@sessionsdev.com" in data[1]["email"]

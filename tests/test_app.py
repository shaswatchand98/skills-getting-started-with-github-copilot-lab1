import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities dict before each test
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


@pytest.fixture()
def client():
    return TestClient(app_module.app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect a few known activities from the sample data
    assert "Chess Club" in data


def test_signup_success_and_cleanup(client):
    activity = "Chess Club"
    email = "tester1@example.com"

    # Ensure not present initially
    assert email not in app_module.activities[activity]["participants"]

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Now participant should be present
    assert email in app_module.activities[activity]["participants"]


def test_signup_duplicate(client):
    activity = "Chess Club"
    email = "tester2@example.com"

    # First signup should succeed
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    # Second signup should fail with 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400


def test_signup_activity_not_found(client):
    resp = client.post("/activities/Nonexistent%20Activity/signup?email=anon@example.com")
    assert resp.status_code == 404


def test_unregister_success(client):
    activity = "Chess Club"
    # use an existing participant from sample data
    email = app_module.activities[activity]["participants"][0]

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]


def test_unregister_not_signed_up(client):
    activity = "Chess Club"
    email = "not-signed-up@example.com"

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404


def test_unregister_activity_not_found(client):
    resp = client.delete("/activities/NoSuchActivity/participants?email=anon@example.com")
    assert resp.status_code == 404

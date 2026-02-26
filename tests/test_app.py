from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities_state():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original))


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_payload():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "participants" in data["Basketball Team"]


def test_signup_adds_participant():
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    existing_email = activities["Tennis Club"]["participants"][0]

    response = client.post("/activities/Tennis%20Club/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Unknown%20Activity/signup", params={"email": "x@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    email = activities["Drama Club"]["participants"][0]

    response = client.delete("/activities/Drama%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email not in activities["Drama Club"]["participants"]


def test_unregister_non_member_returns_400():
    response = client.delete("/activities/Art%20Studio/signup", params={"email": "notjoined@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_unknown_activity_returns_404():
    response = client.delete("/activities/Unknown%20Activity/signup", params={"email": "x@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

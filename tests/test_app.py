import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore activity participant lists after every test."""
    original = {
        name: details["participants"].copy()
        for name, details in activities.items()
    }

    yield

    for name, participants in original.items():
        activities[name]["participants"] = participants


def test_signup_for_activity_success():
    """A student can sign up for an existing activity."""
    email = "new.student@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Chess Club"
    }
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_signup():
    """A student cannot sign up for the same activity twice."""
    email = "michael@mergington.edu"

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_for_activity_rejects_unknown_activity():
    """Signing up for a non-existent activity returns a not-found error."""
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

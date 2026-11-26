import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, activities):
    # Arrange
    expected_activities = activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activities):
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities[activity_name]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client, activities):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities["Chess Club"]["participants"] == ["existing@mergington.edu"]


def test_signup_rejects_duplicate_participant(client, activities):
    # Arrange
    activity_name = "Chess Club"
    email = "existing@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert activities[activity_name]["participants"] == [email]


def test_unregister_removes_participant(client, activities):
    # Arrange
    activity_name = "Chess Club"
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/Chess%20Club/participants/{email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities[activity_name]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client, activities):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/Unknown%20Club/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities["Chess Club"]["participants"] == ["existing@mergington.edu"]


def test_unregister_returns_not_found_for_unregistered_participant(
    client, activities
):
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/Chess%20Club/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not registered for this activity"
    }
    assert activities[activity_name]["participants"] == ["existing@mergington.edu"]

from fastapi.testclient import TestClient
from src.app import app
from urllib.parse import quote

client = TestClient(app)


def test_get_activities():
    # Arrange
    expected_activities = ["Chess Club", "Programming Class"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    for activity in expected_activities:
        assert activity in data


def test_signup_new_participant():
    # Arrange
    activity = "Chess Club"
    email = "testuser@mergington.edu"
    initial_participants = client.get("/activities").json()[activity]["participants"]
    if email in initial_participants:
        initial_participants.remove(email)

    # Act
    encoded_activity = quote(activity)
    response = client.post(f"/activities/{encoded_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    updated_participants = client.get("/activities").json()[activity]["participants"]
    assert email in updated_participants


def test_signup_duplicate_participant():
    # Arrange
    activity = "Chess Club"
    email = "duplicate@mergington.edu"
    encoded_activity = quote(activity)
    client.post(f"/activities/{encoded_activity}/signup?email={email}")

    # Act
    duplicate_response = client.post(f"/activities/{encoded_activity}/signup?email={email}")

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant():
    # Arrange
    activity = "Chess Club"
    email = "toremove@mergington.edu"
    encoded_activity = quote(activity)
    client.post(f"/activities/{encoded_activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{encoded_activity}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"
    participants_after = client.get("/activities").json()[activity]["participants"]
    assert email not in participants_after

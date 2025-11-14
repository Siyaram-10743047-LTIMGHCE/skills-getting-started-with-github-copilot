import pytest
from fastapi.testclient import TestClient
from src.app import app  # Import your FastAPI app from src/app.py

client = TestClient(app)

def test_get_activities():
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Check that at least one known activity exists
    assert "Chess Club" in data
    # Validate structure of an activity
    for activity, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details

def test_signup_and_unregister():
    """Test signing up and unregistering a participant"""
    activity_name = "Chess Club"
    email = "testuser@mergington.edu"

    # Sign up
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_response.status_code == 200
    signup_data = signup_response.json()
    assert "message" in signup_data
    assert email in client.get("/activities").json()[activity_name]["participants"]

    # Unregister
    unregister_response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    assert unregister_response.status_code == 200
    unregister_data = unregister_response.json()
    assert "message" in unregister_data
    assert email not in client.get("/activities").json()[activity_name]["participants"]

def test_signup_duplicate():
    """Test duplicate signup should fail"""
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    # First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Second signup should fail
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    assert "detail" in response.json()

def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent/signup", params={"email": "user@mergington.edu"})
    assert response.status_code == 404
    assert "detail" in response.json()

def test_unregister_not_signed_up():
    """Test unregister when user is not signed up"""
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
    assert response.status_code == 400
    assert "detail" in response.json()
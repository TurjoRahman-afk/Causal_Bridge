from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CausalBridge"

def test_api_health_endpoint():
    """Test the API health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_analyze_endpoint_valid_request():
    """Test the analyze endpoint with a valid request"""
    response = client.post("/api/v1/analyze", json={
        "question": "What is the effect of education on income?",
        "dataset_uri": "test_data.csv",
        "schema": {
            "treatment": "education",
            "outcome": "income",
            "confounders": ["age", "experience"]
        },
        "params": {
            "method": "backdoor"
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "plan" in data
    assert "results" in data
    assert "message" in data

def test_analyze_endpoint_missing_question():
    """Test the analyze endpoint with missing question"""
    response = client.post("/api/v1/analyze", json={
        "dataset_uri": "test_data.csv",
        "schema": {
            "treatment": "education",
            "outcome": "income"
        }
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_analyze_endpoint_invalid_method():
    """Test the analyze endpoint with invalid method"""
    response = client.post("/api/v1/analyze", json={
        "question": "What is the effect of education on income?",
        "dataset_uri": "test_data.csv",
        "schema": {
            "treatment": "education",
            "outcome": "income"
        },
        "params": {
            "method": "invalid_method"
        }
    })
    assert response.status_code == 400  # Bad Request
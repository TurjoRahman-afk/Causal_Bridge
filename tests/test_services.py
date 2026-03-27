from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_analyze_valid_request():
    response = client.post("/analyze", json={
        "question": "What is the effect of marketing on sales?",
        "schema": {"type": "object", "properties": {"marketing": {"type": "number"}, "sales": {"type": "number"}}},
        "params": {"dataset_uri": "path/to/dataset.csv"}
    })
    assert response.status_code == 200
    data = response.json()
    assert "plan" in data
    assert "estimate" in data
    assert "assumptions" in data
    assert "diagnostics" in data
    assert "narrative" in data

def test_analyze_invalid_request():
    response = client.post("/analyze", json={
        "question": "What is the effect of marketing on sales?",
        "schema": {},  # Invalid schema
        "params": {}
    })
    assert response.status_code == 422  # Unprocessable Entity for validation errors

def test_analyze_missing_question():
    response = client.post("/analyze", json={
        "schema": {"type": "object", "properties": {"marketing": {"type": "number"}, "sales": {"type": "number"}}},
        "params": {"dataset_uri": "path/to/dataset.csv"}
    })
    assert response.status_code == 422  # Unprocessable Entity for validation errors

def test_analyze_empty_request():
    response = client.post("/analyze", json={})
    assert response.status_code == 422  # Unprocessable Entity for validation errors
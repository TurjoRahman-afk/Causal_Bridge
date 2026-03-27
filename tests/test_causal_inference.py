from fastapi.testclient import TestClient
from src.main import app
from src.services.causal_inference_service import run_estimation

client = TestClient(app)

def test_run_estimation_valid():
    plan = {
        "treatment": "treatment_variable",
        "outcome": "outcome_variable",
        "covariates": ["covariate1", "covariate2"]
    }
    dataset_uri = "path/to/dataset.csv"
    schema = {"treatment": "treatment_variable", "outcome": "outcome_variable"}

    result = run_estimation(plan, dataset_uri, schema)
    
    assert result is not None
    assert "estimate" in result
    assert "diagnostics" in result

def test_run_estimation_invalid_plan():
    plan = {}
    dataset_uri = "path/to/dataset.csv"
    schema = {}

    try:
        run_estimation(plan, dataset_uri, schema)
        assert False, "Expected an exception for invalid plan"
    except Exception as e:
        assert str(e) == "Invalid plan provided"

def test_analyze_endpoint():
    response = client.post("/analyze", json={
        "question": "What is the effect of treatment on outcome?",
        "schema": {"treatment": "treatment_variable", "outcome": "outcome_variable"},
        "params": {}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "plan" in data
    assert "estimate" in data
    assert "assumptions" in data
    assert "diagnostics" in data
    assert "narrative" in data
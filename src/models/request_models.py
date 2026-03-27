
"""checks what data comes into the API, validates incoming JSON data automatically"""
"""this file defines dta models that validate and structure incoming API requests using Pydantic"""
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any


# validates requess to the main /api/v1/analyze endpoint
class AnalyzeRequest(BaseModel):
    question: str = Field(..., description="Natural language causal question")   # Must be a string
    dataset_uri: str = Field(..., description="URI or path to dataset")   # path to the dataset 
    dataset_schema: Dict[str, Any] = Field(default_factory=dict, description="Dataset schema mapping (optional - Gemini can infer)", alias="schema")
    params: Optional[Dict] = Field(default_factory=dict, description="Additional parameters")
    
    # provides example request for users 
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the effect of education on income?",
                "dataset_uri": "data/income_data.csv",
                "schema": {
                    "treatment": "education_years",
                    "outcome": "annual_income",
                    "confounders": ["age", "gender", "experience"]
                },
                "params": {
                    "method": "propensity_score_matching",
                    "confidence_level": 0.95
                }
            }
        }
# validation request 
# used for internal data validation endpoints
class ValidationRequest(BaseModel):
    data: dict
    dataset_schema: dict = Field(alias="schema")
# internal communication model for causal estimation requests 
class CausalEstimationRequest(BaseModel):
    plan: dict
    dataset_uri: str
    dataset_schema: dict = Field(alias="schema")
    
    
    
    
    
    
    """### How it works!!!
    
{
    "question": "Does overtime cause employees to quit?",
    "dataset_uri": "uploads/hr_data.csv"
}


####this file defines
----AnalyzeRequest: Main API input (question +dataset+ optional schema)
----ValidationRequest: for data validation 
----CausalEstimationRequest: internal service communication 
!!! Its the gatekeeper that ensures only valid, well formed data enters the system 
    """
"""checks what data goes out of the API to the users

### here User request(JSON) -> request_models.py (validates) -> API process ->
### -> result created -> response_models.py(structures) -> User receives(JSON) 
# """

from pydantic import BaseModel
from typing import Any, Dict, Optional

# analyze the response model for the main /api/v1/analyze endpoint
class AnalyzeResponse(BaseModel): # this defines the structure of successful analysis responses 
    success: bool # YES/NO if analysis was successful
    plan: Dict[str, Any] # the causal analysis plan used
    results: Dict[str, Any] # the results of the analysis
    message: str # a message about the analysis
    interpretation: Optional[Dict[str, str]] = None  # Human-readable summary
    
    
    ## the Config class provides an example of a typical response for users 
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "plan": {
                    "treatment": "education_years",
                    "outcome": "annual_income",
                    "method": "propensity_score_matching",
                    "confounders": ["age", "gender"]
                },
                "results": {
                    "ate": 5000.0,
                    "confidence_interval": [4500.0, 5500.0],
                    "p_value": 0.001,
                    "n_treated": 500,
                    "n_control": 500
                },
                "message": "Analysis completed successfully",
                "interpretation": {
                    "effect_direction": "positive",
                    "significance": "significant",
                    "plain_english": "Each additional year of education increases annual income by $5,000",
                    "confidence": "high"
                }
            }
        }

class ErrorResponseModel(BaseModel):
    detail: str
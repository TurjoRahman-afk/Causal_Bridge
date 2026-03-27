from fastapi import Depends, HTTPException
from ..services.nlp_service import make_plan
from ..services.causal_inference_service import run_estimation
from ..services.validation_service import validate_request
from ..models.request_models import AnalyzeRequest
from ..core.exceptions import InvalidRequestException
from ..core.config import settings

# Import Gemini service if available
try:
    from ..services.nlp_service_gemini import make_plan_with_gemini
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

def get_analyze_request(request: AnalyzeRequest) -> AnalyzeRequest:
    """
    Validate and return the analysis request.
    
    Args:
        request: The incoming analysis request
        
    Returns:
        Validated AnalyzeRequest object
        
    Raises:
        HTTPException: If validation fails
    """
    if not validate_request(request):
        raise HTTPException(
            status_code=400,
            detail="Invalid request data. Please check question, dataset_uri, and schema."
        )
    return request

def get_plan(question: str, schema: dict, params: dict) -> dict:
    """
    Generate causal analysis plan from natural language question.
    
    Args:
        question: Natural language causal question
        schema: Dataset schema information
        params: Additional parameters
        
    Returns:
        Analysis plan dictionary
    """
    try:
        # Debug logging
        print(f"🔍 GEMINI_AVAILABLE: {GEMINI_AVAILABLE}")
        print(f"🔍 LLM Provider: {settings.llm_provider}")
        print(f"🔍 Gemini Key exists: {bool(settings.gemini_api_key)}")
        print(f"🔍 Groq Key exists: {bool(settings.groq_api_key)}")

        # Use AI service if either Gemini or Groq key is available
        has_ai_key = bool(settings.gemini_api_key) or bool(settings.groq_api_key)
        if GEMINI_AVAILABLE and has_ai_key:
            try:
                print("✅ Attempting to use AI service (Gemini/Groq)...")
                return make_plan_with_gemini(question, schema, params)
            except Exception as ai_error:
                print(f"⚠️  AI service failed ({ai_error}), falling back to simple parser")
        else:
            print(f"⚠️  No AI key configured, using simple parser")
        
        # Fallback to simple pattern-based parser
        return make_plan(question, schema, params)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analysis plan: {str(e)}"
        )

def get_estimation(plan: dict, dataset_uri: str, schema: dict) -> dict:
    """
    Execute causal inference estimation.
    
    Args:
        plan: Analysis plan from NLP service
        dataset_uri: Path or URI to dataset
        schema: Dataset schema
        
    Returns:
        Estimation results dictionary
    """
    try:
        return run_estimation(plan, dataset_uri, schema)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run estimation: {str(e)}"
        )
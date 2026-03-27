from fastapi import APIRouter, Depends, HTTPException
from ..models.request_models import AnalyzeRequest
from ..models.response_models import AnalyzeResponse
from .dependencies import get_analyze_request, get_plan, get_estimation

router = APIRouter()

def _generate_interpretation(plan: dict, results: dict) -> dict:
    """Generate human-readable interpretation of results"""
    ate = results.get('ate', 0)
    p_value = results.get('p_value', 1)
    treatment = plan.get('treatment', 'treatment')
    outcome = plan.get('outcome', 'outcome')
    
    # Determine effect direction
    if ate > 0:
        direction = "increases"
        effect_dir = "positive"
    elif ate < 0:
        direction = "decreases"
        effect_dir = "negative"
    else:
        direction = "has no effect on"
        effect_dir = "none"
    
    # Determine significance
    is_significant = p_value < 0.05
    sig_text = "✅ SIGNIFICANT" if is_significant else "❌ NOT SIGNIFICANT"
    confidence = "high" if p_value < 0.01 else "moderate" if p_value < 0.05 else "low"
    
    # Build plain English explanation
    if abs(ate) < 0.0001:
        plain = f"{treatment.replace('_', ' ').title()} has NO measurable effect on {outcome.replace('_', ' ')}"
    elif 'attrition' in outcome.lower() or 'quit' in outcome.lower() or 'leave' in outcome.lower():
        # For binary outcomes (like attrition)
        percent_change = abs(ate) * 100
        plain = f"{treatment.replace('_', ' ').title()} {direction} the chance of leaving by {percent_change:.1f} percentage points"
    else:
        # For continuous outcomes
        plain = f"Each unit increase in {treatment.replace('_', ' ')} {direction} {outcome.replace('_', ' ')} by {abs(ate):.3f}"
    
    # Add confidence statement
    if is_significant:
        plain += f" (with {confidence} confidence)"
    else:
        plain += " (but this result is NOT statistically reliable)"
    
    return {
        "effect_direction": effect_dir,
        "significance": sig_text,
        "plain_english": plain,
        "confidence": confidence,
        "recommendation": "Act on this finding" if is_significant and abs(ate) > 0.01 else "More data needed"
    }

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_causal_effect(
    request: AnalyzeRequest = Depends(get_analyze_request)
):
    """
    Analyze causal effects based on natural language question.
    
    NEW FEATURES:
    - Automatic data quality checks
    - Confounder suggestions
    - Multiple causal methods
    - Bootstrap confidence intervals
    
    Args:
        request: Contains question, dataset URI, schema, and parameters
        
    Returns:
        Causal inference results with quality warnings and suggestions
    """
    try:
        # Step 1: Generate analysis plan from NL question (pass dataset_uri for Gemini)
        params_with_uri = {**request.params, 'dataset_uri': request.dataset_uri}
        plan = get_plan(request.question, request.dataset_schema, params_with_uri)
        
        # Step 2: Execute causal inference (now includes quality checks)
        results = get_estimation(plan, request.dataset_uri, request.dataset_schema)
        
        # Build response message with warnings
        message = "Analysis completed successfully"
        quality = results.get("data_quality", {})
        if quality.get("warnings"):
            message += f". Warnings: {len(quality['warnings'])} data quality issues detected."
        
        # Generate human-readable interpretation
        interpretation = _generate_interpretation(plan, results)
        
        return AnalyzeResponse(
            success=True,
            plan=plan,
            results=results,
            message=message,
            interpretation=interpretation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CausalBridge", "version": "1.1.0"}
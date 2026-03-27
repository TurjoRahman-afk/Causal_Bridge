"""
NLP Service for converting natural language questions to causal analysis plans.
"""
from typing import Dict, List
from ..core.config import settings
from ..core.exceptions import PlanGenerationException

def make_plan(question: str, schema: dict, params: dict) -> dict:
    """
    Convert natural language question into causal analysis plan using LLM.
    
    Args:
        question: Natural language causal question (e.g., "What is the effect of X on Y?")
        schema: Dataset schema with column information
        params: Additional parameters for analysis
        
    Returns:
        Dict containing:
            - treatment: Treatment variable name
            - outcome: Outcome variable name
            - confounders: List of confounder variables
            - method: Causal inference method to use
            - effect_type: Type of effect (ATE, ATT, etc.)
    """
    try:
        # Extract variables from schema if provided
        treatment = schema.get("treatment")
        outcome = schema.get("outcome")
        confounders = schema.get("confounders", [])
        
        # If schema doesn't specify, try to parse from question
        if not treatment or not outcome:
            treatment, outcome = _parse_question(question)
        
        # Determine method
        method = params.get("method", settings.default_method)
        
        plan = {
            "treatment": treatment,
            "outcome": outcome,
            "confounders": confounders,
            "method": method,
            "effect_type": "ATE",
            "estimand_type": "nonparametric-ate"
        }
        
        return plan
        
    except Exception as e:
        raise PlanGenerationException(f"Failed to generate plan: {str(e)}")

def _parse_question(question: str) -> tuple:
    """
    Simple parser to extract treatment and outcome from natural language questions.
    Handles many common causal question patterns.
    """
    import re
    q = question.strip().rstrip('?').lower()

    # Pattern: "effect of X on Y" / "impact of X on Y" / "influence of X on Y"
    for phrase in ["effect of", "impact of", "influence of", "role of"]:
        if phrase in q and " on " in q:
            parts = q.split(phrase)[1].split(" on ")
            return parts[0].strip(), parts[1].strip()

    # Pattern: "does X cause/lead to/affect/increase/reduce Y"
    for phrase in ["cause", "lead to", "leads to", "affect", "affects",
                   "increase", "increases", "decrease", "decreases",
                   "reduce", "reduces", "improve", "improves",
                   "result in", "results in", "drive", "drives",
                   "influence", "influences", "predict", "predicts"]:
        match = re.search(rf"does (.+?) {re.escape(phrase)} (.+)", q)
        if match:
            return match.group(1).strip(), match.group(2).strip()

    # Pattern: "X causes/leads to/affects Y" (no "does")
    for phrase in ["causes", "leads to", "affects", "increases", "decreases",
                   "reduces", "improves", "drives", "influences", "predicts"]:
        match = re.search(rf"(.+?) {re.escape(phrase)} (.+)", q)
        if match:
            return match.group(1).strip(), match.group(2).strip()

    # Pattern: "is X related to Y"
    for pattern in [r"is (.+?) related to (.+)", r"does (.+?) relate to (.+)"]:
        match = re.search(pattern, q)
        if match:
            return match.group(1).strip(), match.group(2).strip()

    # Pattern: "X -> Y" or "X => Y"
    for sep in [" -> ", " => "]:
        if sep in question:
            parts = question.split(sep)
            return parts[0].strip(), parts[1].strip()

    raise PlanGenerationException(
        "Could not parse question. Please specify Treatment and Outcome manually in the dashboard."
    )

def enhance_plan_with_llm(question: str, schema: Dict, available_columns: List[str]) -> Dict:
    """
    Use LLM to enhance the causal analysis plan.
    This is a placeholder for future LLM integration.
    
    Args:
        question: Natural language question
        schema: Current schema information
        available_columns: List of available columns in dataset
        
    Returns:
        Enhanced plan with suggested confounders and method
    """
    # TODO: Implement OpenAI/Claude API call
    pass
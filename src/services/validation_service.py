"""
Validation Service for request validation.
"""
from typing import Dict
from ..models.request_models import AnalyzeRequest

def validate_request(request: AnalyzeRequest) -> bool:
    """
    Validate incoming analysis request.
    
    Args:
        request: The analysis request to validate
        
    Returns:
        True if valid, raises exception otherwise
    """
    # Validate question
    if not request.question or len(request.question.strip()) == 0:
        return False
    
    if len(request.question) > 1000:
        return False
    
    # Validate dataset URI
    if not request.dataset_uri or len(request.dataset_uri.strip()) == 0:
        return False
    
    # Schema is optional - can be empty dict if we want Gemini to infer everything
    # Just validate it's a dict if provided
    if request.dataset_schema is not None and not isinstance(request.dataset_schema, dict):
        return False
    
    # If schema is provided and has variables, that's great
    # If schema is empty or None, Gemini will try to infer from question
    # Both are valid scenarios
    
    # Validate params if present
    if request.params:
        if not isinstance(request.params, dict):
            return False
        
        # Validate method if specified
        valid_methods = ["backdoor", "propensity_score_matching", 
                        "instrumental_variable", "iv", 
                        "regression_discontinuity", "rd"]
        
        if "method" in request.params:
            if request.params["method"] not in valid_methods:
                return False
    
    return True

def validate_schema(schema: Dict) -> bool:
    """
    Validate schema structure.
    
    Args:
        schema: Dataset schema
        
    Returns:
        True if valid
    """
    if not isinstance(schema, dict):
        return False
    
    return True

def validate_dataset_access(dataset_uri: str) -> bool:
    """
    Validate that dataset can be accessed.
    
    Args:
        dataset_uri: Path or URI to dataset
        
    Returns:
        True if accessible
    """
    import os
    
    # Check if local file exists
    if os.path.isfile(dataset_uri):
        # Check file size
        file_size_mb = os.path.getsize(dataset_uri) / (1024 * 1024)
        if file_size_mb > 100:  # 100MB limit
            return False
        return True
    
    # If it's a URL, assume valid for now
    return True
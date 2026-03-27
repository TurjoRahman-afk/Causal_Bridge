
"""this file contains custom exception classes for better error handling in the project """
# theres total 5 custon exception classes defined here 
class CausalBridgeException(Exception):
    """Base exception for CausalBridge"""
    pass

class InvalidRequestException(CausalBridgeException):
    """Exception raised for invalid input data."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class PlanGenerationException(CausalBridgeException):
    """Raised when NLP plan generation fails"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class EstimationException(CausalBridgeException):
    """Exception raised when causal estimation fails."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ConfigurationError(CausalBridgeException):
    """Exception raised for configuration-related issues."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
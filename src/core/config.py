from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App settings
    app_name: str = "CausalBridge"
    debug: bool = True
    
    # LLM settings
    llm_provider: str = "Gemini"  # Options: "Gemini", "Groq", "OpenAI", "None"
    gemini_api_key: str = ""  # Get free key from https://aistudio.google.com/app/apikey
    groq_api_key: str = ""    # Get FREE key from https://console.groq.com (no credit card needed)
    openai_api_key: str = ""  # Optional, if you prefer OpenAI
    
    # Causal inference settings
    default_method: str = "backdoor"
    seed: int = 42
    confidence_level: float = 0.95
    
    # Data settings
    max_dataset_size_mb: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
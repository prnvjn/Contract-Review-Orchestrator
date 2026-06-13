from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./contract_orchestrator.db"
    
    # LangGraph Settings
    RECURSION_LIMIT: int = 5
    
    # Application Settings
    DEBUG: bool = False
    PROJECT_NAME: str = "ContractReviewOrchestrator"
    LLM_PROVIDER: str = "openai" # "openai" or "anthropic"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

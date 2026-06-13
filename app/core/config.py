from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLAMA_CLOUD_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./contract_orchestrator.db"
    
    # LangGraph Settings
    RECURSION_LIMIT: int = 5
    
    # Application Settings
    DEBUG: bool = False
    PROJECT_NAME: str = "ContractReviewOrchestrator"
    LLM_PROVIDER: str = "openai" # "openai" or "anthropic"
    PARSER_TYPE: str = "pypdf" # "pypdf" or "llamaparse"

    # External Tools
    SIMPLYRETS_KEY: str = "simplyrets"
    SIMPLYRETS_SECRET: str = "simplyrets"
    FUB_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

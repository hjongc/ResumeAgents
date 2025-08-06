"""
Default configuration for ResumeAgents framework.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean value from environment variable."""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_env_int(key: str, default: int = 0) -> int:
    """Get integer value from environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default

def get_env_float(key: str, default: float = 0.0) -> float:
    """Get float value from environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default

DEFAULT_CONFIG = {
    # LLM Models (from .env)
    "deep_think_llm": os.getenv("DEEP_THINK_LLM", "gpt-4o-mini"),
    "quick_think_llm": os.getenv("QUICK_THINK_LLM", "gpt-4o-mini"),
    
    # Agent Settings (from .env)
    "max_debate_rounds": get_env_int("MAX_DEBATE_ROUNDS", 2),
    "analysis_depth": os.getenv("ANALYSIS_DEPTH", "medium"),
    "online_tools": get_env_bool("ONLINE_TOOLS", True),
    "web_search_enabled": get_env_bool("WEB_SEARCH_ENABLED", True),
    
    # Document Settings (from .env)
    "document_type": os.getenv("DOCUMENT_TYPE", "resume"),
    "language": os.getenv("LANGUAGE", "ko"),
    "format": os.getenv("FORMAT", "markdown"),
    
    # Analysis Settings
    "include_company_analysis": get_env_bool("INCLUDE_COMPANY_ANALYSIS", True),
    "include_jd_analysis": get_env_bool("INCLUDE_JD_ANALYSIS", True),
    "include_trend_analysis": get_env_bool("INCLUDE_TREND_ANALYSIS", True),
    "include_experience_analysis": get_env_bool("INCLUDE_EXPERIENCE_ANALYSIS", True),
    
    # Quality Settings (from .env)
    "quality_threshold": get_env_float("QUALITY_THRESHOLD", 0.8),
    "max_revision_rounds": get_env_int("MAX_REVISION_ROUNDS", 3),
    
    # API Settings (from .env)
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": get_env_float("TEMPERATURE", 0.7),
    "max_tokens": get_env_int("MAX_TOKENS", 4000),
    
    # Debug Settings (from .env)
    "debug": get_env_bool("DEBUG", False),
    "verbose": get_env_bool("VERBOSE", False),
    "save_intermediate_results": get_env_bool("SAVE_INTERMEDIATE_RESULTS", True),
} 
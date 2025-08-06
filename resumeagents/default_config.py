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

def get_depth_config(research_depth: str) -> dict:
    """
    Get depth-specific configuration from environment variables.
    
    Args:
        research_depth: LOW, MEDIUM, or HIGH
        
    Returns:
        dict: Depth-specific configuration
    """
    depth = research_depth.upper()
    
    return {
        # ===== Depth별 모델 설정 =====
        "quick_think_model": os.getenv(f"{depth}_QUICK_THINK_MODEL", "gpt-4o-mini"),
        "deep_think_model": os.getenv(f"{depth}_DEEP_THINK_MODEL", "o4-mini"),
        "web_search_model": os.getenv(f"{depth}_WEB_SEARCH_MODEL", "gpt-4o-mini"),
        "evaluator_model": os.getenv(f"{depth}_EVALUATOR_MODEL", "gpt-4o-mini"),
        
        # ===== Depth별 기타 설정 =====
        "max_tokens": get_env_int(f"{depth}_MAX_TOKENS", 4000),
        "evaluator_max_tokens": get_env_int(f"{depth}_EVALUATOR_MAX_TOKENS", 2000),
        "quality_threshold": get_env_float(f"{depth}_QUALITY_THRESHOLD", 0.8),
        "max_revision_rounds": get_env_int(f"{depth}_MAX_REVISION_ROUNDS", 2),
        "evaluator_temperature": get_env_float(f"{depth}_EVALUATOR_TEMPERATURE", 0.3),
        
        # ===== 연구 깊이 =====
        "research_depth": depth
    }

DEFAULT_CONFIG = {
    # ===== 연구 깊이 설정 (핵심 설정) =====
    "research_depth": os.getenv("RESEARCH_DEPTH", "MEDIUM"),  # LOW, MEDIUM, HIGH
    
    # ===== 기본 설정 =====
    "temperature": get_env_float("TEMPERATURE", 0.7),
    
    # ===== 웹 검색 설정 =====
    "web_search_enabled": get_env_bool("WEB_SEARCH_ENABLED", True),
    "web_search_timeout": get_env_int("WEB_SEARCH_TIMEOUT", 60),
    "web_search_max_tokens": get_env_int("WEB_SEARCH_MAX_TOKENS", 3000),
    "web_search_retry_count": get_env_int("WEB_SEARCH_RETRY_COUNT", 3),
    
    # ===== 문서 설정 =====
    "document_type": os.getenv("DOCUMENT_TYPE", "resume"),
    "language": os.getenv("LANGUAGE", "ko"),
    "format": os.getenv("FORMAT", "markdown"),
    
    # ===== API 설정 =====
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    
    # ===== 디버그 설정 =====
    "debug": get_env_bool("DEBUG", False),
    "verbose": get_env_bool("VERBOSE", False),
} 
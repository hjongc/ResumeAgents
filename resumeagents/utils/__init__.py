"""
Utility functions and model management for ResumeAgents.
DEVELOPMENT_STRATEGY.md 준수 - ProfileManager 중심 구조
"""

import os
from typing import Dict, Any, Optional, List
from ..default_config import get_depth_config

# DEVELOPMENT_STRATEGY.md에 명시된 핵심 모듈들
from .profile_manager import ProfileManager
from .output_manager import OutputManager

# 간단한 텍스트 검증 클래스 (text_utils 대체)
class TextValidator:
    """간단한 텍스트 검증 클래스"""
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 10, max_length: int = 10000) -> bool:
        """텍스트 길이 검증"""
        return min_length <= len(text.strip()) <= max_length
    
    @staticmethod
    def clean_text(text: str) -> str:
        """텍스트 정리"""
        return text.strip()


def supports_temperature(model_name: str) -> bool:
    """
    Check if the model supports temperature parameter.
    
    Args:
        model_name: Name of the model to check
        
    Returns:
        True if model supports temperature, False otherwise
    """
    # o3, o4 시리즈는 temperature 지원하지 않음
    if model_name.startswith(("o3", "o4")):
        return False
    
    # GPT 모델들은 temperature 지원
    if model_name.startswith("gpt"):
        return True
    
    # Claude 모델들도 temperature 지원
    if model_name.startswith("claude"):
        return True
    
    # 기본적으로 지원한다고 가정
    return True


def get_model_for_agent(agent_name: str, config: Dict[str, Any]) -> str:
    """
    Get the appropriate model for a specific agent based on its type and configuration.
    DEVELOPMENT_STRATEGY.md의 에이전트 분류에 따른 모델 선택
    
    Args:
        agent_name: Name of the agent
        config: Configuration dictionary containing model settings
        
    Returns:
        Model name to use for the agent
    """
    # 웹 검색이 필요한 에이전트들 (Analysis Team)
    web_search_agents = [
        "company_analysis", "company_analyst", 
        "market_analysis", "market_analyst",
        "jd_analysis", "jd_analyst"
    ]
    
    # 깊은 사고가 필요한 에이전트들 (Strategy Team, Production Team)
    deep_think_agents = [
        "strength_research", "strength_researcher",
        "weakness_research", "weakness_researcher", 
        "quality_management", "quality_manager",
        "document_writing", "document_writer"
    ]
    
    # 빠른 처리가 필요한 에이전트들 (Matching Team, Guide Team)
    quick_think_agents = [
        "candidate_analysis", "candidate_analyst",
        "culture_analysis", "culture_analyst", 
        "trend_analysis", "trend_analyst",
        "question_guide", "experience_guide", "writing_guide"
    ]
    
    # 에이전트 유형에 따른 모델 선택
    if agent_name in web_search_agents:
        return config.get("web_search_model", "gpt-4o-mini")
    elif agent_name in deep_think_agents:
        return config.get("deep_think_model", "o4-mini")
    elif agent_name in quick_think_agents:
        return config.get("quick_think_model", "gpt-4o-mini")
    else:
        # 기본값: Quick Think 모델 사용
        return config.get("quick_think_model", "gpt-4o-mini")


def get_research_depth_config(research_depth: str) -> Dict[str, Any]:
    """
    Get comprehensive configuration for a specific research depth.
    DEVELOPMENT_STRATEGY.md의 Multi-depth configuration 구현
    
    Args:
        research_depth: Research depth level (LOW, MEDIUM, HIGH)
        
    Returns:
        Complete configuration dictionary for the depth level
    """
    depth_config = get_depth_config(research_depth)
    
    # 모델 분류를 위한 매핑 추가
    config_with_models = depth_config.copy()
    
    # DEVELOPMENT_STRATEGY.md에 명시된 설정들 추가
    config_with_models.update({
        # 기본 모델 정보는 이미 depth_config에 있음
        "web_search_enabled": True,
        "debug": False,
        "temperature": 0.7,
        "web_search_max_tokens": depth_config.get("max_tokens", 4000) - 1000  # 웹 검색용은 조금 적게
    })
    
    return config_with_models


# DEVELOPMENT_STRATEGY.md에 명시된 핵심 모듈들 Export
__all__ = [
    "ProfileManager",  # 문서에 명시된 핵심 모듈
    "OutputManager",   # 문서에 명시된 핵심 모듈
    "TextValidator",
    "supports_temperature",
    "get_model_for_agent", 
    "get_research_depth_config"
] 
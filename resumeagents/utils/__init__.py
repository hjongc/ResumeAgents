"""
Utilities for ResumeAgents framework.
"""

from .output_manager import OutputManager
from .profile_manager import ProfileManager
from .text_utils import TextValidator

# ===== 모델 분류 상수 =====
# Quick Think: 웹 검색 지원 모델 (빠른 처리)
QUICK_THINK_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4.1"]

# Deep Think: Reasoning 모델 (깊은 분석)
DEEP_THINK_MODELS = ["o1-mini", "o4-mini", "gpt-4o"]

# 웹 검색 지원 모델
WEB_SEARCH_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4.1"]

# Temperature 미지원 모델
TEMPERATURE_UNSUPPORTED_MODELS = [
    "gpt-4o-mini",
    "gpt-4o-mini-search-preview", 
    "o4-mini",
    "o1-mini",
    "o1-preview"
]

def supports_temperature(model_name: str) -> bool:
    """Check if a model supports temperature parameter."""
    for unsupported in TEMPERATURE_UNSUPPORTED_MODELS:
        if unsupported in model_name.lower():
            return False
    return True

def supports_web_search(model_name: str) -> bool:
    """Check if a model supports web search."""
    return model_name in WEB_SEARCH_MODELS

def get_research_depth_config(research_depth: str) -> dict:
    """
    Get configuration based on research depth preset from .env settings.
    
    Args:
        research_depth: LOW, MEDIUM, or HIGH
        
    Returns:
        dict: Configuration for the research depth
    """
    from ..default_config import get_depth_config
    
    # .env에서 depth별 설정 가져오기
    depth_config = get_depth_config(research_depth)
    
    # 단계별 모델 매핑 (작업 특성에 따라)
    analysis_models = {
        # 웹 검색이 필요한 에이전트들
        "company_analysis": depth_config["web_search_model"],
        "market_analysis": depth_config["web_search_model"], 
        "trend_analysis": depth_config["web_search_model"],
        
        # 빠른 처리가 필요한 에이전트들 (Quick Think)
        "jd_analysis": depth_config["quick_think_model"],
        
        # 깊은 추론이 필요한 에이전트들 (Deep Think)
        "candidate_analysis": depth_config["deep_think_model"],
        "culture_analysis": depth_config["deep_think_model"],
    }
    
    research_models = {
        # 연구는 깊은 추론이 필요
        "strength_research": depth_config["deep_think_model"],
        "weakness_research": depth_config["deep_think_model"],
    }
    
    production_models = {
        # 문서 작성은 깊은 추론이 필요
        "document_writing": depth_config["deep_think_model"],
        "quality_management": depth_config["deep_think_model"],
    }
    
    guide_models = {
        # 가이드 생성은 깊은 추론이 필요
        "question_guide": depth_config["deep_think_model"],
        "experience_guide": depth_config["deep_think_model"],
        "writing_guide": depth_config["deep_think_model"],
    }
    
    # 전체 설정 반환
    return {
        **depth_config,  # .env에서 가져온 기본 설정
        "analysis_models": analysis_models,
        "research_models": research_models,
        "production_models": production_models,
        "guide_models": guide_models,
    }

def get_model_for_agent(agent_name: str, config: dict) -> str:
    """
    Get appropriate model for specific agent.
    
    Args:
        agent_name: Name of the agent
        config: Configuration dictionary
        
    Returns:
        str: Model name to use
    """
    # 단계별 모델 설정에서 찾기
    for phase in ["analysis_models", "research_models", "production_models", "guide_models"]:
        phase_models = config.get(phase, {})
        if agent_name in phase_models:
            model = phase_models[agent_name]
            
            # 웹 검색이 필요한 에이전트인지 확인
            web_search_agents = ["company_analysis", "market_analysis", "trend_analysis"]
            if agent_name in web_search_agents and not supports_web_search(model):
                return config.get("web_search_model", "gpt-4o-mini")
            
            return model
    
    # 기본 모델 반환
    return config.get("deep_think_model", "o4-mini")

__all__ = [
    "OutputManager", 
    "ProfileManager", 
    "TextValidator", 
    "supports_temperature", 
    "supports_web_search", 
    "get_research_depth_config", 
    "get_model_for_agent"
] 
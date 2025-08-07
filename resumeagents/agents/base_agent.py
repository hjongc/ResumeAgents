"""
Base agent class and shared state definition for ResumeAgents framework.
통합 벡터DB 컨텍스트를 활용한 에이전트 베이스 클래스.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TYPE_CHECKING, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# TYPE_CHECKING을 사용하여 순환 import 방지
if TYPE_CHECKING:
    from ..utils.profile_manager import ProfileManager

# 모델 호환성 체크 함수 import
from ..utils import supports_temperature


class AgentState(BaseModel):
    """Shared state between agents."""
    
    company_name: str = ""
    job_title: str = ""
    job_description: str = ""
    candidate_info: Dict[str, Any] = Field(default_factory=dict)
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    quality_score: Optional[float] = None
    final_document: str = ""  # 최종 문서
    recommendations: List[str] = Field(default_factory=list)  # 추천사항
    profile_manager: Optional[Any] = Field(default=None, exclude=True)  # Any로 변경하여 타입 오류 방지
    
    # 통합 벡터DB 컨텍스트 (임시 저장용)
    agent_context: Optional[Dict[str, Any]] = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True  # ProfileManager 같은 커스텀 타입 허용


class BaseAgent(ABC):
    """Base class for all agents in ResumeAgents with unified vector DB context support."""
    
    def __init__(self, name: str, role: str, llm=None, config=None):
        self.name = name
        self.role = role
        self.config = config or {}
        
        # LLM 초기화
        if not llm:
            model_name = self.config.get("quick_think_llm", "gpt-4o-mini")
            llm_config = {
                "model": model_name,
                "max_tokens": self.config.get("max_tokens", 4000)
            }
            
            # 모델이 temperature를 지원하는 경우에만 추가
            if supports_temperature(model_name):
                llm_config["temperature"] = self.config.get("temperature", 0.7)
            
            self.llm = ChatOpenAI(**llm_config)
        else:
            self.llm = llm
    
    @abstractmethod
    async def analyze(self, state: AgentState) -> AgentState:
        """Perform analysis and return updated state."""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    def get_context_aware_prompt(self, state: AgentState, base_prompt: str) -> str:
        """
        통합 벡터DB 컨텍스트를 활용한 프롬프트 생성
        DEVELOPMENT_STRATEGY.md의 "Context-driven agent design" 구현
        
        Args:
            state: 현재 상태
            base_prompt: 기본 프롬프트
            
        Returns:
            컨텍스트가 강화된 프롬프트
        """
        # 통합 벡터DB 컨텍스트가 있는 경우
        if hasattr(state, 'agent_context') and state.agent_context:
            context = state.agent_context
            
            # 관련 엔트리가 있는 경우 프롬프트에 추가
            if context.get('relevant_entries'):
                enhanced_prompt = base_prompt + "\n\n=== 관련 프로필 정보 (벡터DB 검색 결과) ===\n"
                
                for i, entry in enumerate(context['relevant_entries'][:3], 1):  # 상위 3개만 사용
                    metadata = entry["metadata"]
                    score = entry["score"]
                    entry_type = metadata.get("type", "unknown")
                    data = metadata.get("data", {})
                    
                    enhanced_prompt += f"\n{i}. [{entry_type}] 관련도: {score:.3f}\n"
                    
                    if entry_type == "work_experience":
                        enhanced_prompt += f"   회사: {data.get('company', 'N/A')}\n"
                        enhanced_prompt += f"   직책: {data.get('position', 'N/A')}\n"
                        enhanced_prompt += f"   주요 업무: {', '.join(data.get('responsibilities', [])[:2])}\n"
                        
                        # 성과 정보
                        for achievement in data.get('achievements', [])[:1]:  # 첫 번째 성과만
                            enhanced_prompt += f"   성과: {achievement.get('description', '')}\n"
                            enhanced_prompt += f"   지표: {achievement.get('metrics', '')}\n"
                    
                    elif entry_type == "project":
                        enhanced_prompt += f"   프로젝트: {data.get('name', 'N/A')}\n"
                        enhanced_prompt += f"   설명: {data.get('description', 'N/A')[:100]}...\n"
                        enhanced_prompt += f"   역할: {data.get('role', 'N/A')}\n"
                    
                    elif entry_type == "skills":
                        skills_summary = []
                        for category, skills in data.items():
                            if isinstance(skills, list) and skills:
                                skills_summary.extend(skills[:3])  # 각 카테고리에서 3개씩
                        enhanced_prompt += f"   기술: {', '.join(skills_summary[:5])}\n"  # 총 5개까지
                    
                    elif entry_type == "education":
                        enhanced_prompt += f"   학교: {data.get('university', 'N/A')}\n"
                        enhanced_prompt += f"   전공: {data.get('major', 'N/A')}\n"
                    
                    elif entry_type == "career_goals":
                        enhanced_prompt += f"   단기목표: {data.get('short_term', 'N/A')}\n"
                        enhanced_prompt += f"   장기목표: {data.get('long_term', 'N/A')}\n"
                
                enhanced_prompt += "\n=== 관련 정보 끝 ===\n\n"
                enhanced_prompt += "위 관련 정보를 참고하여 더 구체적이고 개인화된 분석을 제공해주세요."
                
                return enhanced_prompt
        
        # 컨텍스트가 없는 경우 기본 프롬프트 반환
        return base_prompt
    
    def get_candidate_summary(self, state: AgentState) -> str:
        """
        지원자 정보 요약 (벡터DB 컨텍스트 우선, 폴백으로 candidate_info 사용)
        
        Args:
            state: 현재 상태
            
        Returns:
            지원자 정보 요약
        """
        # 통합 벡터DB 컨텍스트가 있는 경우
        if hasattr(state, 'agent_context') and state.agent_context:
            context = state.agent_context
            
            if context.get('relevant_entries'):
                summary_parts = []
                
                # 각 유형별로 요약
                work_experiences = []
                projects = []
                skills = []
                
                for entry in context['relevant_entries']:
                    metadata = entry["metadata"]
                    entry_type = metadata.get("type", "unknown")
                    data = metadata.get("data", {})
                    
                    if entry_type == "work_experience":
                        work_experiences.append(f"{data.get('company', '')} {data.get('position', '')}")
                    elif entry_type == "project":
                        projects.append(data.get('name', ''))
                    elif entry_type == "skills":
                        for category, skill_list in data.items():
                            if isinstance(skill_list, list):
                                skills.extend(skill_list[:2])  # 각 카테고리에서 2개씩
                
                if work_experiences:
                    summary_parts.append(f"주요 경력: {', '.join(work_experiences[:3])}")
                if projects:
                    summary_parts.append(f"주요 프로젝트: {', '.join(projects[:3])}")
                if skills:
                    summary_parts.append(f"주요 기술: {', '.join(skills[:5])}")
                
                return " | ".join(summary_parts) if summary_parts else "관련 정보 없음"
        
        # 폴백: 기본 candidate_info 사용
        candidate_info = state.candidate_info
        summary_parts = []
        
        if candidate_info.get("work_experience"):
            work_exp = candidate_info["work_experience"][0]  # 첫 번째 경력
            summary_parts.append(f"경력: {work_exp.get('company', '')} {work_exp.get('position', '')}")
        
        if candidate_info.get("skills"):
            skills = candidate_info["skills"]
            all_skills = []
            for skill_category in skills.values():
                if isinstance(skill_category, list):
                    all_skills.extend(skill_category[:2])
            if all_skills:
                summary_parts.append(f"기술: {', '.join(all_skills[:3])}")
        
        return " | ".join(summary_parts) if summary_parts else "기본 프로필 정보"
    
    async def _call_llm(self, messages: List, **kwargs) -> str:
        """Call the LLM with given messages."""
        response = await self.llm.ainvoke(messages, **kwargs)
        return response.content
    
    def _create_messages(self, user_prompt: str) -> List:
        """Create messages for LLM call."""
        return [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=user_prompt)
        ]
    
    def log(self, message: str):
        """Log a message if debug is enabled."""
        if self.config.get("debug", False):
            print(f"[{self.name}] {message}") 
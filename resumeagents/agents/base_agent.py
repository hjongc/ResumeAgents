"""
Base agent class and shared state definition for ResumeAgents framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TYPE_CHECKING, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# TYPE_CHECKING을 사용하여 순환 import 방지
if TYPE_CHECKING:
    from ..utils.profile_manager import ProfileManager


class AgentState(BaseModel):
    """Shared state between agents."""
    
    company_name: str = ""
    job_title: str = ""
    job_description: str = ""
    candidate_info: Dict[str, Any] = Field(default_factory=dict)
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    quality_score: Optional[float] = None
    profile_manager: Optional['ProfileManager'] = Field(default=None, exclude=True)  # 직렬화에서 제외
    
    class Config:
        arbitrary_types_allowed = True  # ProfileManager 같은 커스텀 타입 허용


class BaseAgent(ABC):
    """Base class for all agents in ResumeAgents."""
    
    def __init__(
        self,
        name: str,
        role: str,
        llm: Optional[ChatOpenAI] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.role = role
        self.llm = llm or ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=4000
        )
        self.config = config or {}
        
    @abstractmethod
    async def analyze(self, state: AgentState) -> AgentState:
        """Perform analysis and return updated state."""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
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
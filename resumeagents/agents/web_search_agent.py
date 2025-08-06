"""
Web Search enabled base agent for ResumeAgents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json


class WebSearchBaseAgent(ABC):
    """Base class for web search enabled agents in ResumeAgents."""
    
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
    async def analyze(self, state):
        """Perform analysis and return updated state."""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    async def _call_llm_with_web_search(self, messages: List, search_queries: List[str] = None) -> str:
        """Call the LLM with web search capability."""
        if search_queries and self.config.get("web_search_enabled", True):
            # Add web search tool to the call
            tools = [
                {
                    "type": "web_search"
                }
            ]
            # Add search queries to the prompt
            search_prompt = f"\n\nPlease search for the following information:\n"
            for i, query in enumerate(search_queries):
                search_prompt += f"{i+1}. {query}\n"
            
            # Add search prompt to the last message
            if messages and hasattr(messages[-1], 'content'):
                messages[-1].content += search_prompt
            
            response = await self.llm.ainvoke(messages, tools=tools)
        else:
            response = await self.llm.ainvoke(messages)
        return response.content
    
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
    
    def _generate_search_queries(self, company_name: str, job_title: str, context: str = "") -> List[str]:
        """Generate relevant search queries for web search."""
        queries = []
        
        # Company related queries
        queries.append(f"{company_name} 최신 뉴스 2025")
        queries.append(f"{company_name} 재무제표 2025")
        queries.append(f"{company_name} 기업 문화")
        queries.append(f"{company_name} 사업 모델")
        
        # Job/Industry related queries
        queries.append(f"{job_title} 직무 요구사항 2025")
        queries.append(f"{job_title} 시장 동향")
        queries.append(f"{company_name} {job_title} 채용")
        
        # Market related queries
        queries.append(f"{company_name} 경쟁사 분석")
        queries.append(f"{company_name} 산업 트렌드")
        
        return queries 
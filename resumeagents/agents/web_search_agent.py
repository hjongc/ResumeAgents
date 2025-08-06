"""
Web Search Base Agent for ResumeAgents.
"""

from typing import List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from openai import OpenAI
from .base_agent import BaseAgent, AgentState
from ..utils import WEB_SEARCH_MODELS, supports_web_search


class WebSearchBaseAgent(BaseAgent):
    """Base class for agents that support web search functionality."""
    
    def __init__(self, name: str, role: str, llm=None, config=None):
        super().__init__(name, role, llm, config)
        
        # OpenAI client for web search
        if config and config.get("openai_api_key"):
            self.client = OpenAI(api_key=config.get("openai_api_key"))
        else:
            self.client = None
    
    def _call_llm_with_web_search(self, prompt: str, query: str) -> str:
        """Call LLM with web search capability using new OpenAI API."""
        if not self.config.get("web_search_enabled", True):
            # Web search disabled, use regular LLM call
            return self.llm.invoke(prompt).content
        
        if not self.client:
            # No OpenAI client available, fallback to regular LLM
            return self.llm.invoke(prompt).content
        
        # 웹 검색 설정 가져오기
        web_search_model = self.config.get("web_search_model", "gpt-4o-mini")
        web_search_timeout = self.config.get("web_search_timeout", 30)
        retry_count = self.config.get("web_search_retry_count", 2)
        
        # 웹 검색 지원 모델 체크 및 대체
        if not supports_web_search(web_search_model):
            print(f"⚠️  모델 '{web_search_model}'은 웹 검색을 지원하지 않습니다. 'gpt-4o-mini'로 대체합니다.")
            web_search_model = "gpt-4o-mini"
        
        for attempt in range(retry_count + 1):
            try:
                # 웹 검색을 포함한 프롬프트 작성
                search_input = f"""
{prompt}

Please search for recent information about: {query}

Use web search to find the most current and accurate information available.
"""
                
                print(f"웹 검색 시도 {attempt + 1}/{retry_count + 1} - 모델: {web_search_model}")
                
                # OpenAI responses API 사용 (올바른 형식)
                response = self.client.responses.create(
                    model=web_search_model,
                    tools=[{"type": "web_search"}],  # 올바른 타입
                    input=search_input
                )
                
                return response.output_text
                
            except Exception as e:
                print(f"웹 검색 실패 (시도 {attempt + 1}/{retry_count + 1}): {e}")
                if attempt == retry_count:
                    print("모든 웹 검색 시도 실패 - 기본 LLM 분석으로 전환...")
                    # Fallback to regular LLM call
                    return self.llm.invoke(prompt).content
                else:
                    print(f"재시도 중... ({attempt + 2}/{retry_count + 1})")
                    continue
        
        # 이 지점에 도달하면 모든 시도가 실패한 것
        return self.llm.invoke(prompt).content
    
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
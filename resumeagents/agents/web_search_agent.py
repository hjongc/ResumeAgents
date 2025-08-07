"""
Web Search Base Agent for ResumeAgents.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentState
from ..utils import supports_temperature


class WebSearchBaseAgent(BaseAgent):
    """Base class for agents that need web search capabilities."""
    
    def __init__(self, name: str, role: str, llm=None, config=None):
        super().__init__(name, role, llm, config)
        self.web_search_enabled = config.get("web_search_enabled", True)
        self.max_retries = config.get("web_search_retry_count", 3)
    
    def supports_web_search(self, model_name: str) -> bool:
        """Check if the model supports web search capabilities."""
        # GPT models generally support web search
        if model_name.startswith("gpt"):
            return True
        
        # Add other web search capable models here
        web_search_models = ["gpt-4o", "gpt-4o-mini", "gpt-4.1"]
        return model_name in web_search_models
    
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform web search using the LLM's web search capabilities.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        if not self.web_search_enabled:
            self.log("Web search disabled, skipping")
            return []
        
        model_name = getattr(self.llm, 'model_name', 'unknown')
        if not self.supports_web_search(model_name):
            self.log(f"Model {model_name} doesn't support web search")
            return []
        
        search_prompt = f"""
Please search for information about: {query}

Provide the most relevant and up-to-date information available. Focus on:
1. Official company information
2. Recent news and developments  
3. Industry insights and trends
4. Key facts and statistics

Format your response as a structured summary with key points.
"""
        
        for attempt in range(self.max_retries):
            try:
                self.log(f"Web search attempt {attempt + 1}: {query}")
                
                # Use the LLM for web search
                messages = self._create_messages(search_prompt)
                search_result = await self._call_llm(messages)
                
                # Parse and structure the result
                return [{
                    "query": query,
                    "content": search_result,
                    "source": "web_search",
                    "timestamp": "2024-01-15"
                }]
                
            except Exception as e:
                self.log(f"Web search attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    self.log("All web search attempts failed, proceeding without web data")
                    return []
                
                # Wait before retry
                await asyncio.sleep(1)
        
        return []
    
    async def analyze_with_web_search(self, state: AgentState, search_queries: List[str]) -> Dict[str, Any]:
        """
        Perform analysis with web search support.
        
        Args:
            state: Current agent state
            search_queries: List of queries to search for
            
        Returns:
            Dictionary containing search results
        """
        web_results = {}
        
        for query in search_queries:
            results = await self.search_web(query)
            if results:
                web_results[query] = results
                self.log(f"Web search successful for: {query}")
            else:
                self.log(f"Web search failed for: {query}")
        
        return web_results 
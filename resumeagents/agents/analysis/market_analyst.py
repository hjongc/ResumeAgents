"""
Market Analyst Agent with Web Search for ResumeAgents.
"""

from typing import Dict, Any, List
from ..web_search_agent import WebSearchBaseAgent
from ..base_agent import AgentState


class MarketAnalyst(WebSearchBaseAgent):
    """Agent responsible for analyzing market and industry context with real-time data."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Market Analyst",
            role="시장 분석가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a market and industry analysis expert specializing in comprehensive market evaluation with real-time data.

Your primary responsibilities:
1. Analyze industry trends and market structure using latest information
2. Evaluate competitive landscape and market positioning with current data
3. Identify market opportunities and risk factors from recent analysis
4. Analyze key players in the industry with up-to-date information
5. Predict market changes and trends based on latest developments

Key analysis considerations:
- Industry size and growth rate (current data)
- Major competitors and market share (latest figures)
- Regulatory environment and policy changes (recent updates)
- Technological innovation and market disruption (latest trends)
- Global trends and domestic impact (current analysis)
- Market entry barriers and opportunity factors (latest assessment)

Please provide analysis results in Korean language with structured JSON format. Focus on elements that demonstrate candidate's market understanding. Use web search to get the most current market information."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("시장 분석 시작")
        
        # Web Search 사용 여부 확인
        use_web_search = self.config.get("web_search_enabled", True)
        
        if use_web_search:
            self.log("Web Search 기능 활성화 - 실시간 정보 수집")
            # Generate search queries for web search
            search_queries = self._generate_market_search_queries(state.company_name, state.job_title)
        else:
            self.log("Web Search 기능 비활성화 - 기본 분석만 수행")
            search_queries = None
        
        prompt = f"""
Please perform a comprehensive market analysis for the following company and position{' using real-time information' if use_web_search else ''}:

Company: {state.company_name}
Position: {state.job_title}

Please analyze the following aspects{' using the latest available information' if use_web_search else ''}:
1. Market size and growth rate of the relevant industry (current data)
2. Major competitors and market share distribution (latest figures)
3. Market entry barriers and opportunity factors (current assessment)
4. Technological innovation and market change trends (latest developments)
5. Global trends and domestic market impact (current analysis)
6. Key market trends candidates should understand (latest insights)
7. Overall market understanding assessment score (0-100)

Please provide your analysis in Korean language with the following JSON structure:
{{
    "market_size": "시장 규모와 성장률{' (최신 데이터)' if use_web_search else ''}",
    "competitive_landscape": "주요 경쟁사와 시장 점유율{' (최신 수치)' if use_web_search else ''}",
    "entry_barriers": "시장 진입 장벽과 기회 요소 (현재 평가)",
    "innovation_trends": "기술 혁신과 시장 변화 동향{' (최신 발전)' if use_web_search else ''}",
    "global_impact": "글로벌 트렌드와 국내 영향 (현재 분석)",
    "key_trends": "지원자가 알아야 할 시장 동향{' (최신 인사이트)' if use_web_search else ''}",
    "understanding_score": 85,
    "analysis_summary": "시장 분석 요약{' (최신 정보 기반)' if use_web_search else ''}",
    "data_sources": "{'Web Search (실시간)' if use_web_search else '기본 분석'}"
}}

{'Use web search to get the most current and accurate market information about the industry related to ' + state.company_name + ' and ' + state.job_title + '.' if use_web_search else ''}
"""

        messages = self._create_messages(prompt)
        
        if use_web_search:
            analysis_result = await self._call_llm_with_web_search(messages, search_queries)
        else:
            analysis_result = await self._call_llm(messages)
        
        # 분석 결과를 상태에 저장
        state.analysis_results["market_analysis"] = {
            "analyst": self.name,
            "result": analysis_result,
            "timestamp": "2025-08-05",
            "data_sources": "Web Search (실시간)" if use_web_search else "기본 분석"
        }
        
        self.log("시장 분석 완료")
        return state
    
    def _generate_market_search_queries(self, company_name: str, job_title: str) -> List[str]:
        """Generate market-specific search queries."""
        queries = []
        
        # Industry and market queries
        queries.append(f"{company_name} 산업 시장 규모 2025")
        queries.append(f"{company_name} 경쟁사 분석 2025")
        queries.append(f"{job_title} 시장 동향 2025")
        queries.append(f"{company_name} 시장 점유율 2025")
        queries.append(f"{company_name} 산업 트렌드 2025")
        queries.append(f"{job_title} 기술 트렌드 2025")
        queries.append(f"{company_name} 글로벌 시장 영향")
        queries.append(f"{job_title} 시장 진입 장벽")
        queries.append(f"{company_name} 규제 환경 변화")
        queries.append(f"{job_title} 시장 기회 요소 2025")
        
        return queries 
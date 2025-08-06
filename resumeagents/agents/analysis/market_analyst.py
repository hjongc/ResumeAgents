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

Please provide analysis results in Korean with structured JSON format. Focus on market insights that would be valuable for job candidates. Use web search to get the most current market information."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("시장 분석 시작")
        
        # 분석 깊이 설정 가져오기
        analysis_depth = self.config.get("analysis_depth", "medium")
        
        # Web Search 사용 여부 확인
        use_web_search = self.config.get("web_search_enabled", True)
        
        if use_web_search:
            self.log("Web Search 기능 활성화 - 실시간 정보 수집")
        else:
            self.log("Web Search 기능 비활성화 - 기본 분석만 수행")
        
        # 분석 깊이에 따른 프롬프트 조정
        depth_instruction = ""
        if analysis_depth == "low":
            depth_instruction = "핵심적인 시장 정보만 간단히 분석해주세요."
        elif analysis_depth == "medium":
            depth_instruction = "균형잡힌 시장 분석을 해주세요."
        elif analysis_depth == "high":
            depth_instruction = "매우 상세하고 깊이 있는 시장 분석을 해주세요. 최신 시장 데이터와 트렌드를 최대한 활용해주세요."
        
        prompt = f"""
Please perform a comprehensive market analysis for the following company and position{' using real-time information' if use_web_search else ''}:

Company: {state.company_name}
Position: {state.job_title}

{depth_instruction}

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
    "data_sources": "{'Web Search (실시간)' if use_web_search else '기본 분석'}",
    "analysis_depth": "{analysis_depth}"
}}

{'Use web search to get the most current and accurate market information about the industry related to ' + state.company_name + ' and ' + state.job_title + '.' if use_web_search else ''}
"""

        if use_web_search:
            # 웹 검색을 통한 실시간 정보 수집
            search_query = f"{state.company_name} market analysis industry trends 2025"
            try:
                web_result = self._call_llm_with_web_search(prompt, search_query)
                analysis_result = web_result
            except Exception as e:
                self.log(f"Web search failed, using standard analysis: {e}")
                messages = self._create_messages(prompt)
                analysis_result = await self._call_llm(messages)
        else:
            messages = self._create_messages(prompt)
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
"""
Company Analyst Agent with Web Search for ResumeAgents.
"""

from typing import Dict, Any, List
from ..web_search_agent import WebSearchBaseAgent
from ..base_agent import AgentState


class CompanyAnalyst(WebSearchBaseAgent):
    """Agent responsible for analyzing target companies with real-time data."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Company Analyst",
            role="기업 분석가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a company analysis expert specializing in comprehensive business evaluation with real-time data.

Your primary responsibilities:
1. Analyze company business models and core values using latest information
2. Evaluate financial status and performance metrics from recent data
3. Assess company culture and talent development policies
4. Analyze market position and competitive advantages
5. Identify growth potential and future strategies

Key analysis considerations:
- Company's core values and mission (from latest sources)
- Business model and revenue streams (current data)
- Financial performance and investment trends (recent reports)
- Organizational culture and talent development (latest insights)
- Market position and competitive differentiation (current analysis)
- ESG activities and social responsibility (recent initiatives)
- Growth opportunities and risk factors (latest trends)

Please provide analysis results in English with structured JSON format. Focus on elements that would be favorable for job candidates. Use web search to get the most current information about the company."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("기업 분석 시작")
        
        # Web Search 사용 여부 확인
        use_web_search = self.config.get("web_search_enabled", True)
        
        if use_web_search:
            self.log("Web Search 기능 활성화 - 실시간 정보 수집")
            # Generate search queries for web search
            search_queries = self._generate_company_search_queries(state.company_name)
        else:
            self.log("Web Search 기능 비활성화 - 기본 분석만 수행")
            search_queries = None
        
        prompt = f"""
Perform comprehensive analysis of the following company{' using real-time information' if use_web_search else ''}:

Company: {state.company_name}
Position: {state.job_title}

Analyze the following aspects{' using latest available information' if use_web_search else ''}:
1. Company overview and business model (current state)
2. Core values and corporate culture (latest insights)
3. Financial status and performance (recent data)
4. Market position and competitiveness (current analysis)
5. Talent development and growth policies (latest initiatives)
6. Elements favorable to job candidates (current opportunities)
7. Overall company attractiveness score (0-100)

Provide analysis in Korean with the following JSON structure:
{{
    "company_overview": "Company overview and business model{' (latest info)' if use_web_search else ''} - in Korean",
    "core_values": "Core values and corporate culture{' (latest insights)' if use_web_search else ''} - in Korean",
    "financial_status": "Financial status and performance{' (latest data)' if use_web_search else ''} - in Korean",
    "market_position": "Market position and competitiveness - in Korean",
    "talent_policies": "Talent development policies{' (latest initiatives)' if use_web_search else ''} - in Korean",
    "candidate_advantages": "Advantages for job candidates - in Korean",
    "attractiveness_score": 85,
    "analysis_summary": "Comprehensive analysis summary{' (based on latest info)' if use_web_search else ''} - in Korean",
    "data_sources": "{'Web Search (real-time)' if use_web_search else 'Basic analysis'}"
}}

{'Use web search to get current and accurate information about ' + state.company_name + '.' if use_web_search else ''}
Important: All text content should be in Korean for end users.
"""

        messages = self._create_messages(prompt)
        
        if use_web_search:
            analysis_result = await self._call_llm_with_web_search(messages, search_queries)
        else:
            analysis_result = await self._call_llm(messages)
        
        # 분석 결과를 상태에 저장
        state.analysis_results["company_analysis"] = {
            "analyst": self.name,
            "result": analysis_result,
            "timestamp": "2025-08-05",
            "data_sources": "Web Search (실시간)" if use_web_search else "기본 분석"
        }
        
        self.log("기업 분석 완료")
        return state
    
    def _generate_company_search_queries(self, company_name: str) -> List[str]:
        """Generate company-specific search queries."""
        queries = []
        
        # Company specific queries
        queries.append(f"{company_name} 최신 뉴스 2025")
        queries.append(f"{company_name} 재무제표 2025")
        queries.append(f"{company_name} 기업 문화 2025")
        queries.append(f"{company_name} 사업 모델 2025")
        queries.append(f"{company_name} 인재 육성 정책")
        queries.append(f"{company_name} ESG 정책 2025")
        queries.append(f"{company_name} 경쟁사 분석")
        queries.append(f"{company_name} 시장 점유율 2025")
        queries.append(f"{company_name} 성장 전략 2025")
        queries.append(f"{company_name} 채용 정보 2025")
        
        return queries 
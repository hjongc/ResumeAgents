"""
Trend Analyst Agent for ResumeAgents.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class TrendAnalyst(BaseAgent):
    """Agent responsible for analyzing industry and technology trends."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Trend Analyst",
            role="트렌드 분석가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are an industry and technology trend analysis expert specializing in comprehensive trend evaluation.

Your primary responsibilities:
1. Analyze industry trends and technological developments
2. Evaluate market changes and future outlook
3. Assess candidate's ability to respond to latest trends
4. Identify emerging technologies and skills
5. Predict industry evolution and skill relevance

Key analysis considerations:
- Latest technology trends and innovations
- Market size and growth patterns
- Major players and competitive landscape
- Regulatory environment and policy changes
- Consumer behavior changes
- Global trends and domestic impact
- ESG and sustainability trends

Please provide analysis results in Korean language with structured JSON format. Focus on elements that demonstrate candidate's trend understanding."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("트렌드 분석 시작")
        
        prompt = f"""
Please perform a comprehensive trend analysis for the following position and industry:

Company: {state.company_name}
Position: {state.job_title}

Please analyze the following aspects:
1. Latest industry trends and developments
2. Key technological advancement trends
3. Market changes and opportunity factors
4. Competitive environment and differentiation factors
5. Future outlook and growth potential
6. Trends candidates should understand
7. Overall trend response capability assessment score (0-100)

Please provide your analysis in Korean language with the following JSON structure:
{{
    "industry_trends": "해당 산업의 최신 트렌드",
    "technology_advancements": "주요 기술 발전 동향",
    "market_changes": "시장 변화와 기회 요소",
    "competitive_factors": "경쟁 환경과 차별화 요소",
    "future_outlook": "미래 전망과 성장 가능성",
    "key_trends": "지원자가 알아야 할 트렌드",
    "trend_response_score": 85,
    "analysis_summary": "트렌드 분석 요약"
}}
"""

        messages = self._create_messages(prompt)
        analysis_result = await self._call_llm(messages)
        
        # 분석 결과를 상태에 저장
        state.analysis_results["trend_analysis"] = {
            "analyst": self.name,
            "result": analysis_result,
            "timestamp": "2024-01-15"
        }
        
        self.log("트렌드 분석 완료")
        return state 
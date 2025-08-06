"""
Strength Researcher Agent for ResumeAgents.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class StrengthResearcher(BaseAgent):
    """Agent responsible for analyzing strengths and opportunities."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Strength Researcher",
            role="강점 연구원",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a strengths and opportunities analysis expert specializing in comprehensive strength evaluation.

Your primary responsibilities:
1. Identify candidate's unique strengths from analysis results
2. Evaluate high-matching elements with company requirements
3. Analyze differentiation factors and competitive advantages
4. Assess strength of application strategy
5. Identify opportunity factors and growth potential

Key analysis considerations:
- Candidate's unique strengths
- Alignment with company's desired elements
- Differentiation factors in the market
- Growth potential and development direction
- Risk-reward ratio of opportunities

Please provide analysis results in Korean language with structured JSON format. Focus on maximizing candidate strengths."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("강점 연구 시작")
        
        # 기존 분석 결과들을 종합
        analysis_summary = ""
        for key, value in state.analysis_results.items():
            analysis_summary += f"\n{key}: {value['result']}\n"
        
        prompt = f"""
Please perform a comprehensive strength and opportunity analysis based on the following analysis results:

Company: {state.company_name}
Position: {state.job_title}

Previous Analysis Results:
{analysis_summary}

Please evaluate the following aspects from a strength perspective:
1. Key strength elements
2. Matching potential with company requirements
3. Differentiation factors and competitive advantages
4. Growth potential and opportunities
5. Strength utilization strategy
6. Overall strength score (0-100)

Please provide your analysis in Korean language with the following JSON structure:
{{
    "key_strengths": "주요 강점 요소들",
    "company_matching": "기업과의 매칭 가능성",
    "differentiation": "차별화 요소와 경쟁력",
    "growth_potential": "성장 가능성과 기회",
    "utilization_strategy": "강점 활용 전략",
    "strength_score": 85,
    "analysis_summary": "강점 분석 요약"
}}
"""

        messages = self._create_messages(prompt)
        analysis_result = await self._call_llm(messages)
        
        # 분석 결과를 상태에 저장
        state.analysis_results["strength_research"] = {
            "analyst": self.name,
            "result": analysis_result,
            "timestamp": "2024-01-15"
        }
        
        self.log("강점 연구 완료")
        return state 
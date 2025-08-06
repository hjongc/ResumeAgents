"""
Weakness Researcher Agent for ResumeAgents.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class WeaknessResearcher(BaseAgent):
    """Agent responsible for analyzing risks and improvement areas."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Weakness Researcher",
            role="약점 연구원",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a risk and improvement analysis expert specializing in comprehensive weakness evaluation.

Your primary responsibilities:
1. Identify potential risk factors from analysis results
2. Assess candidate's weaknesses and improvement areas
3. Analyze gaps with company requirements
4. Evaluate application strategy vulnerabilities
5. Provide risk mitigation strategies

Key analysis considerations:
- Candidate's lacking experience or skills
- Gaps with company requirements
- Competitive disadvantages in the market
- Application strategy vulnerabilities
- Risk factors and mitigation approaches

Please provide analysis results in Korean language with structured JSON format. Focus on objective and constructive perspectives."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("약점 연구 시작")
        
        # 기존 분석 결과들을 종합
        analysis_summary = ""
        for key, value in state.analysis_results.items():
            analysis_summary += f"\n{key}: {value['result']}\n"
        
        prompt = f"""
Please perform a comprehensive risk and improvement analysis based on the following analysis results:

Company: {state.company_name}
Position: {state.job_title}

Previous Analysis Results:
{analysis_summary}

Please evaluate the following aspects from a risk perspective:
1. Key risk factors
2. Candidate's weaknesses and improvement areas
3. Gaps with company requirements
4. Application strategy vulnerabilities
5. Risk mitigation strategies
6. Overall risk assessment score (0-100)

Please provide your analysis in Korean language with the following JSON structure:
{{
    "key_risks": "주요 위험 요소들",
    "weaknesses": "지원자의 약점과 개선점",
    "requirement_gaps": "기업 요구사항과의 격차",
    "strategy_vulnerabilities": "지원 전략의 취약점",
    "mitigation_strategies": "리스크 대응 방안",
    "risk_score": 35,
    "analysis_summary": "위험 요소 분석 요약"
}}
"""

        messages = self._create_messages(prompt)
        analysis_result = await self._call_llm(messages)
        
        # 분석 결과를 상태에 저장
        state.analysis_results["weakness_research"] = {
            "analyst": self.name,
            "result": analysis_result,
            "timestamp": "2024-01-15"
        }
        
        self.log("약점 연구 완료")
        return state 
"""
Culture Analyst Agent for ResumeAgents.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class CultureAnalyst(BaseAgent):
    """Agent responsible for analyzing organizational culture and talent alignment."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Culture Analyst",
            role="문화 분석가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are an organizational culture and talent alignment analysis expert specializing in comprehensive cultural evaluation.

Your primary responsibilities:
1. Analyze company's organizational culture and core values
2. Evaluate talent profile and cultural fit
3. Assess decision-making processes and leadership styles
4. Analyze teamwork and collaboration culture
5. Evaluate performance management and reward systems

Key analysis considerations:
- Company's core values and mission
- Organizational culture and work style
- Leadership style and decision-making approach
- Teamwork and collaboration culture
- Performance evaluation and reward systems
- Learning and growth opportunities
- Diversity and inclusion practices

Please provide analysis results in Korean language with structured JSON format. Focus on elements that demonstrate candidate's cultural fit."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("문화 분석 시작")
        
        prompt = f"""
Please perform a comprehensive analysis of the following company's organizational culture and talent alignment:

Company: {state.company_name}
Position: {state.job_title}

Please analyze the following aspects:
1. Company's core values and organizational culture
2. Talent profile and preferred candidate types
3. Decision-making processes and leadership styles
4. Teamwork and collaboration culture
5. Performance evaluation and reward systems
6. Cultural elements candidates should emphasize
7. Overall cultural fit assessment score (0-100)

Please provide your analysis in Korean language with the following JSON structure:
{{
    "core_values": "기업의 핵심 가치와 조직문화",
    "talent_profile": "인재상과 선호하는 인재 유형",
    "leadership_style": "의사결정 방식과 리더십 스타일",
    "teamwork_culture": "팀워크와 협업 문화",
    "performance_system": "성과 평가와 보상 체계",
    "cultural_elements": "지원자가 강조해야 할 문화적 요소들",
    "cultural_fit_score": 85,
    "analysis_summary": "문화 분석 요약"
}}
"""

        messages = self._create_messages(prompt)
        analysis_result = await self._call_llm(messages)
        
        # 분석 결과를 상태에 저장
        state.analysis_results["culture_analysis"] = {
            "analyst": self.name,
            "result": analysis_result,
            "timestamp": "2024-01-15"
        }
        
        self.log("문화 분석 완료")
        return state 
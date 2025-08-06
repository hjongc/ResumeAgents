"""
Candidate Analyst Agent for ResumeAgents.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class CandidateAnalyst(BaseAgent):
    """Agent responsible for analyzing candidate experience and skills."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Candidate Analyst",
            role="지원자 분석가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a candidate experience and skills analysis expert specializing in comprehensive candidate evaluation.

Your primary responsibilities:
1. Analyze candidate's career history and experience
2. Evaluate core skills and competencies
3. Assess achievements and performance metrics
4. Evaluate alignment with target position
5. Identify strengths and improvement areas

Key analysis considerations:
- Career continuity and development direction
- Core skills and expertise
- Specific achievements and performance metrics
- Teamwork and leadership experience
- Problem-solving ability and innovation
- Learning ability and adaptability
- Job-candidate matching potential

Please provide analysis results in Korean language with structured JSON format. Focus on maximizing candidate strengths and clearly showing alignment with the target position."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("지원자 분석 시작")
        
        candidate_info = state.candidate_info
        
        prompt = f"""
Please perform a comprehensive analysis of the following candidate's experience and skills:

Company: {state.company_name}
Position: {state.job_title}

Candidate Information:
{candidate_info}

Please analyze the following aspects:
1. Core career experience and background
2. Key skills and competencies
3. Specific achievements and performance metrics
4. Alignment with target position
5. Strengths and differentiation factors
6. Areas for improvement
7. Overall job-candidate matching score (0-100)

Please provide your analysis in Korean language with the following JSON structure:
{{
    "core_experience": "핵심 경력과 경험",
    "key_skills": "주요 스킬과 역량",
    "achievements": "구체적인 성과와 업적",
    "position_alignment": "지원 직무와의 연관성",
    "strengths": "강점과 차별화 요소",
    "improvement_areas": "개선이 필요한 영역",
    "matching_score": 85,
    "analysis_summary": "지원자 분석 요약"
}}
"""

        messages = self._create_messages(prompt)
        analysis_result = await self._call_llm(messages)
        
        # 분석 결과를 상태에 저장
        state.analysis_results["candidate_analysis"] = {
            "analyst": self.name,
            "result": analysis_result,
            "timestamp": "2024-01-15"
        }
        
        self.log("지원자 분석 완료")
        return state 
"""
Candidate Analyst Agent for ResumeAgents.
통합 벡터DB 컨텍스트를 활용한 지원자 분석 에이전트.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class CandidateAnalyst(BaseAgent):
    """Agent responsible for analyzing candidate experience and skills with unified vector DB context."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Candidate Analyst",
            role="지원자 분석가",
            llm=llm,
            config=config
        )

    def get_system_prompt(self) -> str:
        return """You are a candidate experience and skills analysis expert specializing in comprehensive candidate evaluation with context-driven insights.

Your primary responsibilities:
1. Analyze candidate's career history and experience using relevant profile data
2. Evaluate core skills and competencies based on actual experience
3. Assess achievements and performance metrics with concrete evidence
4. Evaluate alignment with target position using specific examples
5. Identify strengths and improvement areas with supporting data

Key analysis considerations:
- Career continuity and development direction (based on actual work history)
- Core skills and expertise (derived from project and work experience)
- Specific achievements and performance metrics (quantifiable results)
- Teamwork and leadership experience (concrete examples)
- Problem-solving ability and innovation (demonstrated through projects)
- Learning ability and adaptability (career progression evidence)
- Job-candidate matching potential (alignment analysis)

IMPORTANT: Use the provided relevant profile information to make your analysis more specific and evidence-based. Reference actual experiences, projects, and achievements when available.

Please provide analysis results in Korean language with structured JSON format. Focus on maximizing candidate strengths and clearly showing alignment with the target position using concrete examples from their background."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("지원자 분석 시작 (통합 벡터DB 컨텍스트 활용)")
        
        # 기본 프롬프트 생성
        base_prompt = f"""
Please perform a comprehensive analysis of the following candidate's experience and skills:

Company: {state.company_name}
Position: {state.job_title}

Job Description:
{state.job_description}

Candidate Summary: {self.get_candidate_summary(state)}

Please analyze the following aspects:
1. Core career experience and background (with specific examples)
2. Key skills and competencies (evidenced by actual work)
3. Specific achievements and performance metrics (quantifiable results)
4. Alignment with target position (detailed matching analysis)
5. Strengths and differentiation factors (unique value proposition)
6. Areas for improvement (constructive development areas)
7. Overall job-candidate matching score (0-100) with reasoning

Please provide your analysis in Korean language with the following JSON structure:
{{
    "core_experience": "핵심 경력과 경험 (구체적 사례 포함)",
    "key_skills": "주요 스킬과 역량 (실제 업무 기반)",
    "achievements": "구체적인 성과와 업적 (정량적 지표 포함)",
    "position_alignment": "지원 직무와의 연관성 (상세 매칭 분석)",
    "strengths": "강점과 차별화 요소 (독특한 가치 제안)",
    "improvement_areas": "개선이 필요한 영역 (건설적 발전 방향)",
    "matching_score": 85,
    "analysis_summary": "지원자 분석 요약 (핵심 인사이트)"
}}
"""

        # 통합 벡터DB 컨텍스트를 활용한 프롬프트 강화
        enhanced_prompt = self.get_context_aware_prompt(state, base_prompt)

        messages = self._create_messages(enhanced_prompt)
        analysis_result = await self._call_llm(messages)
        
        # 분석 결과를 상태에 저장
        state.analysis_results["candidate_analysis"] = {
            "analyst": self.name,
            "result": analysis_result,
            "timestamp": "2024-01-15",
            "context_used": hasattr(state, 'agent_context') and state.agent_context is not None,
            "vectordb_enabled": hasattr(state, 'agent_context') and state.agent_context and state.agent_context.get('vectordb_enabled', False)
        }
        
        self.log("지원자 분석 완료 (컨텍스트 강화 분석)")
        return state 
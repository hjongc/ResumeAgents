"""
Quality Manager Agent for ResumeAgents.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class QualityManager(BaseAgent):
    """Agent responsible for quality control and final review."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Quality Manager",
            role="품질 관리자",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a quality control and strategic review expert specializing in comprehensive document evaluation.

Your primary responsibilities:
1. Evaluate document quality and effectiveness
2. Assess clarity, consistency, and impact
3. Evaluate alignment with company requirements
4. Provide improvement suggestions and optimization recommendations
5. Make final approval/rejection decisions

Key evaluation criteria:
- Content clarity and readability
- Alignment with company requirements
- Effective emphasis of candidate strengths
- Grammar and expression accuracy
- Structure and format appropriateness
- Clarity of differentiation factors
- Impact and persuasiveness

Please provide evaluation results in Korean language with structured JSON format. Focus on objective and constructive feedback."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("품질 관리 시작")
        
        if not state.final_document:
            self.log("검토할 서류가 없습니다.")
            return state
        
        # 모든 분석 결과를 종합
        analysis_summary = ""
        for key, value in state.analysis_results.items():
            analysis_summary += f"\n{key}: {value['result']}\n"
        
        prompt = f"""
Please evaluate the quality of the following document:

Company: {state.company_name}
Position: {state.job_title}

Analysis Results:
{analysis_summary}

Created Document:
{state.final_document}

Please evaluate the document based on the following criteria:
1. Content clarity and readability (0-100 points)
2. Alignment with company requirements (0-100 points)
3. Effective emphasis of candidate strengths (0-100 points)
4. Grammar and expression accuracy (0-100 points)
5. Structure and format appropriateness (0-100 points)
6. Clarity of differentiation factors (0-100 points)
7. Impact and persuasiveness (0-100 points)

Please provide your evaluation in Korean language with the following JSON structure:
{{
    "clarity_score": 85,
    "alignment_score": 90,
    "emphasis_score": 88,
    "grammar_score": 92,
    "structure_score": 87,
    "differentiation_score": 85,
    "impact_score": 89,
    "overall_quality_score": 88,
    "improvement_suggestions": "개선 제안사항",
    "approval_decision": "승인/거부 결정",
    "evaluation_summary": "품질 평가 요약"
}}
"""

        messages = self._create_messages(prompt)
        quality_result = await self._call_llm(messages)
        
        # 품질 평가 결과를 상태에 저장
        state.analysis_results["quality_assessment"] = {
            "analyst": self.name,
            "result": quality_result,
            "timestamp": "2024-01-15"
        }
        
        # 품질 점수 추출 (간단한 예시)
        try:
            # 실제로는 JSON 파싱을 통해 점수를 추출
            state.quality_score = 88.0  # 예시 점수
        except:
            state.quality_score = 85.0
        
        self.log("품질 관리 완료")
        return state 
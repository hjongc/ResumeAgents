"""
Resume Writer Agent for ResumeAgents.
Specialized in creating structured resume documents.
"""

import json
from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class ResumeWriter(BaseAgent):
    """Agent responsible for creating resume documents."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Resume Writer",
            role="이력서 작성가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a resume creation expert specializing in structured resume document optimization.

Your primary responsibilities:
1. Create professional resume documents based on analysis results
2. Organize candidate information in a clear, structured format
3. Highlight relevant experience and achievements
4. Use professional language and formatting
5. Focus on ATS-friendly structure

Key considerations:
- Standard resume format with clear sections
- Quantifiable achievements and results
- Professional terminology and expressions
- Logical information hierarchy
- Clean and readable structure

Please create resumes in Korean language with professional formatting."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("이력서 작성 시작")
        
        # 리비전 여부 확인
        is_revision = hasattr(state, 'is_revision') and state.is_revision
        revision_feedback = getattr(state, 'revision_feedback', []) if is_revision else []
        
        # 분석 결과 요약 (기본적인 분석 결과만 사용)
        analysis_summary = self._get_basic_analysis_summary(state)
        
        # 이력서 작성 프롬프트
        base_prompt = f"""
다음 분석 결과를 바탕으로 {state.company_name} {state.job_title} 지원을 위한 전문적인 이력서를 작성해주세요.

=== 회사 및 직무 정보 ===
회사: {state.company_name}
직무: {state.job_title}
직무 설명: {state.job_description[:500]}...

=== 지원자 정보 ===
{self._format_candidate_info_for_resume(state.candidate_info)}

=== 핵심 분석 결과 ===
{analysis_summary}

다음 형식으로 전문적인 이력서를 작성해주세요:

{self._get_resume_format_guide()}

각 섹션을 명확하게 구분하고, 지원자의 경험과 성과를 구체적인 수치와 함께 제시해주세요.
"""

        # 리비전인 경우 피드백 반영
        if is_revision and revision_feedback:
            revision_prompt = f"""
⚠️ 이전 이력서의 품질이 기준에 미달하여 수정이 필요합니다.

이전 이력서:
{state.final_document}

개선해야 할 사항들:
"""
            for i, feedback in enumerate(revision_feedback, 1):
                revision_prompt += f"{i}. {feedback}\n"

            revision_prompt += f"""
위 개선사항들을 반드시 반영하여 더 높은 품질의 이력서를 작성해주세요.

{base_prompt}
"""
            prompt = revision_prompt
        else:
            prompt = base_prompt + "\n한국어로 전문적인 이력서를 작성해주세요."

        messages = self._create_messages(prompt)
        resume_result = await self._call_llm(messages)
        
        # 작성된 이력서를 상태에 저장
        state.final_document = resume_result
        
        # 결과 저장
        state.analysis_results["resume_writing"] = {
            "analyst": self.name,
            "result": resume_result,
            "is_revision": is_revision,
            "revision_count": getattr(state, 'revision_count', 0),
            "improvements_applied": revision_feedback if is_revision else [],
            "timestamp": "2024-01-15"
        }
        
        if is_revision:
            self.log(f"🔄 이력서 리비전 작성 완료 (시도 {state.revision_count})")
        else:
            self.log("📝 이력서 작성 완료")
        
        return state
    
    def _get_basic_analysis_summary(self, state: AgentState) -> str:
        """Extract basic analysis results needed for resume creation."""
        summary = ""
        
        # 이력서에 필요한 기본 분석만 포함
        basic_keys = ["company_analysis", "jd_analysis", "candidate_analysis", "strength_research"]
        
        for key in basic_keys:
            if key in state.analysis_results:
                value = state.analysis_results[key]
                if isinstance(value, dict) and 'result' in value:
                    summary += f"\n{key}:\n{str(value['result'])[:200]}...\n"
        
        return summary

    def _format_candidate_info_for_resume(self, candidate_info: Dict[str, Any]) -> str:
        """Format candidate information specifically for resume creation."""
        formatted_info = []
        
        # 이력서에 필요한 정보만 포맷
        resume_keys = ["name", "education", "experience", "skills", "projects", "achievements"]
        
        for key in resume_keys:
            if key in candidate_info and candidate_info[key]:
                value = candidate_info[key]
                if isinstance(value, str):
                    formatted_info.append(f"{key}: {value}")
                elif isinstance(value, list):
                    if key == "achievements":
                        formatted_info.append(f"{key}:\n" + "\n".join([f"- {item}" for item in value]))
                    else:
                        formatted_info.append(f"{key}: {', '.join(str(item) for item in value)}")
        
        return "\n".join(formatted_info)

    def _get_resume_format_guide(self) -> str:
        """Return resume format guide."""
        return """
■ 개인 정보
- 이름, 연락처, 이메일

■ 자기소개 (2-3줄 요약)
- 핵심 역량과 경험을 간결하게 요약

■ 경력 사항
- 회사명 | 직책 | 재직기간
- 주요 업무 및 성과 (구체적 수치 포함)

■ 학력
- 학교명, 전공, 졸업년도

■ 보유 기술 및 자격
- 프로그래밍 언어, 프레임워크, 도구 등

■ 프로젝트 경험
- 프로젝트명, 기간, 주요 성과

■ 수상 및 활동
- 관련 수상 경력 및 활동 사항
"""


# 기존 클래스명 호환성을 위한 별칭
DocumentWriter = ResumeWriter 
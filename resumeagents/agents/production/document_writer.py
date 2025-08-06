"""
Document Writer Agent for ResumeAgents.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class DocumentWriter(BaseAgent):
    """Agent responsible for creating final documents."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Document Writer",
            role="서류 작성가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a strategic document creation expert specializing in comprehensive document optimization.

Your primary responsibilities:
1. Create optimal documents based on comprehensive analysis results
2. Maximize candidate strengths through strategic content organization
3. Create customized documents aligned with company requirements
4. Use clear and impactful expressions
5. Create structured and readable documents

Key considerations:
- Content aligned with company's core values and culture
- Specific experience and achievements related to target position
- Candidate's unique strengths and differentiation factors
- Clear and concise expressions
- Logical and structured content
- Impactful keywords and expressions

Please create documents in Korean language. Focus on maximizing candidate's competitive advantages."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("서류 작성 시작")
        
        # 리비전 여부 확인
        is_revision = hasattr(state, 'revision_count') and state.revision_count > 0
        revision_feedback = getattr(state, 'revision_feedback', [])
        
        if is_revision:
            self.log(f"🔄 리비전 작성 시작 (시도 {state.revision_count})")
            if revision_feedback:
                self.log(f"📝 개선 사항: {len(revision_feedback)}개")
        
        # 모든 분석 결과를 종합
        analysis_summary = ""
        for key, value in state.analysis_results.items():
            if isinstance(value, dict) and 'result' in value:
                analysis_summary += f"\n{key}: {str(value['result'])[:300]}...\n"
        
        document_type = self.config.get("document_type", "resume")
        
        # 기본 프롬프트 구성
        base_prompt = f"""
다음 종합 분석 결과를 바탕으로 최적화된 {document_type}을 작성해주세요:

회사: {state.company_name}
직무: {state.job_title}
지원자 정보: {state.candidate_info}

분석 결과:
{analysis_summary}

다음 요구사항을 따라 {document_type}을 작성해주세요:
1. 회사의 핵심 가치와 문화에 부합하는 내용
2. 목표 직무와 관련된 구체적인 경험과 성과
3. 지원자의 고유한 강점과 차별화 요소
4. 명확하고 임팩트 있는 표현
5. 구조적이고 가독성 높은 형식

{self._get_document_format_guide(document_type)}
"""

        # 리비전인 경우 피드백 반영
        if is_revision and revision_feedback:
            revision_prompt = f"""
⚠️ 이전 버전의 품질이 기준에 미달하여 수정이 필요합니다.

이전 문서:
{state.final_document}

개선해야 할 사항들:
"""
            for i, feedback in enumerate(revision_feedback, 1):
                revision_prompt += f"{i}. {feedback}\n"

            revision_prompt += f"""
위 개선사항들을 반드시 반영하여 더 높은 품질의 {document_type}을 작성해주세요.
특히 다음 사항들을 중점적으로 개선해주세요:
- 내용의 명확성과 구체성 향상
- 회사 요구사항과의 연관성 강화
- 지원자 강점의 더 효과적인 표현
- 문법과 표현의 정확성 개선
- 차별화 요소의 명확한 제시
- 전체적인 임팩트와 설득력 강화

{base_prompt}
"""
            prompt = revision_prompt
        else:
            prompt = base_prompt + "\n한국어로 작성해주세요."

        messages = self._create_messages(prompt)
        document_result = await self._call_llm(messages)
        
        # 작성된 서류를 상태에 저장
        state.final_document = document_result
        
        # 결과 저장
        state.analysis_results["document_writing"] = {
            "analyst": self.name,
            "result": document_result,
            "is_revision": is_revision,
            "revision_count": getattr(state, 'revision_count', 0),
            "improvements_applied": revision_feedback if is_revision else [],
            "timestamp": "2024-01-15"
        }
        
        if is_revision:
            self.log(f"🔄 리비전 작성 완료 (시도 {state.revision_count})")
        else:
            self.log("📝 초기 서류 작성 완료")
        
        return state
    
    def _get_document_format_guide(self, document_type: str) -> str:
        """Return document format guide based on document type."""
        if document_type == "resume":
            return """
Resume Format Guide:
- Personal Information (Name, Contact, Email)
- Self-Introduction (2-3 sentences)
- Work Experience (Company, Position, Period, Key Responsibilities)
- Education
- Skills and Certifications
- Project Experience (with specific achievements)
- Awards and Activities
"""
        elif document_type == "cover_letter":
            return """
Cover Letter Format Guide:
- Application Motivation (Understanding of company and position)
- Personal Experience and Competencies
- Contributions to the company
- Future aspirations after joining
- Thank you message
"""
        else:
            return "Please create in standard document format." 
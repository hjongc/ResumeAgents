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
        
        # 모든 분석 결과를 종합
        analysis_summary = ""
        for key, value in state.analysis_results.items():
            analysis_summary += f"\n{key}: {value['result']}\n"
        
        document_type = self.config.get("document_type", "resume")
        
        prompt = f"""
Please create an optimized {document_type} based on the following comprehensive analysis results:

Company: {state.company_name}
Position: {state.job_title}
Candidate Information: {state.candidate_info}

Analysis Results:
{analysis_summary}

Please create the {document_type} following these requirements:
1. Content aligned with company's core values and culture
2. Specific experience and achievements related to target position
3. Candidate's unique strengths and differentiation factors
4. Clear and impactful expressions
5. Structured and readable format

{self._get_document_format_guide(document_type)}

Please create the {document_type} in Korean language.
"""

        messages = self._create_messages(prompt)
        document_result = await self._call_llm(messages)
        
        # 작성된 서류를 상태에 저장
        state.final_document = document_result
        
        self.log("서류 작성 완료")
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
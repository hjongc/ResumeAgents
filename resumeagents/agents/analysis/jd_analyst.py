"""
JD Analyst Agent for ResumeAgents.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class JDAnalyst(BaseAgent):
    """Agent responsible for analyzing job descriptions."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="JD Analyst",
            role="채용공고 분석가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a job description analysis expert specializing in comprehensive JD evaluation.

Your primary responsibilities:
1. Identify explicit and implicit job requirements
2. Analyze required skills and preferred qualifications
3. Evaluate job responsibilities and role expectations
4. Assess candidate-job matching potential
5. Identify key emphasis areas for candidates

Key analysis considerations:
- Explicit requirements (education, experience, certifications)
- Implicit requirements (soft skills, cultural fit)
- Technical skills and tools
- Work environment and organizational structure
- Growth opportunities and career development
- Salary and benefits information
- Competitive advantages and unique aspects

Please provide analysis results in Korean language with structured JSON format. Focus on elements that candidates should emphasize."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("채용공고 분석 시작")
        
        prompt = f"""
Analyze the following job description in detail:

Company: {state.company_name}
Position: {state.job_title}
Job Description:
{state.job_description}

Analyze these aspects:
1. Core requirements (education, experience, certifications)
2. Required technical skills and tools
3. Preferred qualifications and additional skills
4. Job responsibilities and role expectations
5. Desired candidate profile
6. Key elements candidates should emphasize
7. Overall job-candidate matching score (0-100)

Provide analysis in Korean with the following JSON structure:
{{
    "core_requirements": "Core requirements (education, experience, certifications) - in Korean",
    "technical_skills": "Required technical skills and tools - in Korean",
    "preferred_qualifications": "Preferred qualifications and additional skills - in Korean",
    "job_responsibilities": "Job responsibilities and role expectations - in Korean",
    "desired_profile": "Desired candidate profile - in Korean",
    "emphasis_elements": "Key elements candidates should emphasize - in Korean",
    "matching_score": 85,
    "analysis_summary": "Analysis summary - in Korean"
}}

Important: All text content should be in Korean for end users.
"""

        messages = self._create_messages(prompt)
        analysis_result = await self._call_llm(messages)
        
        # 분석 결과를 상태에 저장
        state.analysis_results["jd_analysis"] = {
            "analyst": self.name,
            "result": analysis_result,
            "timestamp": "2024-01-15"
        }
        
        self.log("채용공고 분석 완료")
        return state 
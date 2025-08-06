"""
Guide Stage Evaluator for ResumeAgents.
"""

from typing import Dict, Any
from .stage_evaluator import StageEvaluator


class GuideEvaluator(StageEvaluator):
    """Guide stage evaluator for Question, Experience, and Writing guide collective output."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            stage_name="Guide",
            llm=llm,
            config=config
        )
    
    def get_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Define Guide category evaluation criteria based on strategy document."""
        return {
            "guidance_specificity": {
                "description": "Guidance Specificity - Concrete and actionable guidance quality",
                "weight": 0.3,
                "details": [
                    "Specific writing strategies and techniques",
                    "Clear step-by-step guidance and instructions",
                    "Actionable recommendations with implementation details",
                    "Concrete examples and templates provided"
                ]
            },
            "experience_relevance": {
                "description": "Experience Relevance - Alignment with candidate profile and job requirements",
                "weight": 0.25,
                "details": [
                    "Experience selection accuracy and relevance",
                    "STAR method application effectiveness",
                    "Story arc development and narrative flow",
                    "Experience-job requirement mapping precision"
                ]
            },
            "strategic_coherence": {
                "description": "Strategic Coherence - Consistency with overall application strategy",
                "weight": 0.25,
                "details": [
                    "Alignment with strategic positioning from previous phases",
                    "Consistent messaging across all guidance elements",
                    "Integration of company culture and values",
                    "Coherent personal brand development"
                ]
            },
            "practical_usability": {
                "description": "Practical Usability - Ease of implementation and user-friendliness",
                "weight": 0.2,
                "details": [
                    "Clear structure and organization",
                    "Character limit optimization strategies",
                    "Practical writing tips and techniques",
                    "User-friendly format and presentation"
                ]
            }
        }
    
    def _create_evaluation_prompt(self, state, stage_result: Any, agent_name: str) -> str:
        """Create evaluation prompt for Guide category."""
        
        criteria = self.get_evaluation_criteria()
        criteria_text = "\n=== EVALUATION CRITERIA ===\n"
        for key, criterion in criteria.items():
            criteria_text += f"\n**{criterion['description']}** (Weight: {criterion['weight']*100}%)\n"
            for detail in criterion['details']:
                criteria_text += f"  • {detail}\n"
        
        # Collect all guide results for collective evaluation
        guide_results = ""
        guide_keys = ["question_guide", "experience_guide", "writing_guide"]
        for key in guide_keys:
            if hasattr(state, 'analysis_results') and key in state.analysis_results:
                result = state.analysis_results[key]
                if isinstance(result, dict) and 'result' in result:
                    guide_results += f"\n--- {key.upper().replace('_', ' ')} ---\n{str(result['result'])[:800]}...\n"
        
        # Strategic context from previous phases
        strategic_context = ""
        context_keys = ["company_analysis", "jd_analysis", "candidate_analysis", "strength_research"]
        for key in context_keys:
            if hasattr(state, 'analysis_results') and key in state.analysis_results:
                result = state.analysis_results[key]
                if isinstance(result, dict) and 'result' in result:
                    strategic_context += f"{key}: {str(result['result'])[:120]}...\n"
        
        return f"""
Evaluate the collective output of the Guide Team (Question + Experience + Writing guidance):

=== EVALUATION TARGET ===
Team: Guide Team
Company: {getattr(state, 'company_name', 'N/A')}
Position: {getattr(state, 'job_title', 'N/A')}
Quality Threshold: {self.quality_threshold*100:.0f}%

=== STRATEGIC CONTEXT (for reference) ===
{strategic_context}

=== GUIDE TEAM OUTPUT ===
{guide_results}

{criteria_text}

=== EVALUATION INSTRUCTIONS ===
1. Evaluate the COLLECTIVE performance of all three guide agents
2. Score each criterion from 0-100 points
3. Focus on actionable guidance quality and strategic coherence
4. If overall score < {self.quality_threshold*100:.0f}%, provide specific improvement suggestions
5. Consider how well this guidance supports the final document creation phase

{self._get_json_format()}

**Note**: Evaluate the team's ability to provide comprehensive, actionable, and strategically coherent writing guidance.
""" 
"""
Matching Stage Evaluator for ResumeAgents.
"""

from typing import Dict, Any
from .stage_evaluator import StageEvaluator


class MatchingEvaluator(StageEvaluator):
    """Matching stage evaluator for Candidate, Culture, and Trend analysis collective output."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            stage_name="Matching",
            llm=llm,
            config=config
        )
    
    def get_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Define Matching category evaluation criteria based on strategy document."""
        return {
            "candidate_company_fit": {
                "description": "Candidate-Company Fit - Accuracy of alignment assessment",
                "weight": 0.3,
                "details": [
                    "Skills matching precision and relevance",
                    "Experience level evaluation appropriateness",
                    "Growth potential analysis validity",
                    "Role-specific competency alignment"
                ]
            },
            "market_positioning": {
                "description": "Market Positioning - Strategic positioning within industry context",
                "weight": 0.25,
                "details": [
                    "Industry trend reflection and awareness",
                    "Technology trend understanding and application",
                    "Competitive landscape positioning accuracy",
                    "Market opportunity identification"
                ]
            },
            "competitive_analysis": {
                "description": "Competitive Analysis - Differentiation and advantage identification",
                "weight": 0.25,
                "details": [
                    "Unique strengths identification clarity",
                    "Competitive advantage analysis depth",
                    "Differentiation factor articulation",
                    "Value proposition development"
                ]
            },
            "cultural_integration": {
                "description": "Cultural Integration - Cultural fit and alignment assessment",
                "weight": 0.2,
                "details": [
                    "Company culture understanding depth",
                    "Values alignment analysis accuracy",
                    "Team dynamics compatibility assessment",
                    "Cultural adaptation potential evaluation"
                ]
            }
        }
    
    def _create_evaluation_prompt(self, state, stage_result: Any, agent_name: str) -> str:
        """Create evaluation prompt for Matching category."""
        
        criteria = self.get_evaluation_criteria()
        criteria_text = "\n=== EVALUATION CRITERIA ===\n"
        for key, criterion in criteria.items():
            criteria_text += f"\n**{criterion['description']}** (Weight: {criterion['weight']*100}%)\n"
            for detail in criterion['details']:
                criteria_text += f"  • {detail}\n"
        
        # Collect all matching results for collective evaluation
        matching_results = ""
        matching_keys = ["candidate_analysis", "culture_analysis", "trend_analysis"]
        for key in matching_keys:
            if hasattr(state, 'analysis_results') and key in state.analysis_results:
                result = state.analysis_results[key]
                if isinstance(result, dict) and 'result' in result:
                    matching_results += f"\n--- {key.upper().replace('_', ' ')} ---\n{str(result['result'])[:800]}...\n"
        
        # Analysis context for reference
        analysis_context = ""
        analysis_keys = ["company_analysis", "market_analysis", "jd_analysis"]
        for key in analysis_keys:
            if hasattr(state, 'analysis_results') and key in state.analysis_results:
                result = state.analysis_results[key]
                if isinstance(result, dict) and 'result' in result:
                    analysis_context += f"{key}: {str(result['result'])[:150]}...\n"
        
        return f"""
Evaluate the collective output of the Matching Team (Candidate + Culture + Trend analysis):

=== EVALUATION TARGET ===
Team: Matching Team  
Company: {getattr(state, 'company_name', 'N/A')}
Position: {getattr(state, 'job_title', 'N/A')}
Quality Threshold: {self.quality_threshold*100:.0f}%

=== ANALYSIS CONTEXT (for reference) ===
{analysis_context}

=== MATCHING TEAM OUTPUT ===
{matching_results}

{criteria_text}

=== EVALUATION INSTRUCTIONS ===
1. Evaluate the COLLECTIVE performance of all three matching agents
2. Score each criterion from 0-100 points  
3. Focus on alignment assessment and positioning strategy
4. If overall score < {self.quality_threshold*100:.0f}%, provide specific improvement suggestions
5. Consider how well this matching analysis supports strategic positioning

{self._get_json_format()}

**Note**: Evaluate the team's ability to assess candidate-company alignment and strategic market positioning.
""" 
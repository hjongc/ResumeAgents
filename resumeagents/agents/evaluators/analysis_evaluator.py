"""
Analysis Stage Evaluator for ResumeAgents.
"""

from typing import Dict, Any
from .stage_evaluator import StageEvaluator


class AnalysisEvaluator(StageEvaluator):
    """Analysis stage evaluator for Company, Market, and JD analysis collective output."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            stage_name="Analysis",
            llm=llm,
            config=config
        )
    
    def get_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Define Analysis category evaluation criteria based on strategy document."""
        return {
            "information_accuracy": {
                "description": "Information Accuracy - Reliability and correctness of gathered data",
                "weight": 0.25,
                "details": [
                    "Company information accuracy and currency",
                    "Market data reliability and source credibility", 
                    "Job requirements precision and completeness",
                    "Factual consistency across all analysis"
                ]
            },
            "coverage_completeness": {
                "description": "Coverage Completeness - Thoroughness of analysis scope",
                "weight": 0.25,
                "details": [
                    "Comprehensive company culture and values analysis",
                    "Complete market landscape and competitive positioning",
                    "Thorough job requirements and skill mapping",
                    "No critical information gaps"
                ]
            },
            "strategic_relevance": {
                "description": "Strategic Relevance - Alignment with application strategy",
                "weight": 0.25,
                "details": [
                    "Information directly applicable to application strategy",
                    "Context building for subsequent phases",
                    "Relevance to candidate positioning",
                    "Strategic insight generation potential"
                ]
            },
            "insight_depth": {
                "description": "Insight Depth - Quality of analytical insights",
                "weight": 0.25,
                "details": [
                    "Deep understanding beyond surface information",
                    "Pattern recognition and trend identification",
                    "Implications and strategic opportunities",
                    "Actionable intelligence for next phases"
                ]
            }
        }
    
    def get_quality_threshold(self) -> float:
        """Analysis category uses 72% threshold (more lenient for foundational analysis)."""
        base_threshold = self.config.get("quality_threshold", 0.8)
        return base_threshold * 0.9  # 72% for analysis phase
    
    def _create_evaluation_prompt(self, state, stage_result: Any, agent_name: str) -> str:
        """Create evaluation prompt for Analysis category."""
        
        criteria = self.get_evaluation_criteria()
        criteria_text = "\n=== EVALUATION CRITERIA ===\n"
        for key, criterion in criteria.items():
            criteria_text += f"\n**{criterion['description']}** (Weight: {criterion['weight']*100}%)\n"
            for detail in criterion['details']:
                criteria_text += f"  • {detail}\n"
        
        # Collect all analysis results for collective evaluation
        analysis_results = ""
        analysis_keys = ["company_analysis", "market_analysis", "jd_analysis"]
        for key in analysis_keys:
            if hasattr(state, 'analysis_results') and key in state.analysis_results:
                result = state.analysis_results[key]
                if isinstance(result, dict) and 'result' in result:
                    analysis_results += f"\n--- {key.upper().replace('_', ' ')} ---\n{str(result['result'])[:800]}...\n"
        
        return f"""
Evaluate the collective output of the Analysis Team (Company + Market + JD analysis):

=== EVALUATION TARGET ===
Team: Analysis Team
Company: {getattr(state, 'company_name', 'N/A')}
Position: {getattr(state, 'job_title', 'N/A')}
Quality Threshold: {self.quality_threshold*100:.0f}%

=== ANALYSIS TEAM OUTPUT ===
{analysis_results}

{criteria_text}

=== EVALUATION INSTRUCTIONS ===
1. Evaluate the COLLECTIVE performance of all three analysis agents
2. Score each criterion from 0-100 points
3. Focus on data quality and strategic context building
4. If overall score < {self.quality_threshold*100:.0f}%, provide specific improvement suggestions
5. Consider how well this analysis sets up subsequent matching and strategy phases

{self._get_json_format()}

**Note**: This is foundational analysis - focus on information quality and strategic context building rather than perfect execution.
""" 
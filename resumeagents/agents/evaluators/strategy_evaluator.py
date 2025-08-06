"""
Strategy Stage Evaluator for ResumeAgents.
"""

from typing import Dict, Any
from .stage_evaluator import StageEvaluator


class StrategyEvaluator(StageEvaluator):
    """Strategy stage evaluator for Strength and Weakness research collective output."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            stage_name="Strategy",
            llm=llm,
            config=config
        )
    
    def get_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Define Strategy category evaluation criteria based on strategy document."""
        return {
            "evidence_quality": {
                "description": "Evidence Quality - Strength and credibility of supporting evidence",
                "weight": 0.3,
                "details": [
                    "Concrete examples and quantifiable achievements",
                    "Relevant experience validation and verification",
                    "Credible skill demonstration and proof points",
                    "Consistent evidence across strength/weakness analysis"
                ]
            },
            "strategic_positioning": {
                "description": "Strategic Positioning - Effectiveness of competitive positioning",
                "weight": 0.25,
                "details": [
                    "Clear value proposition development",
                    "Competitive advantage articulation",
                    "Market differentiation strategy clarity",
                    "Positioning alignment with company needs"
                ]
            },
            "balanced_assessment": {
                "description": "Balanced Assessment - Comprehensive and realistic evaluation",
                "weight": 0.25,
                "details": [
                    "Honest weakness identification and mitigation",
                    "Strength-weakness balance and integration",
                    "Risk assessment accuracy and completeness",
                    "Improvement strategy feasibility"
                ]
            },
            "differentiation_factor": {
                "description": "Differentiation Factor - Unique value and competitive edge clarity",
                "weight": 0.2,
                "details": [
                    "Unique selling proposition identification",
                    "Distinctive competencies highlighting",
                    "Personal brand differentiation",
                    "Memorable positioning elements"
                ]
            }
        }
    
    def _create_evaluation_prompt(self, state, stage_result: Any, agent_name: str) -> str:
        """Create evaluation prompt for Strategy category."""
        
        criteria = self.get_evaluation_criteria()
        criteria_text = "\n=== EVALUATION CRITERIA ===\n"
        for key, criterion in criteria.items():
            criteria_text += f"\n**{criterion['description']}** (Weight: {criterion['weight']*100}%)\n"
            for detail in criterion['details']:
                criteria_text += f"  • {detail}\n"
        
        # Collect all strategy results for collective evaluation
        strategy_results = ""
        strategy_keys = ["strength_research", "weakness_research"]
        for key in strategy_keys:
            if hasattr(state, 'analysis_results') and key in state.analysis_results:
                result = state.analysis_results[key]
                if isinstance(result, dict) and 'result' in result:
                    strategy_results += f"\n--- {key.upper().replace('_', ' ')} ---\n{str(result['result'])[:800]}...\n"
        
        # Previous phases context for reference
        context_summary = ""
        context_keys = ["company_analysis", "jd_analysis", "candidate_analysis", "culture_analysis"]
        for key in context_keys:
            if hasattr(state, 'analysis_results') and key in state.analysis_results:
                result = state.analysis_results[key]
                if isinstance(result, dict) and 'result' in result:
                    context_summary += f"{key}: {str(result['result'])[:120]}...\n"
        
        return f"""
Evaluate the collective output of the Strategy Team (Strength + Weakness research):

=== EVALUATION TARGET ===
Team: Strategy Team
Company: {getattr(state, 'company_name', 'N/A')}
Position: {getattr(state, 'job_title', 'N/A')}
Quality Threshold: {self.quality_threshold*100:.0f}%

=== PREVIOUS ANALYSIS CONTEXT (for reference) ===
{context_summary}

=== STRATEGY TEAM OUTPUT ===
{strategy_results}

{criteria_text}

=== EVALUATION INSTRUCTIONS ===
1. Evaluate the COLLECTIVE performance of both strategy research agents
2. Score each criterion from 0-100 points
3. Focus on strategic advantage development and competitive positioning
4. If overall score < {self.quality_threshold*100:.0f}%, provide specific improvement suggestions
5. Consider how well this strategic analysis supports writing guidance phase

{self._get_json_format()}

**Note**: Evaluate the team's ability to develop compelling strategic positioning and competitive advantages.
""" 
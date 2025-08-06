"""
Production Stage Evaluator for ResumeAgents.
"""

from typing import Dict, Any
from .stage_evaluator import StageEvaluator


class ProductionEvaluator(StageEvaluator):
    """Production stage evaluator for Document Writer and Quality Manager collective output."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            stage_name="Production",
            llm=llm,
            config=config
        )
    
    def get_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Define Production category evaluation criteria based on strategy document."""
        return {
            "content_integration": {
                "description": "Content Integration - Effective synthesis of all analysis phases",
                "weight": 0.25,
                "details": [
                    "Comprehensive integration of analysis insights",
                    "Strategic positioning implementation accuracy",
                    "Guidance recommendations incorporation",
                    "Cohesive narrative development"
                ]
            },
            "persuasive_impact": {
                "description": "Persuasive Impact - Compelling and convincing presentation",
                "weight": 0.25,
                "details": [
                    "Strong opening and compelling hook",
                    "Persuasive argumentation and evidence",
                    "Emotional appeal and connection",
                    "Memorable closing and call to action"
                ]
            },
            "professional_quality": {
                "description": "Professional Quality - Writing excellence and presentation standards",
                "weight": 0.2,
                "details": [
                    "Grammar, syntax, and language precision",
                    "Professional tone and style consistency",
                    "Clear structure and logical flow",
                    "Appropriate formatting and presentation"
                ]
            },
            "requirements_compliance": {
                "description": "Requirements Compliance - Adherence to specifications and constraints",
                "weight": 0.15,
                "details": [
                    "Character/word limit compliance",
                    "Question requirements fulfillment",
                    "Format and structure specifications",
                    "Company-specific requirements addressing"
                ]
            },
            "differentiation_clarity": {
                "description": "Differentiation Clarity - Unique value proposition articulation",
                "weight": 0.15,
                "details": [
                    "Clear unique selling proposition",
                    "Competitive advantage highlighting",
                    "Personal brand differentiation",
                    "Memorable positioning elements"
                ]
            }
        }
    
    def get_quality_threshold(self) -> float:
        """Production category uses 84% threshold (more stringent for final output)."""
        base_threshold = self.config.get("quality_threshold", 0.8)
        return base_threshold * 1.05  # 84% for production phase
    
    def _create_evaluation_prompt(self, state, stage_result: Any, agent_name: str) -> str:
        """Create evaluation prompt for Production category."""
        
        criteria = self.get_evaluation_criteria()
        criteria_text = "\n=== EVALUATION CRITERIA ===\n"
        for key, criterion in criteria.items():
            criteria_text += f"\n**{criterion['description']}** (Weight: {criterion['weight']*100}%)\n"
            for detail in criterion['details']:
                criteria_text += f"  • {detail}\n"
        
        # Get final document and quality assessment
        final_document = getattr(state, 'final_document', 'No document available')
        quality_assessment = ""
        
        if hasattr(state, 'analysis_results') and 'quality_assessment' in state.analysis_results:
            quality_result = state.analysis_results['quality_assessment']
            if isinstance(quality_result, dict) and 'result' in quality_result:
                quality_assessment = f"\n--- QUALITY ASSESSMENT ---\n{str(quality_result['result'])[:600]}...\n"
        
        # Comprehensive workflow summary
        workflow_summary = ""
        workflow_keys = ["company_analysis", "candidate_analysis", "strength_research", "question_guide", "document_writing"]
        for key in workflow_keys:
            if hasattr(state, 'analysis_results') and key in state.analysis_results:
                result = state.analysis_results[key]
                if isinstance(result, dict) and 'result' in result:
                    workflow_summary += f"{key}: {str(result['result'])[:100]}...\n"
        
        return f"""
Evaluate the collective output of the Production Team (Document Writer + Quality Manager):

=== EVALUATION TARGET ===
Team: Production Team
Company: {getattr(state, 'company_name', 'N/A')}
Position: {getattr(state, 'job_title', 'N/A')}
Quality Threshold: {self.quality_threshold*100:.0f}% (Higher standard for final output)

=== WORKFLOW SUMMARY (for context) ===
{workflow_summary}

=== FINAL DOCUMENT ===
{final_document}

=== QUALITY MANAGEMENT OUTPUT ===
{quality_assessment}

{criteria_text}

=== EVALUATION INSTRUCTIONS ===
1. Evaluate the COLLECTIVE performance of document creation and quality management
2. Score each criterion from 0-100 points
3. Focus on final document excellence and quality assurance
4. If overall score < {self.quality_threshold*100:.0f}%, provide specific improvement suggestions
5. This is the final output - apply highest standards for evaluation

{self._get_json_format()}

**Note**: This is the final deliverable - evaluate with the highest standards for document quality and professional presentation.
""" 
"""
Base Stage Evaluator for ResumeAgents.
"""

import json
import re
from typing import Dict, Any, List, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from ..base_agent import AgentState


class StageEvaluator:
    """Base class for stage-specific evaluation agents."""
    
    def __init__(self, stage_name: str, llm=None, config=None):
        self.name = f"{stage_name} Evaluator"
        self.role = f"{stage_name} stage evaluator"
        self.stage_name = stage_name
        self.llm = llm
        self.config = config or {}
        self.evaluation_criteria = self.get_evaluation_criteria()
        self.quality_threshold = self.get_quality_threshold()
    
    def get_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Define evaluation criteria for this stage. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must define evaluation criteria.")
    
    def get_quality_threshold(self) -> float:
        """Get quality threshold for this stage."""
        base_threshold = self.config.get('quality_threshold', 0.8)
        return base_threshold
    
    def get_system_prompt(self) -> str:
        """Get system prompt for this evaluator."""
        return f"""You are an expert evaluator specializing in {self.stage_name} stage assessment for job application documents.

Your primary responsibilities:
1. Evaluate team performance using specific criteria
2. Provide objective scores and constructive feedback
3. Determine if revision is needed based on quality thresholds
4. Generate actionable improvement suggestions

Evaluation Approach:
- Focus on collective team output rather than individual agents
- Apply consistent scoring standards (0-100 points)
- Provide specific, actionable feedback for improvements
- Consider strategic context from previous workflow phases

Response Format:
- Always respond in valid JSON format
- Include numerical scores for each criterion
- Provide specific improvement suggestions when needed
- Make clear revision recommendations"""

    async def evaluate_stage(self, state: AgentState, stage_result: Any, team_name: str) -> Tuple[bool, List[str], Dict[str, float]]:
        """Evaluate a stage and return revision decision, feedback, and scores."""
        
        # Create evaluation prompt
        prompt = self._create_evaluation_prompt(state, stage_result, team_name)
        
        # Call LLM for evaluation
        messages = self._create_messages(prompt)
        evaluation_result = await self._call_llm(messages)
        
        # Extract scores and feedback
        scores = self._extract_evaluation_scores(evaluation_result)
        feedback = self._extract_feedback(evaluation_result)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(scores)
        
        # Determine if revision is needed
        needs_revision = overall_score < self.quality_threshold
        
        self.log(f"📊 {self.stage_name} Evaluation: {overall_score:.2f} (Threshold: {self.quality_threshold:.2f})")
        
        return needs_revision, feedback, scores
    
    def _create_evaluation_prompt(self, state: AgentState, stage_result: Any, team_name: str) -> str:
        """Create evaluation prompt. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement _create_evaluation_prompt")
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        if not scores:
            return 0.0
        
        criteria = self.get_evaluation_criteria()
        total_score = 0.0
        total_weight = 0.0
        
        for criterion_key, score in scores.items():
            if criterion_key in criteria:
                weight = criteria[criterion_key].get('weight', 1.0)
                total_score += score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _extract_evaluation_scores(self, evaluation_result: str) -> Dict[str, float]:
        """Extract scores from evaluation result."""
        scores = {}
        
        try:
            # Try to parse as JSON
            if '{' in evaluation_result and '}' in evaluation_result:
                json_match = re.search(r'\{.*\}', evaluation_result, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    evaluation_data = json.loads(json_str)
                    
                    # Extract scores for each criterion
                    for criterion_name in self.evaluation_criteria.keys():
                        score_key = f"{criterion_name}_score"
                        if score_key in evaluation_data:
                            scores[criterion_name] = float(evaluation_data[score_key]) / 100.0
                    
                    # Extract overall score if available
                    if 'overall_score' in evaluation_data:
                        scores['overall'] = float(evaluation_data['overall_score']) / 100.0
            
            # Use default values if no scores found
            if not scores:
                for criterion_name in self.evaluation_criteria.keys():
                    scores[criterion_name] = 0.75  # Default 75%
                scores['overall'] = 0.75
                
        except Exception as e:
            self.log(f"Score extraction failed: {e}")
            # Set default values
            for criterion_name in self.evaluation_criteria.keys():
                scores[criterion_name] = 0.75
            scores['overall'] = 0.75
        
        return scores
    
    def _extract_feedback(self, evaluation_result: str) -> List[str]:
        """Extract feedback from evaluation result."""
        feedback = []
        
        try:
            if '{' in evaluation_result and '}' in evaluation_result:
                json_match = re.search(r'\{.*\}', evaluation_result, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    evaluation_data = json.loads(json_str)
                    
                    # Extract improvement suggestions
                    if 'improvement_suggestions' in evaluation_data:
                        suggestions = evaluation_data['improvement_suggestions']
                        if isinstance(suggestions, list):
                            feedback = suggestions
                        elif isinstance(suggestions, str):
                            feedback = [suggestions]
                    
                    # Extract specific feedback if available
                    if 'specific_feedback' in evaluation_data:
                        specific = evaluation_data['specific_feedback']
                        if isinstance(specific, list):
                            feedback.extend(specific)
                        elif isinstance(specific, str):
                            feedback.append(specific)
        
        except Exception as e:
            self.log(f"Feedback extraction failed: {e}")
        
        # Provide default feedback if none found
        if not feedback:
            feedback = [f"Overall quality improvement needed for {self.stage_name} stage."]
        
        return feedback
    
    def _create_messages(self, user_prompt: str) -> List:
        """Create messages for LLM call."""
        return [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=user_prompt)
        ]
    
    async def _call_llm(self, messages: List, **kwargs) -> str:
        """Call the LLM with given messages."""
        response = await self.llm.ainvoke(messages, **kwargs)
        return response.content
    
    def _get_json_format(self) -> str:
        """Get JSON response format example."""
        criteria_scores = {}
        for criterion_name in self.evaluation_criteria.keys():
            criteria_scores[f"{criterion_name}_score"] = 85
        
        example_json = {
            **criteria_scores,
            "overall_score": 87,
            "improvement_suggestions": ["Specific improvement suggestions"],
            "specific_feedback": ["Detailed step-by-step feedback"],
            "revision_needed": "yes" if True else "no",
            "evaluation_summary": "Evaluation summary"
        }
        
        return f"""Please provide evaluation results in the following JSON format:
{json.dumps(example_json, ensure_ascii=False, indent=2)}"""
    
    def log(self, message: str):
        """Log a message if debug is enabled."""
        if self.config.get("debug", False):
            print(f"[{self.name}] {message}") 
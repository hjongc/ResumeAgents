"""
Writing Guide Agent for providing comprehensive writing strategy and structure guidance.
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent, AgentState


class WritingGuide(BaseAgent):
    """Agent responsible for providing comprehensive writing strategy and structure guidance."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Writing Guide",
            role="작성 가이드 전문가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a writing guidance expert specializing in creating comprehensive writing strategies for self-introduction questions.

Your primary responsibilities:
1. Create detailed writing plans for each question
2. Develop structured content outlines and frameworks
3. Plan narrative flow and storytelling approach
4. Design strategic content organization
5. Provide practical writing guidance and tips

Key guidance considerations:
- Content structure and logical flow
- Storytelling approach and narrative arc
- Key message positioning and emphasis
- Content length and word count distribution
- Hook and conclusion strategies
- Emotional engagement and impact maximization

Please provide comprehensive writing guidance in Korean language with structured format. Focus on creating practical and effective writing strategies."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("작성 가이드 분석 시작")
        
        # 문항 정보와 이전 가이드 결과들 추출
        questions = state.candidate_info.get("custom_questions", [])
        question_guides = state.analysis_results.get("question_guides", {}).get("guides", [])
        experience_guides = state.analysis_results.get("experience_guides", {}).get("guides", [])
        
        if not questions:
            self.log("가이드할 문항이 없습니다.")
            return state
        
        guides = []
        
        for i, question in enumerate(questions):
            self.log(f"문항 {i+1} 작성 가이드 생성 중: {question['question'][:50]}...")
            
            # 해당 문항의 이전 가이드 결과들 찾기
            question_guide = ""
            experience_guide = ""
            
            if i < len(question_guides):
                question_guide = question_guides[i].get("guide", "")
            if i < len(experience_guides):
                experience_guide = experience_guides[i].get("guide", "")
            
            prompt = f"""
Please provide comprehensive writing guidance for the following question:

Company: {state.company_name}
Position: {state.job_title}
Question: {question['question']}
Question Type: {question.get('type', 'general')}

Previous Analysis:
Question Guide: {question_guide if question_guide else "분석 정보 없음"}
Experience Guide: {experience_guide if experience_guide else "분석 정보 없음"}

Candidate Information:
- Experience: {state.candidate_info.get('experience', '')}
- Skills: {state.candidate_info.get('skills', '')}
- Projects: {state.candidate_info.get('projects', '')}
- Education: {state.candidate_info.get('education', '')}

Please provide comprehensive writing guidance in Korean language with the following structure:
{{
    "question": "원본 문항",
    "writing_strategy": {{
        "overall_approach": "전체 접근 방법",
        "narrative_strategy": "내러티브 전략",
        "emotional_strategy": "감정적 전략",
        "impact_strategy": "임팩트 전략"
    }},
    "content_structure": {{
        "introduction": {{
            "purpose": "도입부 목적",
            "key_elements": ["핵심 요소 1", "핵심 요소 2"],
            "writing_tips": ["작성 팁 1", "작성 팁 2"],
            "estimated_length": "예상 글자 수"
        }},
        "main_body": {{
            "purpose": "본론 목적",
            "sections": [
                {{
                    "section": "섹션 1",
                    "purpose": "목적",
                    "key_points": ["핵심 포인트 1", "핵심 포인트 2"],
                    "writing_tips": ["작성 팁 1", "작성 팁 2"],
                    "estimated_length": "예상 글자 수"
                }},
                {{
                    "section": "섹션 2",
                    "purpose": "목적",
                    "key_points": ["핵심 포인트 1", "핵심 포인트 2"],
                    "writing_tips": ["작성 팁 1", "작성 팁 2"],
                    "estimated_length": "예상 글자 수"
                }}
            ]
        }},
        "conclusion": {{
            "purpose": "결론 목적",
            "key_elements": ["핵심 요소 1", "핵심 요소 2"],
            "writing_tips": ["작성 팁 1", "작성 팁 2"],
            "estimated_length": "예상 글자 수"
        }}
    }},
    "narrative_flow": [
        "스토리텔링 단계 1",
        "스토리텔링 단계 2",
        "스토리텔링 단계 3"
    ],
    "key_messages": [
        "핵심 메시지 1",
        "핵심 메시지 2",
        "핵심 메시지 3"
    ],
    "writing_techniques": {{
        "hook_techniques": ["훅 기법 1", "훅 기법 2"],
        "transition_techniques": ["전환 기법 1", "전환 기법 2"],
        "emphasis_techniques": ["강조 기법 1", "강조 기법 2"],
        "conclusion_techniques": ["결론 기법 1", "결론 기법 2"]
    }},
    "style_guidance": {{
        "tone_recommendation": "어조 제안",
        "language_style": "언어 스타일",
        "formality_level": "격식 수준",
        "personal_touch": "개인적 터치 방법"
    }},
    "common_mistakes": [
        "피해야 할 실수 1",
        "피해야 할 실수 2",
        "피해야 할 실수 3"
    ],
    "quality_checklist": [
        "품질 체크 항목 1",
        "품질 체크 항목 2",
        "품질 체크 항목 3"
    ],
    "writing_timeline": {{
        "planning_phase": "계획 단계",
        "drafting_phase": "초안 작성 단계",
        "revision_phase": "수정 단계",
        "finalization_phase": "완성 단계"
    }},
    "guidance_summary": "작성 가이드 요약"
}}

Focus on:
1. Creating compelling and structured writing plans
2. Maximizing emotional impact and engagement
3. Ensuring logical flow and coherence
4. Providing practical writing techniques
5. Planning for maximum effectiveness and memorability
"""

            messages = self._create_messages(prompt)
            guide_result = await self._call_llm(messages)
            
            guides.append({
                "question": question,
                "guide": guide_result,
                "analyst": self.name,
                "timestamp": "2025-08-05"
            })
        
        # 가이드 결과를 상태에 저장
        state.analysis_results["writing_guides"] = {
            "analyst": self.name,
            "guides": guides,
            "total_questions": len(questions),
            "timestamp": "2025-08-05"
        }
        
        self.log("작성 가이드 분석 완료")
        return state 
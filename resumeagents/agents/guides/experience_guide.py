"""
Experience Guide Agent for matching experiences to questions and providing storytelling guidance.
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent, AgentState


class ExperienceGuide(BaseAgent):
    """Agent responsible for matching candidate experiences to questions and providing storytelling guidance."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Experience Guide",
            role="경험 가이드 전문가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are an experience guidance expert specializing in helping candidates identify and utilize their experiences effectively for self-introduction questions.

Your primary responsibilities:
1. Analyze candidate experiences and achievements
2. Match experiences with question requirements
3. Provide strategic experience selection guidance
4. Suggest specific examples and achievements
5. Create comprehensive experience utilization plans

Key guidance considerations:
- Experience relevance to question intent
- Achievement impact and quantifiable results
- Experience recency and current relevance
- Skill demonstration alignment
- Storytelling potential and narrative strength
- Uniqueness and differentiation value

Please provide comprehensive guidance in Korean language with structured format. Focus on helping candidates maximize their experience impact."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("경험 가이드 분석 시작")
        
        # 문항 정보와 문항 가이드 결과 추출
        questions = state.candidate_info.get("custom_questions", [])
        question_guides = state.analysis_results.get("question_guides", {}).get("guides", [])
        
        if not questions:
            self.log("가이드할 문항이 없습니다.")
            return state
        
        guides = []
        
        for i, question in enumerate(questions):
            self.log(f"문항 {i+1} 경험 가이드 생성 중: {question['question'][:50]}...")
            
            # 해당 문항의 가이드 결과 찾기
            question_guide = ""
            if i < len(question_guides):
                question_guide = question_guides[i].get("guide", "")
            
            prompt = f"""
Please provide comprehensive experience guidance for the following question:

Company: {state.company_name}
Position: {state.job_title}
Question: {question['question']}
Question Type: {question.get('type', 'general')}

Question Analysis:
{question_guide if question_guide else "분석 정보 없음"}

Candidate Information:
- Experience: {state.candidate_info.get('experience', '')}
- Skills: {state.candidate_info.get('skills', '')}
- Projects: {state.candidate_info.get('projects', '')}
- Education: {state.candidate_info.get('education', '')}

Please provide comprehensive experience guidance in Korean language with the following structure:
{{
    "question": "원본 문항",
    "experience_analysis": {{
        "candidate_experiences": [
            {{
                "experience": "경험 설명",
                "relevance_score": 85,
                "relevance_reason": "관련성 이유",
                "key_achievements": ["성과 1", "성과 2"],
                "storytelling_potential": "스토리텔링 가능성"
            }}
        ],
        "experience_ranking": [
            {{
                "rank": 1,
                "experience": "가장 적합한 경험",
                "reason": "선택 이유",
                "utilization_strategy": "활용 전략"
            }}
        ]
    }},
    "strategic_guidance": {{
        "experience_selection": "경험 선택 가이드",
        "achievement_emphasis": "성과 강조 방법",
        "skill_demonstration": "스킬 보여주기 방법",
        "narrative_structure": "내러티브 구조 제안"
    }},
    "content_development": {{
        "experience_details": ["상세히 다룰 경험 1", "상세히 다룰 경험 2"],
        "achievement_metrics": ["구체적 수치 1", "구체적 수치 2"],
        "skill_examples": ["스킬 예시 1", "스킬 예시 2"],
        "storytelling_elements": ["스토리텔링 요소 1", "스토리텔링 요소 2"]
    }},
    "writing_guidance": {{
        "structure_recommendation": "구조 제안",
        "content_organization": "내용 구성 방법",
        "emphasis_strategies": ["강조 전략 1", "강조 전략 2"],
        "flow_guidance": "흐름 가이드"
    }},
    "improvement_suggestions": [
        {{
            "area": "개선 영역",
            "suggestion": "개선 제안",
            "priority": "우선순위"
        }}
    ],
    "experience_gaps": [
        {{
            "gap": "경험 부족 영역",
            "compensation_strategy": "보완 전략"
        }}
    ],
    "guidance_summary": "경험 가이드 요약"
}}

Focus on:
1. Identifying the most relevant experiences for each question
2. Maximizing the impact of candidate experiences
3. Providing strategic guidance for experience utilization
4. Helping candidates tell compelling stories
5. Addressing experience gaps and improvement areas
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
        state.analysis_results["experience_guides"] = {
            "analyst": self.name,
            "guides": guides,
            "total_questions": len(questions),
            "timestamp": "2025-08-05"
        }
        
        self.log("경험 가이드 분석 완료")
        return state 
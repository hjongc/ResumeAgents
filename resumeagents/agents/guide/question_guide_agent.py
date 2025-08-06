"""
Question Guide Agent for analyzing self-introduction questions and providing guidance.
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent, AgentState
import json


class QuestionGuideAgent(BaseAgent):
    """Agent responsible for analyzing self-introduction questions and providing comprehensive guidance."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Question Guide Agent",
            role="문항 가이드 전문가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a self-introduction question analysis and guidance expert specializing in understanding question intent and providing strategic guidance.

Your primary responsibilities:
1. Analyze question intent and underlying purpose
2. Identify key requirements and evaluation criteria
3. Provide strategic guidance for optimal responses
4. Assess question difficulty and complexity
5. Create comprehensive guidance for each question

Key analysis considerations:
- Question type and category (motivation, experience, problem-solving, values, skills, etc.)
- Company culture and values reflected in the question
- Required response structure and length
- Key evaluation points and success criteria
- Common pitfalls and what to avoid
- Strategic approach recommendations

Please provide comprehensive guidance in Korean language with structured format. Focus on helping candidates understand what the company truly wants to know and how to respond effectively."""

    async def analyze(self, state: AgentState) -> AgentState:
        """Analyze self-introduction questions and provide comprehensive guidance."""
        custom_questions = state.candidate_info.get("custom_questions", [])
        
        if not custom_questions:
            state.analysis_results["question_guides"] = {
                "status": "no_questions",
                "message": "No custom questions provided",
                "guides": []
            }
            return state
        
        guides = []
        
        for question_data in custom_questions:
            question = question_data.get("question", "")
            char_limit = question_data.get("char_limit")
            char_limit_note = question_data.get("char_limit_note", "")
            
            # 자동 질문 유형 분석
            question_type = await self._analyze_question_type(question)
            
            # 벡터DB 기반 관련 경험 검색 (ProfileManager를 통해)
            relevant_experiences = []
            if hasattr(state, 'profile_manager') and state.profile_manager:
                try:
                    profile_name = state.candidate_info.get("name", "default")
                    relevant_experiences = state.profile_manager.find_relevant_experiences_for_question(
                        profile_name=profile_name,
                        question=question,
                        question_type=question_type,
                        top_k=3
                    )
                except Exception as e:
                    print(f"⚠️  벡터 검색 실패: {e}")
                    relevant_experiences = []
            
            # 글자수 제한 정보
            char_limit_info = ""
            if char_limit:
                from ...utils.text_utils import TextValidator
                char_limit_info = TextValidator.create_character_limit_prompt_instruction(char_limit, char_limit_note)
            
            # 프롬프트 구성
            experiences_context = ""
            if relevant_experiences:
                experiences_context = "\n\nRelevant candidate experiences for this question:\n"
                for i, exp_data in enumerate(relevant_experiences, 1):
                    exp = exp_data["experience"]
                    score = exp_data.get("relevance_score", 0)
                    experiences_context += f"{i}. [{exp.get('type', 'unknown')}] {exp.get('company', exp.get('name', 'Unknown'))}: {exp.get('position', exp.get('description', ''))} (Relevance: {score:.2f})\n"
                    
                    # 주요 성과나 책임 추가
                    if exp.get('achievements'):
                        for ach in exp['achievements'][:2]:  # 최대 2개
                            experiences_context += f"   - Achievement: {ach.get('description', '')}\n"
                    if exp.get('responsibilities'):
                        for resp in exp['responsibilities'][:2]:  # 최대 2개
                            experiences_context += f"   - Responsibility: {resp}\n"
            else:
                experiences_context = "\n\nNote: No specific relevant experiences found in vector database. Use general candidate information."
            
            prompt = f"""
            You are an expert career consultant analyzing self-introduction questions for job applications.
            
            Question to analyze: "{question}"
            Question type: {question_type}
            {char_limit_info}
            
            Company: {state.company_name}
            Position: {state.job_title}
            
            Job Description:
            {state.job_description}
            
            Candidate Information:
            - Name: {state.candidate_info.get('name', '')}
            - Education: {state.candidate_info.get('education', '')}
            - Experience: {state.candidate_info.get('experience', '')}
            - Skills: {state.candidate_info.get('skills', '')}
            - Projects: {state.candidate_info.get('projects', '')}
            
            {experiences_context}
            
            Please provide a comprehensive analysis and guide in the following JSON format.
            The content values should be in Korean, but the JSON structure should use English keys:
            
            {{
                "question": {{
                    "question": "{question}",
                    "type": "{question_type}",
                    "char_limit": {char_limit or "null"},
                    "char_limit_note": "{char_limit_note}",
                    "analysis": "질문의 의도와 평가 포인트 분석 (한국어)"
                }},
                "guide": "이 문항에 대해 어떤 내용을 작성하면 좋을지 상세한 가이드 (한국어로 작성, 구체적인 작성 방향과 포함해야 할 핵심 요소들을 제시)",
                "writing_strategy": {{
                    "structure_recommendation": "글자수 제한을 고려한 구조 추천 (한국어)",
                    "content_allocation": "글자수 배분 가이드 (한국어, 예: 도입부 100자, 본론 600자, 결론 100자)",
                    "key_points_priority": ["우선순위별 핵심 포인트 (한국어)", "두 번째 핵심 포인트", "세 번째 핵심 포인트"]
                }}
            }}
            
            IMPORTANT: If there is a character limit, provide specific guidance on:
            1. How to structure the response within the limit
            2. What content to prioritize
            3. How to allocate characters across different sections
            4. Tips for concise yet impactful writing
            
            Focus on providing actionable guidance that helps the candidate write a compelling response within the constraints.
            """
            
            try:
                response = self.llm.invoke(prompt)
                response_content = response.content.strip()
                
                # JSON 파싱
                if response_content.startswith('```json'):
                    response_content = response_content[7:]
                if response_content.endswith('```'):
                    response_content = response_content[:-3]
                
                guide_data = json.loads(response_content.strip())
                
                # 벡터DB 검색 결과 추가
                guide_data["relevant_experiences"] = relevant_experiences
                guide_data["search_method"] = "vector_db" if relevant_experiences else "fallback"
                
                guides.append(guide_data)
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error for question: {question}")
                print(f"Response: {response_content}")
                guides.append({
                    "question": {"question": question, "type": question_type, "analysis": "분석 실패"},
                    "guide": "가이드 생성에 실패했습니다.",
                    "error": str(e),
                    "relevant_experiences": relevant_experiences,
                    "search_method": "vector_db" if relevant_experiences else "fallback"
                })
            except Exception as e:
                print(f"Error analyzing question: {question}")
                print(f"Error: {str(e)}")
                guides.append({
                    "question": {"question": question, "type": question_type, "analysis": "분석 실패"},
                    "guide": "가이드 생성에 실패했습니다.",
                    "error": str(e),
                    "relevant_experiences": relevant_experiences,
                    "search_method": "vector_db" if relevant_experiences else "fallback"
                })
        
        state.analysis_results["question_guides"] = {
            "status": "completed",
            "total_questions": len(custom_questions),
            "guides": guides
        }
        
        return state
    
    async def _analyze_question_type(self, question_text: str) -> str:
        """Automatically analyze question type."""
        prompt = f"""
Analyze the type of the following self-introduction question:

Question: {question_text}

Classify into one of the following categories:
- motivation: Application motivation, reasons for applying
- experience: Experience, projects, achievements, accomplishments
- problem_solving: Problem solving, overcoming difficulties, challenges
- values: Values, life philosophy, beliefs
- skills: Technical skills, capabilities, expertise
- other: Other types

Respond with only the classification result.
"""

        messages = self._create_messages(prompt)
        result = await self._call_llm(messages)
        
        # Parse result
        result = result.strip().lower()
        if 'motivation' in result:
            return 'motivation'
        elif 'experience' in result:
            return 'experience'
        elif 'problem' in result or 'solving' in result:
            return 'problem_solving'
        elif 'value' in result:
            return 'values'
        elif 'skill' in result:
            return 'skills'
        else:
            return 'other' 
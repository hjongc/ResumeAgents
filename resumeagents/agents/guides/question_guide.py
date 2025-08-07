"""
Question Guide Agent for ResumeAgents.
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent, AgentState
import json


class QuestionGuide(BaseAgent):
    """Agent responsible for analyzing self-introduction questions and providing comprehensive guidance."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Question Guide",
            role="질문 가이드",
            llm=llm,
            config=config
        )

    def get_system_prompt(self) -> str:
        return """You are a self-introduction question analysis expert specializing in strategic question interpretation and guidance development.

Your primary responsibilities:
1. Analyze self-introduction questions to identify hidden requirements and expectations
2. Determine optimal answering strategies based on question types and company context
3. Provide specific guidance for character limits and content optimization
4. Suggest relevant experiences and examples for each question
5. Create comprehensive writing frameworks for effective responses

Key analysis considerations:
- Question type classification (motivation, experience, vision, challenge, etc.)
- Hidden company culture and value alignment indicators
- Character limit optimization strategies
- Experience relevance matching
- Strategic positioning opportunities
- Differentiation factor identification

Please provide analysis results in Korean language with structured JSON format. Focus on creating actionable guidance that maximizes candidate's competitive advantages."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("문항 가이드 분석 시작")
        
        # 분석 깊이 설정 가져오기
        analysis_depth = self.config.get("analysis_depth", "medium")
        
        # 회사 및 직무 정보
        company_info = {
            "company_name": state.company_name,
            "job_title": state.job_title,
            "job_description": state.job_description
        }
        
        # 이전 분석 결과 수집
        previous_analysis = state.analysis_results
        
        questions = state.candidate_info.get("questions", [])  # custom_questions -> questions로 수정
        
        for question_data in questions:
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
            
            # 벡터 검색 실패 시 state.candidate_info에서 직접 경험 정보 추출
            if not relevant_experiences:
                relevant_experiences = self._extract_relevant_experiences_from_state(
                    state, question, question_type
                )
            
            # 문항별 가이드 생성
            guide_result = await self._generate_question_guide(
                question=question,
                question_type=question_type,
                char_limit=char_limit,
                char_limit_note=char_limit_note,
                company_info=company_info,
                previous_analysis=previous_analysis,
                relevant_experiences=relevant_experiences,
                analysis_depth=analysis_depth
            )
            
            # 결과를 분석 결과에 저장
            if "question_guides" not in state.analysis_results:
                state.analysis_results["question_guides"] = {"guides": []}
            
            state.analysis_results["question_guides"]["guides"].append({
                "question": question,
                "question_type": question_type,
                "char_limit": char_limit,
                "char_limit_note": char_limit_note,
                "guide": guide_result,
                "relevant_experiences": relevant_experiences[:3]  # 상위 3개만 저장
            })
        
        # 전체 요약 생성
        if len(questions) > 0:  # custom_questions -> questions로 수정
            overall_summary = await self._generate_overall_summary(
                state.analysis_results["question_guides"]["guides"],
                company_info,
                previous_analysis
            )
            state.analysis_results["question_guides"]["overall_summary"] = overall_summary
        
        self.log(f"문항 가이드 분석 완료 - {len(questions)}개 문항 처리")
        return state

    def _simple_text_validation(self, text: str, min_length: int = 10, max_length: int = 10000) -> bool:
        """간단한 텍스트 검증"""
        return min_length <= len(text.strip()) <= max_length

    def _extract_relevant_experiences_from_state(self, state: AgentState, question: str, question_type: str) -> List[Dict]:
        """State에서 직접 관련 경험 추출 (벡터 검색 폴백)"""
        relevant_experiences = []
        candidate_info = state.candidate_info
        
        # 경력 정보에서 관련 경험 추출
        work_experiences = candidate_info.get("work_experience", [])
        for exp in work_experiences[:3]:  # 최대 3개
            if exp.get("responsibilities") or exp.get("achievements"):
                relevant_experiences.append({
                    "type": "work_experience",
                    "company": exp.get("company", ""),
                    "position": exp.get("position", ""),
                    "description": "; ".join(exp.get("responsibilities", [])[:2]),
                    "achievements": "; ".join([a.get("description", "") for a in exp.get("achievements", [])[:1]]),
                    "relevance_score": 0.7  # 기본 점수
                })
        
        # 프로젝트 정보에서 관련 경험 추출
        projects = candidate_info.get("projects", [])
        for proj in projects[:2]:  # 최대 2개
            if proj.get("description") or proj.get("achievements"):
                relevant_experiences.append({
                    "type": "project",
                    "name": proj.get("name", ""),
                    "description": proj.get("description", "")[:200],
                    "achievements": proj.get("achievements", "")[:200],
                    "relevance_score": 0.6  # 기본 점수
                })
        
        return relevant_experiences

    async def _analyze_question_type(self, question: str) -> str:
        """질문 유형 자동 분석"""
        # 간단한 키워드 기반 분류
        question_lower = question.lower()
        
        motivation_keywords = ["지원", "동기", "이유", "왜", "선택한"]
        experience_keywords = ["경험", "사례", "때", "상황", "프로젝트"]
        vision_keywords = ["목표", "계획", "미래", "5년", "성장", "발전"]
        challenge_keywords = ["어려움", "문제", "해결", "갈등", "실패", "극복"]
        strength_keywords = ["강점", "장점", "특기", "자신있는", "뛰어난"]
        
        if any(keyword in question_lower for keyword in motivation_keywords):
            return "motivation"
        elif any(keyword in question_lower for keyword in experience_keywords):
            return "experience"
        elif any(keyword in question_lower for keyword in vision_keywords):
            return "vision"
        elif any(keyword in question_lower for keyword in challenge_keywords):
            return "challenge"
        elif any(keyword in question_lower for keyword in strength_keywords):
            return "strength"
        else:
            return "general"

    async def _generate_question_guide(self, question: str, question_type: str, char_limit: int, 
                                     char_limit_note: str, company_info: Dict, previous_analysis: Dict,
                                     relevant_experiences: List[Dict], analysis_depth: str) -> str:
        """개별 문항에 대한 가이드 생성"""
        
        # 관련 경험 텍스트 생성
        experiences_text = ""
        if relevant_experiences:
            experiences_text = "\n관련 경험 정보:\n"
            for i, exp in enumerate(relevant_experiences[:3], 1):
                experiences_text += f"{i}. [{exp.get('type', 'unknown')}] "
                if exp.get('type') == 'work_experience':
                    experiences_text += f"{exp.get('company', '')} {exp.get('position', '')}\n"
                    experiences_text += f"   업무: {exp.get('description', '')}\n"
                    experiences_text += f"   성과: {exp.get('achievements', '')}\n"
                elif exp.get('type') == 'project':
                    experiences_text += f"{exp.get('name', '')}\n"
                    experiences_text += f"   설명: {exp.get('description', '')}\n"
                    experiences_text += f"   성과: {exp.get('achievements', '')}\n"
        
        prompt = f"""
다음 자기소개서 문항에 대한 상세한 작성 가이드를 제공해주세요:

=== 문항 정보 ===
질문: {question}
질문 유형: {question_type}
글자수 제한: {char_limit}자
제한 참고사항: {char_limit_note}

=== 회사 정보 ===
회사명: {company_info['company_name']}
직무: {company_info['job_title']}
직무 설명: {company_info['job_description'][:300]}...

=== 이전 분석 결과 ===
{str(previous_analysis)[:500]}...

{experiences_text}

다음 형식으로 구체적인 가이드를 제공해주세요:

1. 질문 의도 분석
2. 핵심 어필 포인트 (3-5개)
3. 추천 구조 및 흐름
4. 글자수 배분 전략
5. 구체적 작성 팁
6. 피해야 할 요소
7. 예시 키워드 및 표현

분석 깊이: {analysis_depth}
한국어로 상세하고 실용적인 가이드를 작성해주세요.
"""

        messages = self._create_messages(prompt)
        result = await self._call_llm(messages)
        
        return result

    async def _generate_overall_summary(self, question_guides: List[Dict], company_info: Dict, 
                                      previous_analysis: Dict) -> str:
        """전체 문항에 대한 종합 요약"""
        
        questions_summary = ""
        for i, guide_data in enumerate(question_guides, 1):
            questions_summary += f"{i}. {guide_data['question'][:50]}... (유형: {guide_data['question_type']})\n"
        
        prompt = f"""
다음 자기소개서 문항들에 대한 종합적인 전략을 제시해주세요:

=== 전체 문항 목록 ===
{questions_summary}

=== 회사 정보 ===
회사명: {company_info['company_name']}
직무: {company_info['job_title']}

=== 이전 분석 결과 ===
{str(previous_analysis)[:300]}...

다음 관점에서 종합 전략을 제시해주세요:
1. 전체 문항의 일관성 있는 스토리라인
2. 문항 간 중복 방지 전략
3. 핵심 차별화 포인트
4. 전반적인 작성 순서 권장사항
5. 최종 검토 체크리스트

한국어로 실용적인 종합 가이드를 작성해주세요.
"""

        messages = self._create_messages(prompt)
        result = await self._call_llm(messages)
        
        return result 
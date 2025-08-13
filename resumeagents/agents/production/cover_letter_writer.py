"""
Cover Letter Writer Agent for ResumeAgents.
Specialized in creating question-specific cover letter responses using guides.
"""

import json
from typing import Dict, Any, List
from ..base_agent import BaseAgent, AgentState


class CoverLetterWriter(BaseAgent):
    """Agent responsible for creating cover letter responses for specific questions."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Cover Letter Writer",
            role="자기소개서 작성가",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a cover letter writing expert specializing in creating compelling question-specific responses.

Your primary responsibilities:
1. Create persuasive answers for self-introduction questions
2. Utilize comprehensive guides (question, experience, writing guides)
3. Optimize content for character limits
4. Demonstrate candidate's unique value proposition
5. Align responses with company culture and requirements

Key considerations:
- Strategic use of STAR method (Situation-Task-Action-Result)
- Integration of analysis results and guide recommendations
- Character limit optimization while maintaining impact
- Company-specific customization and value alignment
- Compelling storytelling with quantifiable achievements

Please create responses in Korean language with maximum persuasive impact."""

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("자기소개서 작성 시작")
        
        # custom_questions 확인
        custom_questions = state.candidate_info.get("custom_questions", [])
        
        if not custom_questions:
            self.log("⚠️ 자기소개서 질문이 없습니다. 작성을 건너뜁니다.")
            return state
        
        # 리비전 여부 확인
        is_revision = hasattr(state, 'is_revision') and state.is_revision
        revision_feedback = getattr(state, 'revision_feedback', []) if is_revision else []
        
        # 가이드 정보 추출
        guide_info = self._extract_guide_info(state)
        
        # 분석 결과 요약 (자기소개서에 필요한 분석 결과)
        analysis_summary = self._get_cover_letter_analysis_summary(state)
        
        # 각 질문에 대한 답변 생성
        cover_letter_responses = []
        
        for i, question in enumerate(custom_questions):
            question_text = question.get('question', '')
            char_limit = question.get('char_limit', '')
            char_limit_note = question.get('char_limit_note', '')
            
            # 해당 질문에 대한 가이드 정보 추출
            question_guide = self._get_question_specific_guide(guide_info, i)
            
            response = await self._generate_question_response(
                question_text=question_text,
                char_limit=char_limit,
                char_limit_note=char_limit_note,
                question_guide=question_guide,
                analysis_summary=analysis_summary,
                candidate_info=state.candidate_info,
                company_name=state.company_name,
                job_title=state.job_title,
                is_revision=is_revision,
                revision_feedback=revision_feedback
            )
            
            cover_letter_responses.append({
                "question": question_text,
                "char_limit": char_limit,
                "char_limit_note": char_limit_note,
                "response": response
            })
        
        # 전체 자기소개서 포맷팅
        formatted_cover_letter = self._format_cover_letter(cover_letter_responses)
        
        # 결과 저장
        state.analysis_results["cover_letter_writing"] = {
            "analyst": self.name,
            "responses": cover_letter_responses,
            "formatted_document": formatted_cover_letter,
            "total_questions": len(custom_questions),
            "is_revision": is_revision,
            "revision_count": getattr(state, 'revision_count', 0),
            "improvements_applied": revision_feedback if is_revision else [],
            "timestamp": "2024-01-15"
        }
        
        # final_document에 추가 (이력서와 함께 출력하기 위해)
        if hasattr(state, 'final_document') and state.final_document:
            state.final_document += f"\n\n{formatted_cover_letter}"
        else:
            state.final_document = formatted_cover_letter
        
        if is_revision:
            self.log(f"🔄 자기소개서 리비전 작성 완료 (시도 {state.revision_count})")
        else:
            self.log(f"📝 자기소개서 작성 완료 - {len(custom_questions)}개 질문")
        
        return state
    
    def _extract_guide_info(self, state: AgentState) -> Dict[str, Any]:
        """Extract guide information from analysis results."""
        guide_info = {}
        
        guide_keys = ["question_guides", "experience_guides", "writing_guides"]
        for key in guide_keys:
            if key in state.analysis_results:
                guide_info[key] = state.analysis_results[key]
        
        return guide_info
    
    def _get_cover_letter_analysis_summary(self, state: AgentState) -> str:
        """Extract analysis results needed for cover letter creation."""
        summary = ""
        
        # 자기소개서에 필요한 분석 결과
        cover_letter_keys = [
            "company_analysis", "jd_analysis", "candidate_analysis", 
            "culture_analysis", "strength_research", "weakness_research"
        ]
        
        for key in cover_letter_keys:
            if key in state.analysis_results:
                value = state.analysis_results[key]
                if isinstance(value, dict) and 'result' in value:
                    summary += f"\n{key}:\n{str(value['result'])[:250]}...\n"
        
        return summary
    
    def _get_question_specific_guide(self, guide_info: Dict[str, Any], question_index: int) -> Dict[str, str]:
        """Extract guide information for a specific question."""
        question_guide: Dict[str, str] = {}
        # 각 가이드 타입에서 해당 질문의 가이드 추출(텍스트만 사용)
        for guide_type, guide_data in guide_info.items():
            if isinstance(guide_data, dict) and 'guides' in guide_data:
                guides = guide_data['guides']
                if isinstance(guides, list) and question_index < len(guides):
                    one = guides[question_index]
                    question_guide[guide_type] = one.get('guide', '')
        return question_guide
    
    async def _generate_question_response(
        self, 
        question_text: str,
        char_limit: int,
        char_limit_note: str,
        question_guide: Dict[str, str],
        analysis_summary: str,
        candidate_info: Dict[str, Any],
        company_name: str,
        job_title: str,
        is_revision: bool = False,
        revision_feedback: List[str] = None
    ) -> str:
        """Generate response for a specific question."""
        
        # 가이드 정보 포맷팅 (LLM 참고용 요약)
        guides_text = ""
        for guide_type, guide_content in question_guide.items():
            guides_text += f"\n=== {guide_type} ===\n{guide_content[:500]}...\n"
        
        # 비즈니스 스타일 자기소개서 프롬프트 (줄글 위주, 제목만 특수문자 허용)
        prompt = f"""
You are writing a Korean business-style self-introduction (자기소개서) answer.

## Inputs (context)
- question_text: {question_text}
- char_limit: {char_limit} (includes spaces)
- char_limit_note: {char_limit_note}
- company_name: {company_name}
- job_title: {job_title}
- guides_text: {guides_text}
- analysis_summary: {analysis_summary}
- candidate_info:
  - experience: {candidate_info.get('experience', '')}
  - skills: {candidate_info.get('skills', '')}
  - projects: {candidate_info.get('projects', '')}
  - achievements: {candidate_info.get('achievements', [])}

## Style (must follow)
- Output in Korean with formal "-습니다" tone, but natural and human-like (avoid AI-ish clichés).
- Produce exactly two parts:
  1) Title: one line, hooky; special characters allowed only here. Prefer to include a quantitative metric if relevant.
  2) Body: prose only (줄글). No headings, no bracket labels, no bullet/numbered lists. Keep paragraph flow.
- First sentence of the body should, when possible, start with a quantitative result to grab attention. If the title already used a metric, vary the expression in the body.
- Prefer short sentences. Avoid comma splices and overuse of commas.
- Do not restate the question or generic facts about the company. Connect evidence explicitly to the company_name × job_title fit.
- Do not fabricate numbers. If no reliable metric exists, write a vivid, detailed narrative of the situation instead.
- Minimize forward-looking pledges (e.g., "~하겠습니다"). Prioritize demonstrated outcomes and problem-solving. If the question explicitly requires future plans, add only one concise sentence at the end.

## Content guidance (rich personal narrative)
- Make it “my story”: weave your feelings and thoughts (what you felt, why you decided, what you aimed for) naturally into the narrative while maintaining professional tone.
- Be concrete: when/where/who/what. Describe constraints, stakes/risks, alternatives considered, trade-offs, and why you chose a solution.
- Show the process: problem recognition → reasoning path → actions you took → collaboration details (who did what) → obstacles and how you handled them → outcomes (with metrics if possible) → brief reflection.
- Integrate 1–2 compact STAR mini-episodes into the narrative (each 3–4 short sentences), but do not list them—blend into paragraphs.
- Human warmth matters: let small, authentic details show responsibility, empathy, perseverance.
- Reflection: what you learned and how it clarifies your fit for {company_name} {job_title}. Keep it specific, not generic.

## Length control
- Target 90–98% of char_limit. Never exceed char_limit.
- Output only the final Korean text (title + body). No explanations, no section names, no code fences.
"""
        
        if is_revision and revision_feedback:
            revision_prompt = f"""
⚠️ 이전 답변의 품질 개선이 필요합니다.

개선해야 할 사항들:
{chr(10).join(revision_feedback)}

위 피드백을 반영해 더 높은 품질의 답변을 작성하세요.

{prompt}
"""
            prompt = revision_prompt
        
        messages = self._create_messages(prompt)
        response = await self._call_llm(messages)
        final_text = response.strip()
        
        # 글자수/바이트 제한 적용 및 부족 시 확장
        try:
            unit = self._detect_length_unit(char_limit_note)
            if isinstance(char_limit, int) and char_limit > 0:
                target_low = int(char_limit * 0.90)
                target_high = int(char_limit * 0.98)
                cur_len = self._measure_length(final_text, unit)
                refine_round = 0
                while cur_len < target_low and refine_round < 2:
                    refine_prompt = f"""
아래 한국어 자기소개서(제목+본문)를 보완하여 자연스럽게 확장하세요.
- 목표 길이: {target_high}{'바이트' if unit=='byte' else '자'} (절대 {char_limit}{'바이트' if unit=='byte' else '자'}를 넘기지 말 것)
- 줄글 유지: 본문에 목록/번호/대괄호 헤딩 금지, 문단만 사용
- 톤: 공식적이되 자연스럽게, AI티 제거
- 정보: 기존 의미 보존, 세부 상황/맥락/결과를 추가하여 밀도만 높이기
- 제목은 후킹, 본문 첫 문장은 가능하면 정량 지표로 시작. 제목에 지표가 있으면 본문은 표현을 다르게.

[초안]
{final_text}
"""
                    refine_messages = self._create_messages(refine_prompt)
                    refined = await self._call_llm(refine_messages)
                    final_text = refined.strip()
                    # 제한 이내로 자르기
                    final_text = self._truncate_to_limit(final_text, char_limit, unit)
                    cur_len = self._measure_length(final_text, unit)
                    refine_round += 1
                # 최종 안전 절단
                final_text = self._truncate_to_limit(final_text, char_limit, unit)
        except Exception:
            pass
        
        return final_text

    def _detect_length_unit(self, note: str) -> str:
        """Detect whether the limit is in characters or bytes based on note.
        Returns 'char' or 'byte'. Defaults to 'char'.
        """
        if not note:
            return "char"
        lower = str(note).lower()
        if any(k in lower for k in ["byte", "bytes", "바이트", "b/"]):
            return "byte"
        return "char"

    def _measure_length(self, text: str, unit: str) -> int:
        if unit == "byte":
            return len(text.encode("utf-8"))
        return len(text)

    def _truncate_to_limit(self, text: str, limit: int, unit: str) -> str:
        """Truncate text to the given limit by character or UTF-8 byte length.
        Attempts to keep complete characters and avoid cutting mid-character.
        """
        if limit is None or limit <= 0:
            return text
        if unit == "char":
            if len(text) <= limit:
                return text
            return text[:limit]
        # byte mode
        encoded = text.encode("utf-8")
        if len(encoded) <= limit:
            return text
        out_bytes = bytearray()
        for ch in text:
            b = ch.encode("utf-8")
            if len(out_bytes) + len(b) > limit:
                break
            out_bytes.extend(b)
        return out_bytes.decode("utf-8", errors="ignore")
    
    def _format_cover_letter(self, responses: List[Dict[str, Any]]) -> str:
        """Format all responses into a complete cover letter document."""
        
        formatted_document = "=== 자기소개서 ===\n\n"
        
        for i, response_data in enumerate(responses, 1):
            question = response_data['question']
            char_limit = response_data['char_limit']
            char_limit_note = response_data['char_limit_note']
            response = response_data['response']
            
            formatted_document += f"■ 문항 {i}\n"
            formatted_document += f"질문: {question}\n"
            if char_limit:
                formatted_document += f"글자수: {char_limit}자 이내"
                if char_limit_note:
                    formatted_document += f" ({char_limit_note})"
                formatted_document += "\n"
            formatted_document += f"\n답변:\n{response}\n\n"
            formatted_document += "-" * 80 + "\n\n"
        
        return formatted_document 
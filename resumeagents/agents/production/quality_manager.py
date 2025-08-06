"""
Quality Manager Agent for ResumeAgents.
"""

import json
import re
from typing import Dict, Any
from ..base_agent import BaseAgent, AgentState


class QualityManager(BaseAgent):
    """Agent responsible for quality control and final review."""
    
    def __init__(self, llm=None, config=None):
        super().__init__(
            name="Quality Manager",
            role="품질 관리자",
            llm=llm,
            config=config
        )
    
    def get_system_prompt(self) -> str:
        return """You are a quality control and strategic review expert specializing in comprehensive document evaluation.

Your primary responsibilities:
1. Evaluate document quality and effectiveness
2. Assess clarity, consistency, and impact
3. Evaluate alignment with company requirements
4. Provide improvement suggestions and optimization recommendations
5. Make final approval/rejection decisions

Key evaluation criteria:
- Content clarity and readability
- Alignment with company requirements
- Effective emphasis of candidate strengths
- Grammar and expression accuracy
- Structure and format appropriateness
- Clarity of differentiation factors
- Impact and persuasiveness

Please provide evaluation results in Korean language with structured JSON format. Focus on objective and constructive feedback."""

    def _extract_quality_score(self, quality_result: str) -> float:
        """품질 평가 결과에서 점수를 추출합니다."""
        try:
            # JSON 형태로 파싱 시도
            if '{' in quality_result and '}' in quality_result:
                # JSON 부분만 추출
                json_match = re.search(r'\{.*\}', quality_result, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    quality_data = json.loads(json_str)
                    
                    # overall_quality_score 추출
                    if 'overall_quality_score' in quality_data:
                        return float(quality_data['overall_quality_score']) / 100.0  # 0-1 범위로 변환
                    
                    # 개별 점수들의 평균 계산
                    scores = []
                    score_keys = ['clarity_score', 'alignment_score', 'emphasis_score', 
                                'grammar_score', 'structure_score', 'differentiation_score', 'impact_score']
                    
                    for key in score_keys:
                        if key in quality_data:
                            scores.append(float(quality_data[key]))
                    
                    if scores:
                        return sum(scores) / len(scores) / 100.0  # 0-1 범위로 변환
            
            # 숫자 패턴 찾기 (예: "85점", "85/100", "0.85" 등)
            number_patterns = [
                r'(\d+(?:\.\d+)?)\s*점',  # "85점"
                r'(\d+(?:\.\d+)?)\s*/\s*100',  # "85/100"
                r'전체.*?(\d+(?:\.\d+)?)',  # "전체 점수 85"
                r'(\d+(?:\.\d+)?)(?:\s*%)?$'  # 마지막 숫자
            ]
            
            for pattern in number_patterns:
                matches = re.findall(pattern, quality_result)
                if matches:
                    score = float(matches[-1])  # 마지막 매치 사용
                    # 0-1 범위로 정규화
                    if score > 1:
                        score = score / 100.0
                    return min(max(score, 0.0), 1.0)  # 0-1 범위로 클램핑
                    
        except Exception as e:
            self.log(f"품질 점수 추출 실패: {e}")
        
        # 기본값 반환
        return 0.75  # 75% 기본 점수

    async def analyze(self, state: AgentState) -> AgentState:
        self.log("품질 관리 시작")
        
        if not state.final_document:
            self.log("검토할 서류가 없습니다.")
            return state
        
        # 모든 분석 결과를 종합
        analysis_summary = ""
        for key, value in state.analysis_results.items():
            if isinstance(value, dict) and 'result' in value:
                analysis_summary += f"\n{key}: {str(value['result'])[:200]}...\n"
        
        # 품질 임계값 가져오기
        quality_threshold = self.config.get('quality_threshold', 0.8)
        
        prompt = f"""
다음 자기소개서의 품질을 평가해주세요:

회사: {state.company_name}
직무: {state.job_title}
품질 기준: {quality_threshold * 100}점 이상

분석 결과 요약:
{analysis_summary}

작성된 문서:
{state.final_document}

다음 기준으로 평가해주세요 (각 항목 0-100점):
1. 내용 명확성과 가독성
2. 회사 요구사항과의 일치도
3. 지원자 강점의 효과적 강조
4. 문법과 표현의 정확성
5. 구조와 형식의 적절성
6. 차별화 요소의 명확성
7. 임팩트와 설득력

다음 JSON 형식으로 평가 결과를 제공해주세요:
{{
    "clarity_score": 85,
    "alignment_score": 90,
    "emphasis_score": 88,
    "grammar_score": 92,
    "structure_score": 87,
    "differentiation_score": 85,
    "impact_score": 89,
    "overall_quality_score": 88,
    "improvement_suggestions": ["구체적인 개선 제안사항들"],
    "approval_decision": "승인" 또는 "수정 필요",
    "evaluation_summary": "품질 평가 요약"
}}
"""

        messages = self._create_messages(prompt)
        quality_result = await self._call_llm(messages)
        
        # 품질 점수 추출
        quality_score = self._extract_quality_score(quality_result)
        state.quality_score = quality_score
        
        # 품질 평가 결과를 상태에 저장
        state.analysis_results["quality_assessment"] = {
            "analyst": self.name,
            "result": quality_result,
            "quality_score": quality_score,
            "threshold": quality_threshold,
            "passed": quality_score >= quality_threshold,
            "timestamp": "2024-01-15"
        }
        
        self.log(f"품질 평가 완료: {quality_score:.2f} (기준: {quality_threshold:.2f})")
        
        if quality_score >= quality_threshold:
            self.log("✅ 품질 기준 통과")
        else:
            self.log("❌ 품질 기준 미달 - 수정 필요")
        
        return state 
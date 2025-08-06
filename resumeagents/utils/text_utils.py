"""
Text utilities for character counting and validation.
"""

import re
from typing import Dict, Any, Tuple


class TextValidator:
    """Text validation and character counting utilities."""
    
    @staticmethod
    def count_characters(text: str, include_spaces: bool = True, korean_standard: bool = True) -> int:
        """
        Count characters in text using Korean standard.
        
        Args:
            text: Text to count
            include_spaces: Whether to include spaces in count
            korean_standard: Use Korean character counting standard (True = 1 char per character, False = English standard)
            
        Returns:
            Character count
        """
        if not text:
            return 0
        
        if not include_spaces:
            text = text.replace(' ', '').replace('\n', '').replace('\t', '')
        
        # Korean standard: each Unicode character counts as 1
        # This is the standard for Korean job applications
        if korean_standard:
            return len(text)
        else:
            # English standard (rarely used in Korea)
            return len(text.encode('utf-8'))
    
    @staticmethod
    def validate_character_limit(text: str, char_limit: int, include_spaces: bool = True) -> Dict[str, Any]:
        """
        Validate text against character limit using Korean standard.
        
        Args:
            text: Text to validate
            char_limit: Character limit
            include_spaces: Whether to include spaces in count
            
        Returns:
            Validation result dictionary
        """
        char_count = TextValidator.count_characters(text, include_spaces, korean_standard=True)
        
        return {
            "char_count": char_count,
            "char_limit": char_limit,
            "is_valid": char_count <= char_limit,
            "remaining": char_limit - char_limit,
            "over_limit": max(0, char_count - char_limit),
            "usage_percentage": round((char_count / char_limit) * 100, 1) if char_limit > 0 else 0,
            "counting_method": "한글 기준 (1글자 = 1자)"
        }
    
    @staticmethod
    def get_character_limit_guidance(char_limit: int) -> Dict[str, Any]:
        """
        Get guidance for different character limits (Korean standard).
        
        Args:
            char_limit: Character limit
            
        Returns:
            Guidance dictionary
        """
        if char_limit <= 300:
            return {
                "difficulty": "매우 높음",
                "structure": "핵심 메시지 1개 + 간단한 근거",
                "example_allocation": {
                    "핵심 메시지": "150자 (50%)",
                    "구체적 근거": "100자 (33%)", 
                    "마무리": "50자 (17%)"
                },
                "tips": [
                    "가장 임팩트 있는 경험 1개만 선택",
                    "불필요한 수식어 완전 제거",
                    "간결하고 명확한 문장 구성",
                    "구체적인 수치로 임팩트 강화"
                ]
            }
        elif char_limit <= 600:
            return {
                "difficulty": "높음", 
                "structure": "도입(50자) + 핵심내용(450자) + 마무리(100자)",
                "example_allocation": {
                    "도입부": "50자 (8%)",
                    "핵심 경험": "350자 (58%)",
                    "성과/학습": "100자 (17%)",
                    "마무리": "100자 (17%)"
                },
                "tips": [
                    "핵심 경험 1-2개 선택",
                    "STAR 기법의 A(Action)와 R(Result)에 집중",
                    "구체적인 수치와 결과 포함",
                    "간결한 문장으로 임팩트 극대화"
                ]
            }
        elif char_limit <= 1000:
            return {
                "difficulty": "보통",
                "structure": "도입(100자) + 본론(700자) + 결론(200자)",
                "example_allocation": {
                    "도입부": "100자 (10%)",
                    "경험 1": "300자 (30%)",
                    "경험 2": "250자 (25%)",
                    "성과/학습": "150자 (15%)",
                    "결론/포부": "200자 (20%)"
                },
                "tips": [
                    "2-3개의 핵심 경험 포함 가능",
                    "완전한 STAR 기법 활용",
                    "구체적인 성과와 학습점 강조",
                    "경험 간 연결성 제시"
                ]
            }
        elif char_limit <= 1500:
            return {
                "difficulty": "낮음",
                "structure": "도입(150자) + 본론(1000자) + 결론(350자)",
                "example_allocation": {
                    "도입부": "150자 (10%)",
                    "주요 경험 1": "400자 (27%)",
                    "주요 경험 2": "350자 (23%)",
                    "추가 경험": "250자 (17%)",
                    "결론/비전": "350자 (23%)"
                },
                "tips": [
                    "3-4개의 경험 상세 서술 가능",
                    "스토리텔링 기법 활용",
                    "경험간 연결고리 제시",
                    "구체적인 미래 계획 포함"
                ]
            }
        else:
            return {
                "difficulty": "매우 낮음",
                "structure": "자유로운 구성 가능",
                "example_allocation": {
                    "도입부": "200자 (10%)",
                    "경험 서술": "1200자 (60%)",
                    "성장/학습": "400자 (20%)",
                    "미래 비전": "200자 (10%)"
                },
                "tips": [
                    "다양한 경험 포괄적 서술",
                    "상세한 배경과 과정 설명",
                    "미래 비전까지 포함",
                    "개인의 성장 스토리 구성"
                ]
            }
    
    @staticmethod
    def suggest_content_allocation(char_limit: int, question_type: str) -> Dict[str, Any]:
        """
        Suggest content allocation based on character limit and question type.
        
        Args:
            char_limit: Character limit
            question_type: Type of question (motivation, experience, etc.)
            
        Returns:
            Content allocation suggestion
        """
        base_allocation = {
            "motivation": {
                "지원 배경": 0.2,  # 지원 배경
                "지원 동기": 0.5,      # 지원 동기
                "입사 후 포부": 0.3       # 입사 후 포부
            },
            "experience": {
                "상황 설명": 0.2,   # 상황 설명
                "행동 및 과정": 0.5,      # 행동 및 과정
                "결과 및 학습": 0.3       # 결과 및 학습
            },
            "problem_solving": {
                "문제 상황": 0.3,     # 문제 상황
                "해결 과정": 0.4,    # 해결 과정
                "결과 및 교훈": 0.3      # 결과 및 교훈
            },
            "values": {
                "가치관 설명": 0.3,   # 가치관 설명
                "구체적 사례": 0.5,     # 구체적 사례
                "적용 방안": 0.2  # 적용 방안
            },
            "skills": {
                "스킬 소개": 0.2, # 스킬 소개
                "증명 사례": 0.6,    # 증명 사례
                "발전 계획": 0.2       # 발전 계획
            }
        }
        
        allocation = base_allocation.get(question_type, base_allocation["experience"])
        
        return {
            section: {
                "chars": int(char_limit * ratio),
                "percentage": int(ratio * 100),
                "description": f"{section}: {int(char_limit * ratio)}자 ({int(ratio * 100)}%)"
            }
            for section, ratio in allocation.items()
        }
    
    @staticmethod
    def format_character_info(char_count: int, char_limit: int, char_limit_note: str = "") -> str:
        """
        Format character count information for display.
        
        Args:
            char_count: Current character count
            char_limit: Character limit
            char_limit_note: Additional note about the limit
            
        Returns:
            Formatted string
        """
        if char_limit:
            status = "✅" if char_count <= char_limit else "❌"
            percentage = round((char_count / char_limit) * 100, 1)
            
            info = f"{status} {char_count}/{char_limit}자 ({percentage}%) - 한글 기준"
            if char_limit_note:
                info += f" ({char_limit_note})"
            
            if char_count > char_limit:
                over = char_count - char_limit
                info += f" 🚨 초과: {over}자"
            elif char_count == char_limit:
                info += f" 🎯 정확히 맞음"
            else:
                remaining = char_limit - char_count
                info += f" ⏳ 여유: {remaining}자"
            
            return info
        else:
            return f"📝 {char_count}자 (제한 없음)"
    
    @staticmethod
    def create_character_limit_prompt_instruction(char_limit: int, char_limit_note: str = "") -> str:
        """
        Create clear instruction for LLM about character limits in Korean standard.
        
        Args:
            char_limit: Character limit
            char_limit_note: Additional note about the limit
            
        Returns:
            Formatted instruction for LLM
        """
        if not char_limit:
            return ""
        
        instruction = f"""
CRITICAL CHARACTER LIMIT INSTRUCTION:
- Character Limit: EXACTLY {char_limit} Korean characters
- Counting Method: Korean Standard (1 character = 1 count, regardless of language)
- This means: '안' = 1 char, 'A' = 1 char, ' ' = 1 char, '.' = 1 char
- Note: {char_limit_note}

EXAMPLES of Korean character counting:
- "안녕하세요" = 5 characters
- "Hello" = 5 characters  
- "안녕 Hello" = 8 characters (including space)
- "안녕하세요. 저는 김개발입니다." = 16 characters

IMPORTANT: 
- Use Python len() function logic for counting
- Each Unicode character (한글, English, numbers, punctuation, spaces) = 1 count
- DO NOT use byte-based counting or English word-based counting
- The response content must be EXACTLY within {char_limit} characters when counted by len() in Python

When providing guidance, always specify character allocation in Korean standard.
"""
        return instruction 
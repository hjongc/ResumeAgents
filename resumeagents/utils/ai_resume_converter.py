#!/usr/bin/env python3
"""
AI 기반 이력서 자동 변환 도구 - ResumeAgents 통합 버전

ResumeAgents의 설정 시스템과 모델 분류를 활용하여 기존 이력서를 JSON 프로필로 변환합니다.
DEVELOPMENT_STRATEGY.md의 아키텍처를 준수하며 기존 시스템과 완전 통합됩니다.

사용 방법:
1. python -m resumeagents.utils.ai_resume_converter 실행
2. 이력서 파일 경로 입력
3. 연구 깊이 선택 (LOW/MEDIUM/HIGH)
4. AI가 자동으로 분석하여 JSON 프로필 생성
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# ResumeAgents 모듈 import
from ..default_config import DEFAULT_CONFIG, get_depth_config
from ..utils import get_model_for_agent, get_research_depth_config
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIResumeConverter:
    """AI 기반 이력서 변환기 - ResumeAgents 통합 버전"""
    
    def __init__(self, research_depth: str = "MEDIUM"):
        """
        초기화
        
        Args:
            research_depth: 연구 깊이 (LOW/MEDIUM/HIGH)
        """
        # API 키 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            print("💡 .env 파일에 OPENAI_API_KEY=your_key_here 를 추가하세요")
            sys.exit(1)
        
        # ResumeAgents 설정 시스템 활용
        self.research_depth = research_depth.upper()
        self.config = DEFAULT_CONFIG.copy()
        self.config["research_depth"] = self.research_depth
        
        # Depth별 설정 로드
        depth_config = get_depth_config(self.research_depth)
        self.config.update(depth_config)
        
        print(f"🔧 ResumeAgents 설정 로드 완료:")
        print(f"   연구 깊이: {self.research_depth}")
        print(f"   품질 임계값: {self.config['quality_threshold']}")
        print(f"   최대 토큰: {self.config['max_tokens']}")
        
        # 변환 작업에 적합한 모델 선택 (Quick Think 모델 사용)
        conversion_model = get_model_for_agent("resume_conversion", self.config)
        
        # LLM 초기화 (ResumeAgents 방식)
        llm_config = {
            "model": conversion_model,
            "temperature": 0.1,  # 일관된 분석을 위해 낮은 temperature
            "max_tokens": self.config.get("max_tokens", 4000)
        }
        
        self.llm = ChatOpenAI(**llm_config)
        
        print(f"✅ AI 변환기 초기화 완료 (모델: {conversion_model})")
    
    def read_resume_file(self, file_path: str) -> str:
        """이력서 파일을 읽어옵니다."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        try:
            # 파일 확장자에 따른 처리
            if file_path.lower().endswith('.pdf'):
                return self._extract_text_from_pdf(file_path)
            else:
                # 텍스트 파일로 처리 (다중 인코딩 지원)
                encodings = ['utf-8', 'cp949', 'latin-1', 'euc-kr']
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        
                        if not content.strip():
                            raise ValueError("파일이 비어있습니다.")
                        
                        print(f"✅ 파일 읽기 성공 (인코딩: {encoding})")
                        return content
                        
                    except UnicodeDecodeError:
                        continue
                
                raise ValueError("지원되는 인코딩으로 파일을 읽을 수 없습니다.")
                
        except Exception as e:
            print(f"❌ 파일 읽기 오류: {e}")
            raise
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF에서 텍스트를 추출합니다."""
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            print("⚠️  PDF 처리를 위해 PyPDF2를 설치해야 합니다:")
            print("   pip install PyPDF2")
            print("💡 또는 PDF를 텍스트로 변환하여 .txt 파일로 저장한 후 다시 시도하세요")
            return ""
        except Exception as e:
            print(f"❌ PDF 읽기 오류: {e}")
            return ""
    
    def create_conversion_prompt(self, resume_text: str) -> str:
        """
        ResumeAgents 프로필 형식에 맞는 변환 프롬프트를 생성합니다.
        DEVELOPMENT_STRATEGY.md의 프로필 구조를 반영합니다.
        """
        return f"""
다음 이력서 텍스트를 분석하여 ResumeAgents 프로필 형식의 JSON으로 변환해주세요.

=== 이력서 텍스트 ===
{resume_text}
=== 이력서 텍스트 끝 ===

ResumeAgents 시스템에서 사용하는 다음 JSON 구조로 정확히 변환해주세요:

{{
  "personal_info": {{
    "name": "이름 (필수)",
    "email": "이메일",
    "phone": "전화번호",
    "location": "거주지역"
  }},
  "education": [
    {{
      "degree": "학위 (학사/석사/박사)",
      "major": "전공",
      "university": "학교명",
      "graduation_year": "졸업년도",
      "gpa": "학점 (선택사항)",
      "relevant_courses": ["관련 과목들"],
      "honors": ["수상내역들"]
    }}
  ],
  "work_experience": [
    {{
      "company": "회사명",
      "position": "직책",
      "duration": {{
        "start": "YYYY-MM 형식",
        "end": "YYYY-MM 형식 또는 current"
      }},
      "department": "부서명",
      "responsibilities": ["주요 업무들"],
      "achievements": [
        {{
          "description": "성과 설명",
          "metrics": "정량적 지표 (숫자 포함)",
          "impact": "비즈니스 임팩트"
        }}
      ],
      "technologies": ["사용 기술들"],
      "team_size": "팀 규모",
      "key_projects": ["핵심 프로젝트들"]
    }}
  ],
  "projects": [
    {{
      "name": "프로젝트명",
      "type": "개인/팀/회사 프로젝트",
      "duration": {{
        "start": "YYYY-MM",
        "end": "YYYY-MM"
      }},
      "description": "프로젝트 상세 설명",
      "role": "본인 역할과 책임",
      "technologies": ["사용 기술 스택"],
      "achievements": "구체적 성과와 결과",
      "github_url": "GitHub 저장소 URL",
      "demo_url": "데모/배포 URL",
      "team_size": "팀 규모"
    }}
  ],
  "skills": {{
    "programming_languages": ["프로그래밍 언어들"],
    "frameworks": ["프레임워크/라이브러리들"],
    "databases": ["데이터베이스들"],
    "tools": ["개발/협업 도구들"],
    "cloud_platforms": ["클라우드 서비스들"]
  }},
  "certifications": [
    {{
      "name": "자격증명",
      "issuer": "발급기관",
      "date": "취득일 (YYYY-MM)",
      "expiry": "만료일 (있다면)",
      "score": "점수 (있다면)"
    }}
  ],
  "awards": [
    {{
      "name": "수상명",
      "issuer": "수여기관",
      "date": "수상일 (YYYY-MM)",
      "description": "수상 내용과 의미"
    }}
  ],
  "interests": ["관심 분야들"],
  "career_goals": {{
    "short_term": "단기 목표 (1-2년)",
    "long_term": "장기 목표 (3-5년)",
    "target_companies": ["관심 회사들"],
    "preferred_roles": ["희망 직무들"]
  }},
  "portfolio_links": {{
    "github": "GitHub 프로필 URL",
    "blog": "기술 블로그 URL",
    "linkedin": "LinkedIn 프로필 URL",
    "portfolio": "포트폴리오 사이트 URL"
  }}
}}

중요한 변환 지침:
1. **정확성**: 텍스트에 명시되지 않은 정보는 빈 문자열 "" 또는 빈 배열 []로 설정
2. **날짜 형식**: 모든 날짜는 YYYY-MM 형식으로 통일 (예: 2023-03)
3. **기술 분류**: 기술들을 적절한 카테고리로 정확히 분류
4. **성과 구조화**: achievements는 반드시 description, metrics, impact 구조로 작성
5. **정량적 지표**: 숫자가 있는 성과는 metrics에 명확히 기록
6. **JSON 유효성**: 반드시 유효한 JSON 형식으로 응답
7. **한국어 사용**: 모든 텍스트 내용은 한국어로 작성

연구 깊이: {self.research_depth}
품질 기준: {self.config['quality_threshold']}

JSON으로만 응답해주세요:
"""
    
    async def convert_resume_to_profile(self, resume_text: str) -> Dict[str, Any]:
        """이력서 텍스트를 ResumeAgents 프로필 JSON으로 변환합니다."""
        print(f"🤖 AI가 이력서를 분석하고 있습니다... (깊이: {self.research_depth})")
        
        # 프롬프트 생성
        prompt = self.create_conversion_prompt(resume_text)
        
        # AI 호출 (ResumeAgents 방식)
        messages = [
            SystemMessage(content="""당신은 ResumeAgents 시스템의 이력서 분석 전문가입니다. 
주어진 이력서 텍스트를 정확하게 분석하여 ResumeAgents 프로필 형식의 구조화된 JSON으로 변환합니다.
특히 정량적 성과, 기술 스택 분류, 경험의 임팩트를 정확히 추출하는 것이 중요합니다."""),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            json_text = response.content.strip()
            
            # JSON 파싱 시도
            try:
                profile = json.loads(json_text)
                
                # ResumeAgents 메타데이터 추가
                profile.update({
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "version": "2.0",
                    "conversion_method": "AI_automated",
                    "research_depth": self.research_depth,
                    "vectordb_synced": False
                })
                
                return profile
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 오류: {e}")
                print(f"AI 응답 미리보기: {json_text[:300]}...")
                
                # JSON 수정 시도
                return self._fix_json_response(json_text)
                
        except Exception as e:
            print(f"❌ AI 변환 오류: {e}")
            raise
    
    def _fix_json_response(self, json_text: str) -> Dict[str, Any]:
        """잘못된 JSON 응답을 수정 시도합니다."""
        print("🔧 JSON 형식을 수정하고 있습니다...")
        
        # 일반적인 JSON 오류 수정
        json_text = json_text.strip()
        
        # 코드 블록 마크다운 제거
        if json_text.startswith("```"):
            lines = json_text.split('\n')
            json_text = '\n'.join(lines[1:-1])
        
        # 다시 파싱 시도
        try:
            return json.loads(json_text)
        except:
            # ResumeAgents 호환 빈 템플릿 반환
            print("⚠️  자동 변환 실패. ResumeAgents 호환 템플릿을 사용합니다.")
            return self._create_resumeagents_template()
    
    def _create_resumeagents_template(self) -> Dict[str, Any]:
        """ResumeAgents 호환 빈 템플릿을 생성합니다."""
        from .profile_manager import ProfileManager
        
        # ProfileManager를 사용하여 표준 템플릿 생성
        pm = ProfileManager()
        template = pm.create_profile_template()
        
        # 변환 메타데이터 추가
        template.update({
            "conversion_method": "template_fallback",
            "research_depth": self.research_depth
        })
        
        return template
    
    def save_profile(self, profile: Dict[str, Any], filename: str) -> str:
        """프로필을 ResumeAgents profiles 폴더에 저장합니다."""
        # ResumeAgents 프로젝트 루트 찾기
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        profiles_dir = project_root / "profiles"
        
        profiles_dir.mkdir(exist_ok=True)
        filepath = profiles_dir / f"{filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def print_conversion_summary(self, profile: Dict[str, Any]):
        """변환 결과 요약을 출력합니다."""
        print(f"\n📊 변환 결과 요약 (깊이: {self.research_depth}):")
        print(f"👤 이름: {profile.get('personal_info', {}).get('name', '미확인')}")
        print(f"🎓 학력: {len(profile.get('education', []))}개")
        print(f"💼 경력: {len(profile.get('work_experience', []))}개")
        print(f"🚀 프로젝트: {len(profile.get('projects', []))}개")
        print(f"🏆 자격증: {len(profile.get('certifications', []))}개")
        print(f"🥇 수상: {len(profile.get('awards', []))}개")
        
        # 기술 스택 요약
        skills = profile.get('skills', {})
        total_skills = sum(len(v) for v in skills.values() if isinstance(v, list))
        print(f"💻 기술 스택: {total_skills}개")
        
        # 변환 품질 정보
        conversion_method = profile.get('conversion_method', 'unknown')
        print(f"🔧 변환 방식: {conversion_method}")

async def main():
    """메인 함수"""
    print("🤖 ResumeAgents AI 이력서 변환기")
    print("="*50)
    print("📋 DEVELOPMENT_STRATEGY.md 기반 통합 변환 도구")
    print()
    
    # 연구 깊이 선택
    print("🎯 연구 깊이를 선택하세요:")
    print("1. LOW    - 빠른 변환 (gpt-4o-mini)")
    print("2. MEDIUM - 균형잡힌 변환 (기본값)")
    print("3. HIGH   - 정밀 변환 (고급 모델)")
    
    depth_choice = input("\n선택 (1-3) [기본값: 2]: ").strip() or "2"
    depth_map = {"1": "LOW", "2": "MEDIUM", "3": "HIGH"}
    research_depth = depth_map.get(depth_choice, "MEDIUM")
    
    # 변환기 초기화
    try:
        converter = AIResumeConverter(research_depth=research_depth)
    except SystemExit:
        return
    
    # 이력서 파일 입력
    while True:
        file_path = input("\n📄 이력서 파일 경로를 입력하세요: ").strip()
        if not file_path:
            print("❌ 파일 경로를 입력해주세요.")
            continue
        
        try:
            # 파일 읽기
            print(f"📖 파일을 읽고 있습니다: {file_path}")
            resume_text = converter.read_resume_file(file_path)
            
            if not resume_text.strip():
                print("❌ 파일이 비어있거나 읽을 수 없습니다.")
                continue
            
            print(f"✅ 파일 읽기 완료 ({len(resume_text)} 문자)")
            print(f"📝 미리보기: {resume_text[:200]}...")
            
            break
            
        except Exception as e:
            print(f"❌ 파일 읽기 오류: {e}")
            continue
    
    # AI 변환 실행
    try:
        profile = await converter.convert_resume_to_profile(resume_text)
        
        # 결과 요약 출력
        converter.print_conversion_summary(profile)
        
        # 파일명 입력
        default_name = profile.get('personal_info', {}).get('name', 'converted_profile')
        default_name = default_name.replace(' ', '_').replace('/', '_') if default_name else 'converted_profile'
        
        filename = input(f"\n💾 저장할 파일명 (기본값: {default_name}): ").strip() or default_name
        
        # 파일 저장
        filepath = converter.save_profile(profile, filename)
        
        print(f"\n✅ 변환 완료!")
        print(f"📁 저장 위치: {filepath}")
        print(f"📄 파일 크기: {os.path.getsize(filepath)} bytes")
        
        print(f"\n🎯 다음 단계:")
        print(f"1. 저장된 JSON 파일을 확인하고 필요시 수정")
        print(f"2. ResumeAgents 실행: python main.py")
        print(f"3. 옵션 2 선택: 기존 프로필 사용")
        print(f"4. 프로필 선택: {filename}")
        print(f"5. 연구 깊이: {research_depth} 사용 권장")
        
    except Exception as e:
        print(f"❌ 변환 실패: {e}")
        print("💡 수동 변환 도구를 사용해보세요:")
        print("   python -m resumeagents.utils.convert_resume")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 
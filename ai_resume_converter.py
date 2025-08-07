#!/usr/bin/env python3
"""
AI 기반 이력서 자동 변환 도구

기존 이력서 텍스트/PDF를 ResumeAgents 프로필 형식으로 자동 변환합니다.
OpenAI GPT를 사용하여 텍스트를 분석하고 구조화된 JSON으로 변환합니다.

사용 방법:
1. 기존 이력서를 텍스트 파일로 저장 (또는 PDF에서 텍스트 추출)
2. python ai_resume_converter.py 실행
3. 이력서 파일 경로 입력
4. AI가 자동으로 분석하여 JSON 프로필 생성
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

class AIResumeConverter:
    """AI 기반 이력서 변환기"""
    
    def __init__(self):
        """초기화"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            print("💡 .env 파일에 OPENAI_API_KEY=your_key_here 를 추가하세요")
            sys.exit(1)
        
        # GPT 모델 초기화 (분석용으로 강력한 모델 사용)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # 비용 효율적이면서 성능 좋은 모델
            temperature=0.1,      # 일관된 분석을 위해 낮은 temperature
            max_tokens=4000
        )
        
        print("✅ AI 이력서 변환기 초기화 완료")
    
    def read_resume_file(self, file_path: str) -> str:
        """이력서 파일을 읽어옵니다."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        try:
            # 파일 확장자에 따른 처리
            if file_path.lower().endswith('.pdf'):
                return self._extract_text_from_pdf(file_path)
            else:
                # 텍스트 파일로 처리
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 파일이 비어있는지 확인
                if not content.strip():
                    raise ValueError("파일이 비어있습니다.")
                
                return content
                
        except UnicodeDecodeError:
            # UTF-8로 읽기 실패 시 다른 인코딩 시도
            try:
                with open(file_path, 'r', encoding='cp949') as f:
                    return f.read()
            except:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
    
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
            print("⚠️  PDF 처리를 위해 PyPDF2를 설치해야 합니다: pip install PyPDF2")
            print("💡 PDF를 텍스트로 변환하여 .txt 파일로 저장한 후 다시 시도하세요")
            return ""
        except Exception as e:
            print(f"❌ PDF 읽기 오류: {e}")
            return ""
    
    def create_conversion_prompt(self, resume_text: str) -> str:
        """이력서 변환을 위한 프롬프트를 생성합니다."""
        return f"""
다음 이력서 텍스트를 분석하여 ResumeAgents 프로필 형식의 JSON으로 변환해주세요.

=== 이력서 텍스트 ===
{resume_text}
=== 이력서 텍스트 끝 ===

다음 JSON 구조로 변환해주세요:

{{
  "personal_info": {{
    "name": "이름 (텍스트에서 추출)",
    "email": "이메일 (있다면)",
    "phone": "전화번호 (있다면)",
    "location": "거주지역 (있다면)"
  }},
  "education": [
    {{
      "degree": "학위",
      "major": "전공",
      "university": "학교명",
      "graduation_year": "졸업년도",
      "gpa": "학점 (있다면)",
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
      "department": "부서명 (있다면)",
      "responsibilities": ["주요 업무들"],
      "achievements": [
        {{
          "description": "성과 설명",
          "metrics": "정량적 지표",
          "impact": "임팩트/결과"
        }}
      ],
      "technologies": ["사용 기술들"],
      "team_size": "팀 규모 (추정 가능하다면)"
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
      "description": "프로젝트 설명",
      "role": "본인 역할",
      "technologies": ["사용 기술들"],
      "achievements": "주요 성과",
      "github_url": "GitHub URL (있다면)",
      "demo_url": "데모 URL (있다면)"
    }}
  ],
  "skills": {{
    "programming_languages": ["프로그래밍 언어들"],
    "frameworks": ["프레임워크들"],
    "databases": ["데이터베이스들"],
    "tools": ["개발 도구들"],
    "cloud_platforms": ["클라우드 플랫폼들"]
  }},
  "certifications": [
    {{
      "name": "자격증명",
      "issuer": "발급기관",
      "date": "취득일",
      "expiry": "만료일 (있다면)"
    }}
  ],
  "awards": [
    {{
      "name": "수상명",
      "issuer": "수여기관",
      "date": "수상일",
      "description": "수상 내용"
    }}
  ],
  "interests": ["관심사들"],
  "career_goals": {{
    "short_term": "단기 목표 (추론 가능하다면)",
    "long_term": "장기 목표 (추론 가능하다면)"
  }},
  "portfolio_links": {{
    "github": "GitHub URL (있다면)",
    "blog": "블로그 URL (있다면)",
    "linkedin": "LinkedIn URL (있다면)",
    "portfolio": "포트폴리오 URL (있다면)"
  }}
}}

중요한 지침:
1. 텍스트에 명시되지 않은 정보는 빈 문자열 "" 또는 빈 배열 []로 설정
2. 날짜는 가능한 한 YYYY-MM 형식으로 변환
3. 기술 스택은 카테고리별로 분류
4. 성과는 가능한 한 정량적 지표와 함께 구조화
5. 추론이 필요한 부분은 합리적으로 추정하되, 확실하지 않으면 비워두기
6. 반드시 유효한 JSON 형식으로 응답
7. JSON 외의 다른 텍스트는 포함하지 말 것

JSON으로만 응답해주세요:
"""
    
    async def convert_resume_to_profile(self, resume_text: str) -> Dict[str, Any]:
        """이력서 텍스트를 프로필 JSON으로 변환합니다."""
        print("🤖 AI가 이력서를 분석하고 있습니다...")
        
        # 프롬프트 생성
        prompt = self.create_conversion_prompt(resume_text)
        
        # AI 호출
        messages = [
            SystemMessage(content="당신은 이력서 분석 전문가입니다. 주어진 이력서 텍스트를 정확하게 분석하여 구조화된 JSON 프로필로 변환합니다."),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            json_text = response.content.strip()
            
            # JSON 파싱 시도
            try:
                profile = json.loads(json_text)
                
                # 메타데이터 추가
                profile["created_at"] = datetime.now().isoformat()
                profile["updated_at"] = datetime.now().isoformat()
                profile["version"] = "1.0"
                profile["conversion_method"] = "AI_automated"
                
                return profile
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 오류: {e}")
                print(f"AI 응답: {json_text[:200]}...")
                
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
            # 기본 템플릿 반환
            print("⚠️  자동 변환 실패. 기본 템플릿을 사용합니다.")
            return self._create_empty_template()
    
    def _create_empty_template(self) -> Dict[str, Any]:
        """빈 템플릿을 생성합니다."""
        return {
            "personal_info": {"name": "", "email": "", "phone": "", "location": ""},
            "education": [],
            "work_experience": [],
            "projects": [],
            "skills": {},
            "certifications": [],
            "awards": [],
            "interests": [],
            "career_goals": {},
            "portfolio_links": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0",
            "conversion_method": "template_fallback"
        }
    
    def save_profile(self, profile: Dict[str, Any], filename: str) -> str:
        """프로필을 JSON 파일로 저장합니다."""
        os.makedirs("profiles", exist_ok=True)
        filepath = f"profiles/{filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def print_conversion_summary(self, profile: Dict[str, Any]):
        """변환 결과 요약을 출력합니다."""
        print("\n📊 변환 결과 요약:")
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

async def main():
    """메인 함수"""
    print("🤖 AI 기반 이력서 자동 변환 도구")
    print("="*50)
    
    # 변환기 초기화
    try:
        converter = AIResumeConverter()
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
        default_name = default_name.replace(' ', '_') if default_name else 'converted_profile'
        
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
        
    except Exception as e:
        print(f"❌ 변환 실패: {e}")
        print("💡 수동 변환 도구를 사용해보세요: python convert_resume.py")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 
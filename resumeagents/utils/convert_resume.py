#!/usr/bin/env python3
"""
대화형 이력서 변환 도구 - ResumeAgents 통합 버전

ResumeAgents의 ProfileManager를 활용하여 체계적인 프로필을 대화형으로 생성합니다.
DEVELOPMENT_STRATEGY.md의 아키텍처를 준수하며 기존 시스템과 완전 통합됩니다.

사용 방법:
1. python -m resumeagents.utils.convert_resume 실행
2. 기존 이력서 참조 (선택사항)
3. 단계별 질문에 답하며 상세한 프로필 생성
4. ResumeAgents에서 바로 사용 가능한 JSON 프로필 생성
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

def read_existing_resume(file_path: str) -> str:
    """기존 이력서 파일을 읽어옵니다."""
    try:
        # 다중 인코딩 지원
        encodings = ['utf-8', 'cp949', 'latin-1', 'euc-kr']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ 파일 읽기 성공 (인코딩: {encoding})")
                return content
            except UnicodeDecodeError:
                continue
        
        raise ValueError("지원되는 인코딩으로 파일을 읽을 수 없습니다.")
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return ""
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        return ""

def create_interactive_profile() -> Dict[str, Any]:
    """대화형으로 ResumeAgents 호환 프로필을 생성합니다."""
    
    # ProfileManager를 사용하여 기본 템플릿 생성
    try:
        from .profile_manager import ProfileManager
        pm = ProfileManager()
        profile = pm.create_profile_template()
        
        # 빈 값으로 초기화
        profile = {
            "personal_info": {},
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
            "version": "2.0",
            "conversion_method": "manual_interactive"
        }
        
    except ImportError:
        # ProfileManager를 사용할 수 없는 경우 기본 구조
        profile = {
            "personal_info": {},
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
            "version": "2.0",
            "conversion_method": "manual_interactive"
        }
    
    print("=== ResumeAgents 프로필 생성 도구 ===")
    print("📋 DEVELOPMENT_STRATEGY.md 기반 구조화된 프로필을 생성합니다.")
    print()
    
    # 1. 개인정보
    print("👤 1. 개인정보 입력")
    profile["personal_info"] = {
        "name": input("이름 (필수): "),
        "email": input("이메일: "),
        "phone": input("전화번호: "),
        "location": input("거주지역: ")
    }
    
    # 2. 학력
    print("\n🎓 2. 학력 정보")
    while True:
        if input("학력을 추가하시겠습니까? (y/n): ").lower() != 'y':
            break
        
        education = {
            "degree": input("학위 (학사/석사/박사): "),
            "major": input("전공: "),
            "university": input("학교명: "),
            "graduation_year": input("졸업년도 (YYYY): "),
            "gpa": input("학점 (선택사항): "),
            "relevant_courses": [],
            "honors": []
        }
        
        # 관련 과목
        if input("관련 과목을 입력하시겠습니까? (y/n): ").lower() == 'y':
            courses_input = input("관련 과목 (쉼표로 구분): ")
            education["relevant_courses"] = [course.strip() for course in courses_input.split(",") if course.strip()]
        
        # 수상내역
        if input("학업 관련 수상내역을 입력하시겠습니까? (y/n): ").lower() == 'y':
            honors_input = input("수상내역 (쉼표로 구분): ")
            education["honors"] = [honor.strip() for honor in honors_input.split(",") if honor.strip()]
        
        profile["education"].append(education)
    
    # 3. 경력
    print("\n💼 3. 경력 정보")
    while True:
        if input("경력을 추가하시겠습니까? (y/n): ").lower() != 'y':
            break
        
        print("\n회사 정보:")
        company = input("회사명: ")
        position = input("직책: ")
        start_date = input("시작일 (YYYY-MM): ")
        end_date = input("종료일 (YYYY-MM, 현재 재직중이면 'current'): ")
        department = input("부서명: ")
        
        print("\n주요 업무:")
        responsibilities = []
        while True:
            resp = input(f"업무 {len(responsibilities)+1} (완료하려면 엔터): ")
            if not resp:
                break
            responsibilities.append(resp)
        
        print("\n주요 성과 (ResumeAgents 형식):")
        print("💡 성과는 '설명 + 정량적 지표 + 비즈니스 임팩트'로 구조화됩니다.")
        achievements = []
        while True:
            if input(f"성과 {len(achievements)+1}을 추가하시겠습니까? (y/n): ").lower() != 'y':
                break
            
            print(f"성과 {len(achievements)+1} 정보:")
            achievement = {
                "description": input("  성과 설명: "),
                "metrics": input("  정량적 지표 (예: 매출 20% 증가, 처리시간 30% 단축): "),
                "impact": input("  비즈니스 임팩트 (예: 고객 만족도 향상, 비용 절감): ")
            }
            achievements.append(achievement)
        
        technologies_input = input("\n사용 기술 (쉼표로 구분): ")
        technologies = [tech.strip() for tech in technologies_input.split(",") if tech.strip()]
        
        team_size = input("팀 규모 (예: 5명): ")
        
        key_projects_input = input("핵심 프로젝트 (쉼표로 구분): ")
        key_projects = [project.strip() for project in key_projects_input.split(",") if project.strip()]
        
        experience = {
            "company": company,
            "position": position,
            "duration": {"start": start_date, "end": end_date},
            "department": department,
            "responsibilities": responsibilities,
            "achievements": achievements,
            "technologies": technologies,
            "team_size": team_size,
            "key_projects": key_projects
        }
        profile["work_experience"].append(experience)
    
    # 4. 프로젝트
    print("\n🚀 4. 프로젝트 정보")
    while True:
        if input("프로젝트를 추가하시겠습니까? (y/n): ").lower() != 'y':
            break
        
        project = {
            "name": input("프로젝트명: "),
            "type": input("프로젝트 유형 (개인/팀/회사): "),
            "duration": {
                "start": input("시작일 (YYYY-MM): "),
                "end": input("종료일 (YYYY-MM): ")
            },
            "description": input("프로젝트 상세 설명: "),
            "role": input("본인 역할과 책임: "),
            "technologies": [tech.strip() for tech in input("사용 기술 스택 (쉼표로 구분): ").split(",") if tech.strip()],
            "achievements": input("구체적 성과와 결과: "),
            "github_url": input("GitHub 저장소 URL (선택사항): "),
            "demo_url": input("데모/배포 URL (선택사항): "),
            "team_size": input("팀 규모 (선택사항): ")
        }
        profile["projects"].append(project)
    
    # 5. 기술 스택 (ResumeAgents 분류 방식)
    print("\n💻 5. 기술 스택 (카테고리별 분류)")
    print("💡 ResumeAgents는 기술을 5개 카테고리로 분류합니다.")
    
    skills_categories = {
        "programming_languages": "프로그래밍 언어 (Python, Java, JavaScript 등)",
        "frameworks": "프레임워크/라이브러리 (React, Django, Spring 등)",
        "databases": "데이터베이스 (MySQL, PostgreSQL, MongoDB 등)",
        "tools": "개발/협업 도구 (Git, Docker, Jira 등)",
        "cloud_platforms": "클라우드 서비스 (AWS, GCP, Azure 등)"
    }
    
    profile["skills"] = {}
    
    for category, description in skills_categories.items():
        skills_input = input(f"{description}\n입력 (쉼표로 구분, 스킵하려면 엔터): ")
        if skills_input:
            profile["skills"][category] = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
        else:
            profile["skills"][category] = []
    
    # 6. 자격증
    print("\n🏆 6. 자격증 정보")
    while True:
        if input("자격증을 추가하시겠습니까? (y/n): ").lower() != 'y':
            break
        
        certification = {
            "name": input("자격증명: "),
            "issuer": input("발급기관: "),
            "date": input("취득일 (YYYY-MM): "),
            "expiry": input("만료일 (YYYY-MM, 없으면 엔터): "),
            "score": input("점수 (있다면): ")
        }
        profile["certifications"].append(certification)
    
    # 7. 수상내역
    print("\n🥇 7. 수상내역")
    while True:
        if input("수상내역을 추가하시겠습니까? (y/n): ").lower() != 'y':
            break
        
        award = {
            "name": input("수상명: "),
            "issuer": input("수여기관: "),
            "date": input("수상일 (YYYY-MM): "),
            "description": input("수상 내용과 의미: ")
        }
        profile["awards"].append(award)
    
    # 8. 관심사 & 목표
    print("\n🎯 8. 관심사 & 커리어 목표")
    
    if input("관심사를 입력하시겠습니까? (y/n): ").lower() == 'y':
        interests_input = input("관심 분야 (쉼표로 구분): ")
        profile["interests"] = [interest.strip() for interest in interests_input.split(",") if interest.strip()]
    
    if input("커리어 목표를 입력하시겠습니까? (y/n): ").lower() == 'y':
        profile["career_goals"] = {
            "short_term": input("단기 목표 (1-2년): "),
            "long_term": input("장기 목표 (3-5년): "),
            "target_companies": [company.strip() for company in input("관심 회사 (쉼표로 구분): ").split(",") if company.strip()],
            "preferred_roles": [role.strip() for role in input("희망 직무 (쉼표로 구분): ").split(",") if role.strip()]
        }
    
    # 9. 포트폴리오 링크
    print("\n🔗 9. 포트폴리오 링크")
    if input("포트폴리오 링크를 입력하시겠습니까? (y/n): ").lower() == 'y':
        profile["portfolio_links"] = {
            "github": input("GitHub 프로필 URL: "),
            "blog": input("기술 블로그 URL: "),
            "linkedin": input("LinkedIn 프로필 URL: "),
            "portfolio": input("포트폴리오 사이트 URL: ")
        }
    
    # 벡터DB 동기화 플래그 추가
    profile["vectordb_synced"] = False
    
    return profile

def save_profile(profile: Dict[str, Any], filename: str) -> str:
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

def print_profile_summary(profile: Dict[str, Any]):
    """생성된 프로필 요약을 출력합니다."""
    print("\n📊 생성된 프로필 요약:")
    print(f"👤 이름: {profile.get('personal_info', {}).get('name', '미입력')}")
    print(f"🎓 학력: {len(profile.get('education', []))}개")
    print(f"💼 경력: {len(profile.get('work_experience', []))}개")
    print(f"🚀 프로젝트: {len(profile.get('projects', []))}개")
    print(f"🏆 자격증: {len(profile.get('certifications', []))}개")
    print(f"🥇 수상: {len(profile.get('awards', []))}개")
    
    # 기술 스택 요약
    skills = profile.get('skills', {})
    total_skills = sum(len(v) for v in skills.values() if isinstance(v, list))
    print(f"💻 기술 스택: {total_skills}개")
    
    # 생성 방식
    conversion_method = profile.get('conversion_method', 'unknown')
    print(f"🔧 생성 방식: {conversion_method}")

def main():
    print("🚀 ResumeAgents 대화형 프로필 생성기")
    print("="*50)
    print("📋 DEVELOPMENT_STRATEGY.md 기반 구조화된 프로필 생성")
    print("💡 단계별 질문을 통해 상세하고 정확한 프로필을 만듭니다.")
    print()
    
    # 기존 이력서 파일 확인
    existing_file = input("기존 이력서 파일이 있다면 경로를 입력하세요 (없으면 엔터): ")
    if existing_file and os.path.exists(existing_file):
        content = read_existing_resume(existing_file)
        if content:
            print(f"\n📄 기존 이력서 내용을 참고하세요:")
            print("="*40)
            print(content[:600] + "..." if len(content) > 600 else content)
            print("="*40)
            input("\n위 내용을 참고하여 아래 질문에 답해주세요. (엔터를 눌러 계속)")
    
    # 대화형 프로필 생성
    print("\n🎯 프로필 생성을 시작합니다...")
    profile = create_interactive_profile()
    
    # 프로필 요약 출력
    print_profile_summary(profile)
    
    # 파일명 입력
    default_name = profile.get('personal_info', {}).get('name', 'my_profile')
    default_name = default_name.replace(' ', '_').replace('/', '_') if default_name else 'my_profile'
    
    profile_name = input(f"\n💾 프로필 파일명을 입력하세요 (기본값: {default_name}): ").strip() or default_name
    
    # 저장
    try:
        filepath = save_profile(profile, profile_name)
        
        print(f"\n✅ 프로필 생성 완료!")
        print(f"📁 저장 위치: {filepath}")
        print(f"📄 파일 크기: {os.path.getsize(filepath)} bytes")
        
        print(f"\n🎯 다음 단계:")
        print(f"1. 생성된 JSON 파일을 확인하고 필요시 수정")
        print(f"2. ResumeAgents 실행: python main.py")
        print(f"3. 옵션 2 선택: 기존 프로필 사용")
        print(f"4. 프로필 선택: {profile_name}")
        print(f"5. 원하는 연구 깊이 선택 (LOW/MEDIUM/HIGH)")
        
    except Exception as e:
        print(f"❌ 프로필 저장 실패: {e}")
        print("💡 권한을 확인하거나 다른 경로를 시도해보세요.")

if __name__ == "__main__":
    main() 
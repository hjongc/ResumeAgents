#!/usr/bin/env python3
"""
기존 이력서/포트폴리오를 ResumeAgents 프로필 형식으로 변환하는 도구

사용 방법:
1. 텍스트 파일로 기존 이력서 내용 저장
2. 이 스크립트 실행하여 대화형으로 JSON 프로필 생성
3. 생성된 JSON 파일을 ResumeAgents에서 사용
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List

def read_existing_resume(file_path: str) -> str:
    """기존 이력서 파일을 읽어옵니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return ""
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        return ""

def create_interactive_profile() -> Dict[str, Any]:
    """대화형으로 프로필을 생성합니다."""
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
        "version": "1.0"
    }
    
    print("=== ResumeAgents 프로필 변환 도구 ===\n")
    
    # 1. 개인정보
    print("📋 1. 개인정보 입력")
    profile["personal_info"] = {
        "name": input("이름: "),
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
            "graduation_year": input("졸업년도: "),
            "gpa": input("학점 (선택사항): "),
            "relevant_courses": input("관련 과목 (쉼표로 구분): ").split(",") if input("관련 과목을 입력하시겠습니까? (y/n): ").lower() == 'y' else [],
            "honors": input("수상내역 (쉼표로 구분): ").split(",") if input("수상내역을 입력하시겠습니까? (y/n): ").lower() == 'y' else []
        }
        profile["education"].append(education)
    
    # 3. 경력
    print("\n💼 3. 경력 정보")
    while True:
        if input("경력을 추가하시겠습니까? (y/n): ").lower() != 'y':
            break
        
        print("회사 정보:")
        company = input("회사명: ")
        position = input("직책: ")
        start_date = input("시작일 (YYYY-MM): ")
        end_date = input("종료일 (YYYY-MM, 현재 재직중이면 'current'): ")
        department = input("부서명 (선택사항): ")
        
        print("\n주요 업무:")
        responsibilities = []
        while True:
            resp = input(f"업무 {len(responsibilities)+1} (완료하려면 엔터): ")
            if not resp:
                break
            responsibilities.append(resp)
        
        print("\n주요 성과:")
        achievements = []
        while True:
            if input(f"성과 {len(achievements)+1}을 추가하시겠습니까? (y/n): ").lower() != 'y':
                break
            achievement = {
                "description": input("성과 설명: "),
                "metrics": input("정량적 지표 (예: 매출 20% 증가): "),
                "impact": input("임팩트/결과: ")
            }
            achievements.append(achievement)
        
        technologies = input("사용 기술 (쉼표로 구분): ").split(",")
        team_size = input("팀 규모 (예: 5명): ")
        
        experience = {
            "company": company,
            "position": position,
            "duration": {"start": start_date, "end": end_date},
            "department": department,
            "responsibilities": responsibilities,
            "achievements": achievements,
            "technologies": [tech.strip() for tech in technologies],
            "team_size": team_size
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
            "description": input("프로젝트 설명: "),
            "role": input("본인 역할: "),
            "technologies": input("사용 기술 (쉼표로 구분): ").split(","),
            "achievements": input("주요 성과: "),
            "github_url": input("GitHub URL (선택사항): "),
            "demo_url": input("데모 URL (선택사항): ")
        }
        profile["projects"].append(project)
    
    # 5. 기술 스택
    print("\n💻 5. 기술 스택")
    skills_categories = ["programming_languages", "frameworks", "databases", "tools", "cloud_platforms"]
    profile["skills"] = {}
    
    for category in skills_categories:
        category_name = {
            "programming_languages": "프로그래밍 언어",
            "frameworks": "프레임워크",
            "databases": "데이터베이스",
            "tools": "개발 도구",
            "cloud_platforms": "클라우드 플랫폼"
        }[category]
        
        skills_input = input(f"{category_name} (쉼표로 구분, 스킵하려면 엔터): ")
        if skills_input:
            profile["skills"][category] = [skill.strip() for skill in skills_input.split(",")]
    
    # 6. 관심사 & 목표
    print("\n🎯 6. 관심사 & 목표")
    profile["interests"] = input("관심사 (쉼표로 구분): ").split(",") if input("관심사를 입력하시겠습니까? (y/n): ").lower() == 'y' else []
    
    if input("커리어 목표를 입력하시겠습니까? (y/n): ").lower() == 'y':
        profile["career_goals"] = {
            "short_term": input("단기 목표: "),
            "long_term": input("장기 목표: "),
            "target_companies": input("관심 회사 (쉼표로 구분): ").split(","),
            "preferred_roles": input("희망 직무 (쉼표로 구분): ").split(",")
        }
    
    # 7. 포트폴리오 링크
    print("\n🔗 7. 포트폴리오 링크")
    if input("포트폴리오 링크를 입력하시겠습니까? (y/n): ").lower() == 'y':
        profile["portfolio_links"] = {
            "github": input("GitHub URL: "),
            "blog": input("블로그 URL: "),
            "linkedin": input("LinkedIn URL: "),
            "portfolio": input("포트폴리오 사이트 URL: ")
        }
    
    return profile

def save_profile(profile: Dict[str, Any], filename: str):
    """프로필을 JSON 파일로 저장합니다."""
    os.makedirs("profiles", exist_ok=True)
    filepath = f"profiles/{filename}.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 프로필이 저장되었습니다!")
    print(f"📁 파일 위치: {filepath}")
    print(f"📄 파일 크기: {os.path.getsize(filepath)} bytes")

def main():
    print("🚀 ResumeAgents 프로필 변환 도구")
    print("="*50)
    
    # 기존 이력서 파일 확인
    existing_file = input("\n기존 이력서 파일이 있다면 경로를 입력하세요 (없으면 엔터): ")
    if existing_file and os.path.exists(existing_file):
        content = read_existing_resume(existing_file)
        print(f"\n📄 기존 이력서 내용을 참고하세요:")
        print("="*30)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("="*30)
        input("\n위 내용을 참고하여 아래 질문에 답해주세요. (엔터를 눌러 계속)")
    
    # 대화형 프로필 생성
    profile = create_interactive_profile()
    
    # 파일명 입력
    profile_name = input("\n💾 프로필 파일명을 입력하세요 (확장자 제외): ") or "my_profile"
    
    # 저장
    save_profile(profile, profile_name)
    
    print(f"\n🎯 다음 단계:")
    print(f"1. ResumeAgents 실행: python main.py")
    print(f"2. 옵션 2 선택: 기존 프로필 사용")
    print(f"3. 프로필 선택: {profile_name}")
    print(f"4. 지원할 회사와 직무 정보 입력")

if __name__ == "__main__":
    main() 
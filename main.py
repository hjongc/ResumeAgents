"""
ResumeAgents: Multi-Agents LLM Resume & Job Application Framework

사용 예시:
python main.py
"""

import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv

from resumeagents.graph.resume_graph import ResumeAgentsGraph
from resumeagents.default_config import DEFAULT_CONFIG
from resumeagents.utils.output_manager import OutputManager
from resumeagents.utils.profile_manager import ProfileManager


def create_example_data():
    """예시 데이터 생성"""
    return {
        "company_name": "삼성전자",
        "job_title": "소프트웨어 엔지니어",
        "job_description": """
삼성전자 소프트웨어 엔지니어를 모집합니다.

[주요업무]
- 모바일 애플리케이션 개발
- 시스템 소프트웨어 설계 및 구현
- 코드 리뷰 및 품질 관리
- 신기술 연구 및 적용

[자격요건]
- 컴퓨터공학 또는 관련 학과 졸업
- Java, Python, C++ 중 1개 이상 능숙
- 3년 이상 소프트웨어 개발 경험
- 팀워크 및 커뮤니케이션 능력

[우대사항]
- 모바일 앱 개발 경험
- 클라우드 서비스 경험
- 오픈소스 기여 경험
        """,
        "candidate_info": {
            "name": "김개발",
            "education": "서울대학교 컴퓨터공학과 졸업 (2020)",
            "experience": """
- ABC테크 (2020-2023): 주니어 개발자
  * Android 앱 개발 및 유지보수
  * RESTful API 연동 및 데이터베이스 설계
  * 사용자 10만명 규모 서비스 운영
  
- XYZ스타트업 (2019): 인턴
  * 웹 애플리케이션 프론트엔드 개발
  * React.js 기반 사용자 인터페이스 구현
            """,
            "skills": "Java, Kotlin, Python, JavaScript, React, Spring Boot, MySQL, Git",
            "projects": """
- 개인 프로젝트: AI 기반 추천 시스템 (2023)
  * Python, TensorFlow 활용
  * 머신러닝 모델 설계 및 구현
  * 추천 정확도 85% 달성
  
- 팀 프로젝트: 실시간 채팅 애플리케이션 (2022)
  * Node.js, Socket.io 활용
  * 실시간 메시징 기능 구현
  * 동시 접속자 1000명 처리 가능
            """,
            "custom_questions": [
                {
                    "question": "지원 동기와 입사 후 포부를 기술해 주십시오.",
                    "type": "auto",
                    "char_limit": 1000,
                    "char_limit_note": "공백 포함 1000자 이내"
                },
                {
                    "question": "본인의 핵심역량과 관련된 경험을 구체적으로 설명해 주십시오.",
                    "type": "auto", 
                    "char_limit": 1500,
                    "char_limit_note": "공백 포함 1500자 이내"
                },
                {
                    "question": "팀워크를 발휘한 경험과 그 과정에서 배운 점을 서술해 주십시오.",
                    "type": "auto",
                    "char_limit": 800,
                    "char_limit_note": "공백 포함 800자 이내"
                }
            ]
        }
    }


def create_custom_data():
    """사용자 정의 데이터 생성"""
    print("=== 사용자 정의 데이터 입력 ===")
    
    company_name = input("기업명을 입력하세요: ")
    job_title = input("직무를 입력하세요: ")
    
    print("\n채용공고 내용을 입력하세요 (입력 완료 후 Ctrl+D):")
    job_description_lines = []
    try:
        while True:
            line = input()
            job_description_lines.append(line)
    except EOFError:
        pass
    job_description = "\n".join(job_description_lines)
    
    # 지원자 정보 입력
    print("\n=== 지원자 정보 입력 ===")
    name = input("이름: ")
    education = input("학력: ")
    
    print("경력사항을 입력하세요 (입력 완료 후 Ctrl+D):")
    experience_lines = []
    try:
        while True:
            line = input()
            experience_lines.append(line)
    except EOFError:
        pass
    experience = "\n".join(experience_lines)
    
    skills = input("보유 기술/스킬: ")
    
    print("프로젝트 경험을 입력하세요 (입력 완료 후 Ctrl+D):")
    projects_lines = []
    try:
        while True:
            line = input()
            projects_lines.append(line)
    except EOFError:
        pass
    projects = "\n".join(projects_lines)
    
    # 자기소개서 문항 입력
    print("\n=== 자기소개서 문항 입력 ===")
    custom_questions = []
    question_count = int(input("문항 개수를 입력하세요: "))
    
    for i in range(question_count):
        print(f"\n📝 문항 {i+1}:")
        question = input("문항 내용: ")
        
        # 글자수 제한 입력
        print("💡 글자수 제한 안내: 한글 기준 (한글 1글자 = 영어 1글자 = 숫자 1글자 = 1자)")
        char_limit_input = input("글자수 제한 (없으면 Enter, 예: 1000): ").strip()
        char_limit = int(char_limit_input) if char_limit_input.isdigit() else None
        
        char_limit_note = ""
        if char_limit:
            print(f"📏 예시: '안녕하세요. 저는 김개발입니다.' = {len('안녕하세요. 저는 김개발입니다.')}자")
            char_limit_note = input(f"글자수 제한 설명 (기본: '공백 포함 {char_limit}자 이내'): ").strip()
            if not char_limit_note:
                char_limit_note = f"공백 포함 {char_limit}자 이내"
        
        question_data = {
            "question": question,
            "type": "auto"
        }
        
        if char_limit:
            question_data["char_limit"] = char_limit
            question_data["char_limit_note"] = char_limit_note
        
        custom_questions.append(question_data)
    
    return {
        "company_name": company_name,
        "job_title": job_title,
        "job_description": job_description,
        "candidate_info": {
            "name": name,
            "education": education,
            "experience": experience,
            "skills": skills,
            "projects": projects,
            "custom_questions": custom_questions
        }
    }


async def run_resume_agents(data: Dict[str, Any], config: Dict[str, Any] = None):
    """ResumeAgents를 실행합니다."""
    if config is None:
        config = DEFAULT_CONFIG.copy()
        config["debug"] = True
        config["document_type"] = "resume"
    
    # Initialize graph
    graph = ResumeAgentsGraph(debug=True, config=config)
    
    print(f"ResumeAgents 분석을 시작합니다...")
    print(f"기업: {data['company_name']}")
    print(f"직무: {data['job_title']}")
    print()
    
    # Run analysis
    try:
        final_state, decision = await graph.propagate(
            company_name=data["company_name"],
            job_title=data["job_title"],
            job_description=data["job_description"],
            candidate_info=data["candidate_info"]
        )
        
        print("\n" + "="*50)
        print("분석 완료!")
        print("="*50)
        
        # 디버깅: decision 객체 구조 확인
        print(f"Decision type: {type(decision)}")
        print(f"Decision content: {decision}")
        
        if hasattr(decision, 'quality_score'):
            print(f"품질 점수: {decision.quality_score:.1f}/100")
        elif isinstance(decision, dict) and 'quality_score' in decision:
            print(f"품질 점수: {decision['quality_score']:.1f}/100")
        else:
            print("품질 점수: 정보 없음")
        print()
        
        # 가이드 결과 출력
        if "question_guides" in final_state.analysis_results:
            print("=== 자기소개서 문항 가이드 ===")
            question_guides = final_state.analysis_results["question_guides"]["guides"]
            for i, guide_data in enumerate(question_guides):
                print(f"\n문항 {i+1}: {guide_data['question']['question']}")
                print("-" * 40)
                print(guide_data['guide'])
                print()
        
        if "experience_guides" in final_state.analysis_results:
            print("=== 경험 가이드 ===")
            experience_guides = final_state.analysis_results["experience_guides"]["guides"]
            for i, guide_data in enumerate(experience_guides):
                print(f"\n문항 {i+1} 경험 가이드:")
                print("-" * 40)
                print(guide_data['guide'])
                print()
        
        if "writing_guides" in final_state.analysis_results:
            print("=== 작성 가이드 ===")
            writing_guides = final_state.analysis_results["writing_guides"]["guides"]
            for i, guide_data in enumerate(writing_guides):
                print(f"\n문항 {i+1} 작성 가이드:")
                print("-" * 40)
                print(guide_data['guide'])
                print()
        
        if decision["final_document"]:
            print("작성된 서류:")
            print("-" * 30)
            print(decision["final_document"])
            print("-" * 30)
        
        # 결과 저장
        output_manager = OutputManager()
        output_dir = output_manager.save_all_results(
            company_name=data["company_name"],
            job_title=data["job_title"],
            final_state=final_state,
            decision=decision
        )
        
        return final_state, decision
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None


def main():
    """메인 함수"""
    # Load environment variables
    load_dotenv()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("다음 명령어로 API 키를 설정해주세요:")
        print("export OPENAI_API_KEY=your_api_key_here")
        return
    
    print("=== ResumeAgents ===")
    print("Multi-Agents LLM Resume & Job Application Framework")
    print("🚀 하이브리드 프로필 관리 시스템 (JSON + 벡터DB)")
    print()
    
    # 프로필 관리자 초기화
    profile_manager = ProfileManager()
    print()
    
    # 데이터 선택
    print("📋 데이터 입력 방법을 선택하세요:")
    print("1: 예시 데이터")
    print("2: 기존 프로필 사용")
    print("3: 새 구조화된 프로필 생성")
    print("4: 간단 입력 (기존 방식)")
    
    choice = input("선택 (1-4): ")
    
    if choice == "1":
        data = create_example_data()
        
    elif choice == "2":
        # 기존 프로필 목록 표시 (향상된 UI)
        profiles = profile_manager.list_profiles()
        if not profiles:
            print("❌ 저장된 프로필이 없습니다.")
            print("💡 새 프로필을 생성하려면 옵션 3을 선택하세요.")
            return
        
        print(f"\n📂 저장된 프로필 목록 ({len(profiles)}개):")
        print("-" * 60)
        
        for i, profile_name in enumerate(profiles):
            info = profile_manager.get_profile_info(profile_name)
            status_icon = "🚀" if info.get("vectordb_synced") else "📁"
            vectordb_status = "벡터DB 동기화됨" if info.get("vectordb_synced") else "기본 모드"
            
            print(f"{status_icon} {i+1}: {info.get('name', profile_name)}")
            print(f"     경력: {info.get('experience_count', 0)}개 | 프로젝트: {info.get('project_count', 0)}개")
            print(f"     상태: {vectordb_status} | 업데이트: {info.get('last_updated', '알 수 없음')[:10]}")
            print()
        
        try:
            profile_idx = int(input("프로필 번호 선택: ")) - 1
            if 0 <= profile_idx < len(profiles):
                selected_profile = profiles[profile_idx]
                print(f"\n🔄 프로필 '{selected_profile}' 로딩 중...")
                
                profile_data = profile_manager.load_profile(selected_profile)
                candidate_info = profile_manager.convert_to_agent_format(profile_data)
                
                # 기업 정보 입력
                print("\n📝 기업 및 지원 정보 입력:")
                company_name = input("기업명을 입력하세요: ")
                job_title = input("직무를 입력하세요: ")
                
                print("\n📄 채용공고 내용을 입력하세요 (입력 완료 후 Ctrl+D):")
                job_description_lines = []
                try:
                    while True:
                        line = input()
                        job_description_lines.append(line)
                except EOFError:
                    pass
                job_description = "\n".join(job_description_lines)
                
                # 자기소개서 문항 입력
                print("\n❓ 자기소개서 문항 입력:")
                custom_questions = []
                question_count = int(input("문항 개수를 입력하세요: "))
                
                for i in range(question_count):
                    print(f"\n📝 문항 {i+1}:")
                    question = input("문항 내용: ")
                    
                    # 글자수 제한 입력
                    print("💡 글자수 제한 안내: 한글 기준 (한글 1글자 = 영어 1글자 = 숫자 1글자 = 1자)")
                    char_limit_input = input("글자수 제한 (없으면 Enter, 예: 1000): ").strip()
                    char_limit = int(char_limit_input) if char_limit_input.isdigit() else None
                    
                    char_limit_note = ""
                    if char_limit:
                        print(f"📏 예시: '안녕하세요. 저는 김개발입니다.' = {len('안녕하세요. 저는 김개발입니다.')}자")
                        char_limit_note = input(f"글자수 제한 설명 (기본: '공백 포함 {char_limit}자 이내'): ").strip()
                        if not char_limit_note:
                            char_limit_note = f"공백 포함 {char_limit}자 이내"
                    
                    question_data = {
                        "question": question,
                        "type": "auto"
                    }
                    
                    if char_limit:
                        question_data["char_limit"] = char_limit
                        question_data["char_limit_note"] = char_limit_note
                    
                    custom_questions.append(question_data)
                
                candidate_info["custom_questions"] = custom_questions
                
                data = {
                    "company_name": company_name,
                    "job_title": job_title,
                    "job_description": job_description,
                    "candidate_info": candidate_info
                }
            else:
                print("❌ 잘못된 선택입니다.")
                return
        except (ValueError, IndexError):
            print("❌ 잘못된 입력입니다.")
            return
            
    elif choice == "3":
        # 새 구조화된 프로필 생성
        print("\n🆕 새 프로필 생성 시작...")
        profile_data = profile_manager.create_interactive_profile()
        
        profile_name = input("\n💾 프로필 이름을 입력하세요: ")
        
        print(f"\n🔄 프로필 저장 및 벡터DB 동기화 중...")
        profile_manager.save_profile(profile_name, profile_data)
        
        candidate_info = profile_manager.convert_to_agent_format(profile_data)
        
        # 나머지 정보 입력 (기업, 채용공고, 문항)
        print("\n📝 기업 및 지원 정보 입력:")
        company_name = input("기업명을 입력하세요: ")
        job_title = input("직무를 입력하세요: ")
        
        print("\n📄 채용공고 내용을 입력하세요 (입력 완료 후 Ctrl+D):")
        job_description_lines = []
        try:
            while True:
                line = input()
                job_description_lines.append(line)
        except EOFError:
            pass
        job_description = "\n".join(job_description_lines)
        
        # 자기소개서 문항 입력
        print("\n❓ 자기소개서 문항 입력:")
        custom_questions = []
        question_count = int(input("문항 개수를 입력하세요: "))
        
        for i in range(question_count):
            print(f"\n📝 문항 {i+1}:")
            question = input("문항 내용: ")
            
            # 글자수 제한 입력
            print("💡 글자수 제한 안내: 한글 기준 (한글 1글자 = 영어 1글자 = 숫자 1글자 = 1자)")
            char_limit_input = input("글자수 제한 (없으면 Enter, 예: 1000): ").strip()
            char_limit = int(char_limit_input) if char_limit_input.isdigit() else None
            
            char_limit_note = ""
            if char_limit:
                print(f"📏 예시: '안녕하세요. 저는 김개발입니다.' = {len('안녕하세요. 저는 김개발입니다.')}자")
                char_limit_note = input(f"글자수 제한 설명 (기본: '공백 포함 {char_limit}자 이내'): ").strip()
                if not char_limit_note:
                    char_limit_note = f"공백 포함 {char_limit}자 이내"
            
            question_data = {
                "question": question,
                "type": "auto"
            }
            
            if char_limit:
                question_data["char_limit"] = char_limit
                question_data["char_limit_note"] = char_limit_note
            
            custom_questions.append(question_data)
        
        candidate_info["custom_questions"] = custom_questions
        
        data = {
            "company_name": company_name,
            "job_title": job_title,
            "job_description": job_description,
            "candidate_info": candidate_info
        }
        
    elif choice == "4":
        data = create_custom_data()
    else:
        print("❌ 잘못된 선택입니다. 예시 데이터를 사용합니다.")
        data = create_example_data()
    
    # 설정 선택
    print("\n⚙️  시스템 설정:")
    document_type = input("문서 유형 (resume/cover_letter) [기본값: resume]: ").strip() or "resume"
    analysis_depth = input("분석 깊이 (low/medium/high) [기본값: medium]: ").strip() or "medium"
    
    config = DEFAULT_CONFIG.copy()
    config["debug"] = True
    config["document_type"] = document_type
    config["analysis_depth"] = analysis_depth
    config["web_search_enabled"] = True  # Web Search 활성화
    
    print(f"\n🎯 분석 시작:")
    print(f"   기업: {data['company_name']}")
    print(f"   직무: {data['job_title']}")
    print(f"   문서 유형: {document_type}")
    print(f"   분석 깊이: {analysis_depth}")
    print()
    
    # Run analysis
    asyncio.run(run_resume_agents(data, config))


if __name__ == "__main__":
    main() 
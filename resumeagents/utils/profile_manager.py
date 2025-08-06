"""
Profile Manager for managing candidate profiles systematically.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# 벡터DB는 선택적 import (라이브러리가 없어도 기본 기능 동작)
try:
    from .experience_vectordb import ExperienceVectorDB
    VECTORDB_AVAILABLE = True
except ImportError:
    VECTORDB_AVAILABLE = False


class ProfileManager:
    """Manager for candidate profiles and experiences."""
    
    def __init__(self, profiles_dir: str = "profiles", enable_vectordb: bool = True):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        
        # 벡터DB 초기화 (선택적)
        self.vectordb = None
        self.enable_vectordb = enable_vectordb and VECTORDB_AVAILABLE
        
        if self.enable_vectordb:
            try:
                self.vectordb = ExperienceVectorDB()
                print("✅ 벡터DB 초기화 완료 - 고급 경험 매칭 활성화")
            except Exception as e:
                print(f"⚠️  벡터DB 초기화 실패 - 기본 모드로 동작: {e}")
                self.enable_vectordb = False
        else:
            if not VECTORDB_AVAILABLE:
                print("ℹ️  벡터DB 라이브러리 없음 - 기본 모드로 동작")
    
    def create_profile_template(self) -> Dict[str, Any]:
        """Create a structured profile template."""
        return {
            "personal_info": {
                "name": "",
                "age": "",
                "email": "",
                "phone": "",
                "location": ""
            },
            "education": [
                {
                    "degree": "학사",
                    "major": "컴퓨터공학",
                    "university": "서울대학교",
                    "graduation_year": "2020",
                    "gpa": "3.8/4.5",
                    "relevant_courses": ["데이터구조", "알고리즘", "소프트웨어공학"],
                    "honors": ["졸업우등상", "학과우수상"]
                }
            ],
            "work_experience": [
                {
                    "company": "ABC테크",
                    "position": "주니어 개발자",
                    "duration": {
                        "start": "2021-03",
                        "end": "2023-12"
                    },
                    "department": "모바일개발팀",
                    "responsibilities": [
                        "Android 앱 개발 및 유지보수",
                        "RESTful API 연동",
                        "코드 리뷰 및 품질 관리"
                    ],
                    "achievements": [
                        {
                            "description": "사용자 10만명 달성",
                            "metrics": "MAU 100,000명",
                            "impact": "매출 30% 증가 기여"
                        },
                        {
                            "description": "앱 성능 최적화",
                            "metrics": "로딩 시간 50% 단축",
                            "impact": "사용자 만족도 4.2→4.7점 향상"
                        }
                    ],
                    "technologies": ["Java", "Kotlin", "Android", "Firebase"],
                    "team_size": "5명",
                    "key_projects": ["모바일 앱 리뉴얼", "결제 시스템 개발"]
                }
            ],
            "projects": [
                {
                    "name": "AI 기반 추천 시스템",
                    "type": "개인 프로젝트",
                    "duration": {
                        "start": "2023-01",
                        "end": "2023-06"
                    },
                    "description": "머신러닝을 활용한 상품 추천 시스템 개발",
                    "role": "Full-stack 개발자",
                    "technologies": ["Python", "TensorFlow", "Django", "PostgreSQL"],
                    "achievements": [
                        {
                            "description": "추천 정확도 향상",
                            "metrics": "정확도 85% 달성",
                            "impact": "클릭률 25% 증가"
                        }
                    ],
                    "github_url": "https://github.com/user/recommendation-system",
                    "demo_url": "https://demo.example.com",
                    "challenges": ["데이터 전처리", "모델 최적화", "실시간 추천"],
                    "learnings": ["머신러닝 파이프라인 구축", "대용량 데이터 처리"]
                }
            ],
            "skills": {
                "programming_languages": [
                    {"name": "Java", "proficiency": "고급", "years": 3},
                    {"name": "Python", "proficiency": "중급", "years": 2},
                    {"name": "JavaScript", "proficiency": "중급", "years": 1}
                ],
                "frameworks": [
                    {"name": "Spring Boot", "proficiency": "중급", "years": 2},
                    {"name": "React", "proficiency": "초급", "years": 1}
                ],
                "databases": [
                    {"name": "MySQL", "proficiency": "중급", "years": 2},
                    {"name": "PostgreSQL", "proficiency": "초급", "years": 1}
                ],
                "tools": [
                    {"name": "Git", "proficiency": "고급", "years": 3},
                    {"name": "Docker", "proficiency": "중급", "years": 1}
                ],
                "soft_skills": [
                    "팀워크", "커뮤니케이션", "문제해결", "리더십", "학습능력"
                ]
            },
            "certifications": [
                {
                    "name": "정보처리기사",
                    "issuer": "한국산업인력공단",
                    "date": "2020-08",
                    "validity": "평생"
                }
            ],
            "languages": [
                {
                    "language": "한국어",
                    "proficiency": "원어민"
                },
                {
                    "language": "영어",
                    "proficiency": "중급",
                    "test_score": "TOEIC 850"
                }
            ],
            "achievements": [
                {
                    "title": "사내 해커톤 1위",
                    "date": "2022-11",
                    "description": "AI 챗봇 서비스 개발로 1위 수상",
                    "recognition": "CEO 특별상"
                }
            ],
            "interests": [
                "머신러닝", "오픈소스 기여", "기술 블로그 작성", "스타트업"
            ],
            "career_goals": {
                "short_term": "풀스택 개발자로서 전문성 강화",
                "long_term": "AI/ML 분야 전문가로 성장",
                "target_companies": ["네이버", "카카오", "삼성전자"],
                "preferred_roles": ["시니어 개발자", "테크리드"]
            },
            "portfolio_links": {
                "github": "https://github.com/username",
                "blog": "https://blog.example.com",
                "linkedin": "https://linkedin.com/in/username"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0",
            "vectordb_synced": False  # 벡터DB 동기화 상태
        }
    
    def save_profile(self, profile_name: str, profile_data: Dict[str, Any], sync_to_vectordb: bool = True) -> Path:
        """Save profile to JSON file and optionally sync to vector database."""
        profile_data["updated_at"] = datetime.now().isoformat()
        
        # JSON 파일 저장
        profile_file = self.profiles_dir / f"{profile_name}.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 프로필 저장 완료: {profile_file}")
        
        # 벡터DB 동기화
        if sync_to_vectordb and self.enable_vectordb:
            self._sync_profile_to_vectordb(profile_name, profile_data)
        
        return profile_file
    
    def load_profile(self, profile_name: str, auto_sync_vectordb: bool = True) -> Dict[str, Any]:
        """Load profile from JSON file and ensure vector DB is synced."""
        profile_file = self.profiles_dir / f"{profile_name}.json"
        
        if not profile_file.exists():
            raise FileNotFoundError(f"프로필을 찾을 수 없습니다: {profile_file}")
        
        with open(profile_file, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
        
        # 벡터DB 동기화 확인 및 자동 동기화
        if auto_sync_vectordb and self.enable_vectordb:
            if not profile_data.get("vectordb_synced", False):
                print(f"🔄 프로필 '{profile_name}'을 벡터DB에 동기화 중...")
                self._sync_profile_to_vectordb(profile_name, profile_data)
                
                # 동기화 상태 업데이트
                profile_data["vectordb_synced"] = True
                self.save_profile(profile_name, profile_data, sync_to_vectordb=False)
        
        return profile_data
    
    def _sync_profile_to_vectordb(self, profile_name: str, profile_data: Dict[str, Any]) -> bool:
        """Sync profile experiences to vector database."""
        if not self.enable_vectordb:
            return False
        
        try:
            # 프로필 ID 생성 (중복 방지용)
            profile_id = f"profile_{profile_name}_{profile_data.get('updated_at', '')}"
            
            # 기존 동일 프로필 경험 제거 (업데이트 시)
            self._remove_profile_from_vectordb(profile_name)
            
            # 새로운 경험 추가
            experience_ids = []
            
            # 직장 경험 추가
            for i, exp in enumerate(profile_data.get("work_experience", [])):
                exp_with_metadata = {
                    **exp, 
                    "type": "work_experience",
                    "profile_name": profile_name,
                    "profile_id": profile_id,
                    "experience_index": i
                }
                exp_id = self.vectordb.add_experience(exp_with_metadata)
                experience_ids.append(exp_id)
            
            # 프로젝트 경험 추가
            for i, proj in enumerate(profile_data.get("projects", [])):
                proj_with_metadata = {
                    **proj, 
                    "type": "project",
                    "profile_name": profile_name,
                    "profile_id": profile_id,
                    "experience_index": i
                }
                exp_id = self.vectordb.add_experience(proj_with_metadata)
                experience_ids.append(exp_id)
            
            # 교육 경험 추가
            for i, edu in enumerate(profile_data.get("education", [])):
                edu_with_metadata = {
                    **edu, 
                    "type": "education",
                    "profile_name": profile_name,
                    "profile_id": profile_id,
                    "experience_index": i
                }
                exp_id = self.vectordb.add_experience(edu_with_metadata)
                experience_ids.append(exp_id)
            
            # 벡터DB 저장
            self.vectordb.save_db()
            
            print(f"🚀 벡터DB 동기화 완료: {len(experience_ids)}개 경험 추가")
            return True
            
        except Exception as e:
            print(f"❌ 벡터DB 동기화 실패: {e}")
            return False
    
    def _remove_profile_from_vectordb(self, profile_name: str):
        """Remove existing profile experiences from vector database."""
        if not self.enable_vectordb:
            return
        
        # 현재 FAISS는 개별 삭제를 지원하지 않으므로
        # 향후 업그레이드 시 구현 예정
        # 지금은 전체 재구축으로 처리
        pass
    
    def find_relevant_experiences_for_question(self, profile_name: str, question: str, question_type: str = "general", top_k: int = 3) -> List[Dict[str, Any]]:
        """Find relevant experiences for a specific question using vector search."""
        if not self.enable_vectordb:
            # 벡터DB가 없으면 기본 방식으로 폴백
            return self._fallback_experience_search(profile_name, question)
        
        try:
            # 프로필별 필터링을 위한 검색
            relevant_experiences = self.vectordb.find_experiences_for_question(
                question=question,
                question_type=question_type,
                top_k=top_k * 2  # 더 많이 검색해서 프로필별 필터링
            )
            
            # 해당 프로필의 경험만 필터링
            filtered_experiences = []
            for exp_data in relevant_experiences:
                if exp_data["experience"].get("profile_name") == profile_name:
                    filtered_experiences.append(exp_data)
                    if len(filtered_experiences) >= top_k:
                        break
            
            return filtered_experiences
            
        except Exception as e:
            print(f"⚠️  벡터 검색 실패, 기본 검색 사용: {e}")
            return self._fallback_experience_search(profile_name, question)
    
    def _fallback_experience_search(self, profile_name: str, question: str) -> List[Dict[str, Any]]:
        """Fallback experience search without vector database."""
        try:
            profile_data = self.load_profile(profile_name, auto_sync_vectordb=False)
            
            # 간단한 키워드 매칭
            question_lower = question.lower()
            relevant_experiences = []
            
            # 직장 경험 검색
            for exp in profile_data.get("work_experience", []):
                relevance = 0
                exp_text = f"{exp.get('company', '')} {exp.get('position', '')} {' '.join(exp.get('responsibilities', []))}".lower()
                
                # 간단한 키워드 매칭 점수
                for word in question_lower.split():
                    if word in exp_text:
                        relevance += 1
                
                if relevance > 0:
                    relevant_experiences.append({
                        "experience": {**exp, "type": "work_experience"},
                        "relevance_score": relevance / len(question_lower.split()),
                        "match_reason": f"키워드 매칭: {relevance}개 일치"
                    })
            
            # 프로젝트 경험 검색
            for proj in profile_data.get("projects", []):
                relevance = 0
                proj_text = f"{proj.get('name', '')} {proj.get('description', '')} {' '.join(proj.get('technologies', []))}".lower()
                
                for word in question_lower.split():
                    if word in proj_text:
                        relevance += 1
                
                if relevance > 0:
                    relevant_experiences.append({
                        "experience": {**proj, "type": "project"},
                        "relevance_score": relevance / len(question_lower.split()),
                        "match_reason": f"키워드 매칭: {relevance}개 일치"
                    })
            
            # 관련성 순으로 정렬
            relevant_experiences.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return relevant_experiences[:3]
            
        except Exception as e:
            print(f"❌ 기본 검색도 실패: {e}")
            return []
    
    def list_profiles(self) -> List[str]:
        """List all available profiles."""
        profiles = []
        for file in self.profiles_dir.glob("*.json"):
            profiles.append(file.stem)
        return profiles
    
    def get_profile_info(self, profile_name: str) -> Dict[str, Any]:
        """Get profile summary information."""
        try:
            profile_data = self.load_profile(profile_name, auto_sync_vectordb=False)
            
            return {
                "name": profile_data.get("personal_info", {}).get("name", profile_name),
                "experience_count": len(profile_data.get("work_experience", [])),
                "project_count": len(profile_data.get("projects", [])),
                "last_updated": profile_data.get("updated_at", "알 수 없음"),
                "vectordb_synced": profile_data.get("vectordb_synced", False),
                "has_vectordb": self.enable_vectordb
            }
        except Exception as e:
            return {
                "name": profile_name,
                "error": str(e),
                "vectordb_synced": False,
                "has_vectordb": self.enable_vectordb
            }
    
    def convert_to_agent_format(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert structured profile to agent-compatible format."""
        # 경력 정보 변환
        experience_text = ""
        for exp in profile_data.get("work_experience", []):
            experience_text += f"- {exp['company']} ({exp['duration']['start']}~{exp['duration']['end']}): {exp['position']}\n"
            for resp in exp.get('responsibilities', []):
                experience_text += f"  * {resp}\n"
            for ach in exp.get('achievements', []):
                experience_text += f"  * {ach['description']} ({ach['metrics']})\n"
            experience_text += "\n"
        
        # 프로젝트 정보 변환
        projects_text = ""
        for proj in profile_data.get("projects", []):
            projects_text += f"- {proj['name']} ({proj['type']})\n"
            projects_text += f"  * {proj['description']}\n"
            projects_text += f"  * 기술스택: {', '.join(proj['technologies'])}\n"
            for ach in proj.get('achievements', []):
                projects_text += f"  * {ach['description']} ({ach['metrics']})\n"
            projects_text += "\n"
        
        # 스킬 정보 변환
        skills_text = ""
        for category, skills in profile_data.get("skills", {}).items():
            if category == "soft_skills":
                skills_text += f"{category}: {', '.join(skills)}\n"
            else:
                skill_names = [skill['name'] for skill in skills] if isinstance(skills, list) else skills
                skills_text += f"{category}: {', '.join(skill_names)}\n"
        
        return {
            "name": profile_data.get("personal_info", {}).get("name", ""),
            "education": self._format_education(profile_data.get("education", [])),
            "experience": experience_text.strip(),
            "skills": skills_text.strip(),
            "projects": projects_text.strip(),
            "achievements": self._format_achievements(profile_data.get("achievements", [])),
            "certifications": self._format_certifications(profile_data.get("certifications", [])),
            "portfolio_links": profile_data.get("portfolio_links", {}),
            "career_goals": profile_data.get("career_goals", {}),
            "structured_data": profile_data  # 원본 구조화된 데이터도 포함
        }
    
    def _format_education(self, education_list: List[Dict]) -> str:
        """Format education information."""
        education_text = ""
        for edu in education_list:
            education_text += f"{edu['university']} {edu['major']} {edu['degree']} ({edu['graduation_year']})\n"
        return education_text.strip()
    
    def _format_achievements(self, achievements_list: List[Dict]) -> str:
        """Format achievements information."""
        achievements_text = ""
        for ach in achievements_list:
            achievements_text += f"- {ach['title']} ({ach['date']}): {ach['description']}\n"
        return achievements_text.strip()
    
    def _format_certifications(self, certifications_list: List[Dict]) -> str:
        """Format certifications information."""
        cert_text = ""
        for cert in certifications_list:
            cert_text += f"- {cert['name']} ({cert['issuer']}, {cert['date']})\n"
        return cert_text.strip()
    
    def create_interactive_profile(self) -> Dict[str, Any]:
        """Create profile through interactive input."""
        print("=== 구조화된 프로필 생성 ===")
        
        profile = self.create_profile_template()
        
        # 기본 정보 입력
        print("\n1. 기본 정보")
        profile["personal_info"]["name"] = input("이름: ")
        profile["personal_info"]["age"] = input("나이: ")
        
        # 경력 정보 입력 (간단화)
        print("\n2. 주요 경력 (최대 3개)")
        experiences = []
        for i in range(3):
            print(f"\n경력 {i+1} (없으면 Enter):")
            company = input("회사명: ")
            if not company:
                break
            
            position = input("직책: ")
            start_date = input("시작일 (YYYY-MM): ")
            end_date = input("종료일 (YYYY-MM, 현재 재직중이면 'current'): ")
            
            responsibilities = []
            print("주요 업무 (최대 3개, 없으면 Enter):")
            for j in range(3):
                resp = input(f"업무 {j+1}: ")
                if resp:
                    responsibilities.append(resp)
            
            experiences.append({
                "company": company,
                "position": position,
                "duration": {"start": start_date, "end": end_date},
                "responsibilities": responsibilities,
                "achievements": [],
                "technologies": []
            })
        
        profile["work_experience"] = experiences
        
        # 스킬 입력 (간단화)
        print("\n3. 주요 스킬")
        skills_input = input("주요 기술 스킬 (쉼표로 구분): ")
        if skills_input:
            skills = [{"name": skill.strip(), "proficiency": "중급", "years": 1} 
                     for skill in skills_input.split(',')]
            profile["skills"]["programming_languages"] = skills
        
        return profile 
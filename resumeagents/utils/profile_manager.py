"""
Hybrid Profile Manager for ResumeAgents.
Supports both Light Mode (JSON only) and Advanced Mode (JSON + Vector DB).
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Optional vector DB imports
try:
    from .unified_vectordb import UnifiedVectorDB
    VECTORDB_AVAILABLE = True
except ImportError:
    VECTORDB_AVAILABLE = False


class ProfileManager:
    """
    Hybrid Profile Manager supporting Light and Advanced modes.
    
    Light Mode: JSON-only storage with keyword matching
    Advanced Mode: JSON + Vector DB with semantic search
    """
    
    def __init__(self, profiles_dir: str = "profiles", mode: str = "auto"):
        """
        Initialize ProfileManager with mode selection.
        
        Args:
            profiles_dir: Directory for storing profile JSON files
            mode: "light", "advanced", or "auto" (detect based on dependencies)
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Mode determination
        if mode == "auto":
            self.mode = "advanced" if VECTORDB_AVAILABLE else "light"
        elif mode == "advanced" and not VECTORDB_AVAILABLE:
            print("⚠️  Advanced mode requested but vector DB dependencies not available. Falling back to Light mode.")
            self.mode = "light"
        else:
            self.mode = mode
        
        # Initialize vector DB for advanced mode
        self.vectordb = None
        if self.mode == "advanced":
            try:
                self.vectordb = UnifiedVectorDB()
                print(f"✅ ProfileManager initialized in Advanced mode (JSON + Vector DB)")
            except Exception as e:
                print(f"⚠️  Vector DB initialization failed: {e}. Falling back to Light mode.")
                self.mode = "light"
                self.vectordb = None
        
        if self.mode == "light":
            print(f"✅ ProfileManager initialized in Light mode (JSON only)")
    
    def get_mode_info(self) -> Dict[str, Any]:
        """Get current mode information."""
        return {
            "mode": self.mode,
            "vectordb_available": VECTORDB_AVAILABLE,
            "vectordb_active": self.vectordb is not None,
            "storage": "JSON + Vector DB" if self.mode == "advanced" else "JSON only",
            "search": "Semantic similarity" if self.mode == "advanced" else "Keyword matching"
        }
    
    def create_profile_template(self) -> Dict[str, Any]:
        """Create a structured profile template with metadata."""
        return {
            "profile_metadata": {
                "name": "",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "vector_db_enabled": self.mode == "advanced",
                "last_vectordb_sync": None,
                "version": "2.1"
            },
            "personal_info": {
                "name": "",
                "email": "",
                "phone": "",
                "location": ""
            },
            "education": [
                {
                    "degree": "",
                    "major": "",
                    "university": "",
                    "graduation_year": "",
                    "gpa": "",
                    "relevant_courses": [],
                    "honors": []
                }
            ],
            "work_experience": [
                {
                    "company": "",
                    "position": "",
                    "duration": {
                        "start": "",
                        "end": ""
                    },
                    "department": "",
                    "responsibilities": [],
                    "achievements": [
                        {
                            "description": "",
                            "metrics": "",
                            "impact": ""
                        }
                    ],
                    "technologies": [],
                    "team_size": "",
                    "key_projects": []
                }
            ],
            "projects": [
                {
                    "name": "",
                    "type": "",
                    "duration": {
                        "start": "",
                        "end": ""
                    },
                    "description": "",
                    "role": "",
                    "technologies": [],
                    "achievements": "",
                    "github_url": "",
                    "demo_url": "",
                    "team_size": ""
                }
            ],
            "skills": {
                "programming_languages": [],
                "frameworks": [],
                "databases": [],
                "tools": [],
                "cloud_platforms": []
            },
            "certifications": [
                {
                    "name": "",
                    "issuer": "",
                    "date": "",
                    "expiry": "",
                    "score": ""
                }
            ],
            "awards": [
                {
                    "name": "",
                    "issuer": "",
                    "date": "",
                    "description": ""
                }
            ],
            "interests": [],
            "career_goals": {
                "short_term": "",
                "long_term": "",
                "target_companies": [],
                "preferred_roles": []
            },
            "portfolio_links": {
                "github": "",
                "blog": "",
                "linkedin": "",
                "portfolio": ""
            }
        }
    
    def save_profile(self, profile_data: Dict[str, Any], profile_name: str = None) -> str:
        """
        Save profile with automatic vector DB sync in advanced mode.
        
        Args:
            profile_data: Profile data dictionary
            profile_name: Optional profile name (extracted from data if not provided)
            
        Returns:
            Path to saved profile file
        """
        # Extract profile name
        if not profile_name:
            profile_name = profile_data.get("profile_metadata", {}).get("name") or \
                          profile_data.get("personal_info", {}).get("name", "unnamed_profile")
        
        # Update metadata
        if "profile_metadata" not in profile_data:
            profile_data["profile_metadata"] = {}
        
        profile_data["profile_metadata"].update({
            "name": profile_name,
            "updated_at": datetime.now().isoformat(),
            "vector_db_enabled": self.mode == "advanced"
        })
        
        # Save JSON file
        profile_path = self.profiles_dir / f"{profile_name}_profile.json"
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        # Sync to vector DB in advanced mode
        if self.mode == "advanced" and self.vectordb:
            try:
                self.vectordb.add_profile_to_vectordb(profile_data, profile_name)
                profile_data["profile_metadata"]["last_vectordb_sync"] = datetime.now().isoformat()
                
                # Re-save with updated sync timestamp
                with open(profile_path, 'w', encoding='utf-8') as f:
                    json.dump(profile_data, f, ensure_ascii=False, indent=2)
                    
                print(f"✅ Profile '{profile_name}' saved and synced to vector DB")
            except Exception as e:
                print(f"⚠️  Vector DB sync failed: {e}. Profile saved as JSON only.")
        else:
            print(f"✅ Profile '{profile_name}' saved in Light mode (JSON only)")
        
        return str(profile_path)
    
    def load_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Load profile from JSON file."""
        profile_path = self.profiles_dir / f"{profile_name}_profile.json"
        
        if not profile_path.exists():
            return None
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load profile '{profile_name}': {e}")
            return None
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all available profiles with metadata."""
        profiles = []
        
        for profile_file in self.profiles_dir.glob("*_profile.json"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                    
                metadata = profile_data.get("profile_metadata", {})
                profiles.append({
                    "name": metadata.get("name", profile_file.stem.replace("_profile", "")),
                    "file": str(profile_file),
                    "created_at": metadata.get("created_at", "Unknown"),
                    "updated_at": metadata.get("updated_at", "Unknown"),
                    "vector_db_enabled": metadata.get("vector_db_enabled", False),
                    "last_vectordb_sync": metadata.get("last_vectordb_sync")
                })
            except Exception as e:
                print(f"⚠️  Error reading profile {profile_file}: {e}")
        
        return sorted(profiles, key=lambda x: x["updated_at"], reverse=True)
    
    def find_relevant_experiences_for_question(self, profile_name: str, question: str, 
                                             question_type: str = "general", top_k: int = 3, 
                                             search_mode: str = "hybrid") -> List[Dict[str, Any]]:
        """
        Find relevant experiences using mode-appropriate search.
        
        Args:
            profile_name: Name of the profile
            question: Question text
            question_type: Type of question
            top_k: Number of results to return
            search_mode: "semantic", "keyword", "hybrid" (Advanced mode only)
            
        Returns:
            List of relevant experiences with relevance scores
        """
        if self.mode == "advanced" and self.vectordb:
            return self._find_experiences_advanced(profile_name, question, question_type, top_k, search_mode)
        else:
            return self._find_experiences_light(profile_name, question, question_type, top_k)
    
    def _find_experiences_advanced(self, profile_name: str, question: str, 
                                 question_type: str, top_k: int, search_mode: str = "hybrid") -> List[Dict[str, Any]]:
        """Advanced mode: Vector similarity search with data/AI optimized parameters."""
        try:
            # 데이터/AI 특화 질문 유형별 최소 점수 조정
            min_score_map = {
                # 기본 질문 유형
                "motivation": 0.12,        # 동기 관련은 낮은 임계값
                "experience": 0.15,        # 경험 관련은 중간 임계값
                "challenge": 0.13,         # 도전/문제해결은 중간 임계값
                "strength": 0.14,          # 강점은 중간 임계값
                "general": 0.15,           # 일반적인 질문
                
                # === 데이터/AI 특화 질문 유형 ===
                # 기술적 경험
                "data_analysis": 0.18,     # 데이터 분석 경험 (높은 정확도 요구)
                "machine_learning": 0.17,  # 머신러닝 경험
                "data_engineering": 0.16,  # 데이터 엔지니어링
                "statistics": 0.15,        # 통계 관련
                "programming": 0.16,       # 프로그래밍 경험
                "visualization": 0.14,     # 시각화 경험
                "database": 0.15,          # 데이터베이스 경험
                
                # 프로젝트/성과
                "ml_project": 0.17,        # ML 프로젝트
                "data_project": 0.16,      # 데이터 프로젝트
                "analytics_project": 0.15, # 분석 프로젝트
                "kaggle": 0.14,            # 캐글 경진대회 (창의적 접근 허용)
                "research": 0.16,          # 연구 경험
                
                # 도구/기술
                "python": 0.16,            # Python 경험
                "sql": 0.15,               # SQL 경험
                "spark": 0.17,             # Spark/빅데이터
                "cloud": 0.15,             # 클라우드 경험
                "mlops": 0.16,             # MLOps 경험
                
                # 비즈니스/도메인
                "business_analytics": 0.14, # 비즈니스 분석
                "ab_testing": 0.15,         # A/B 테스트
                "recommendation": 0.16,     # 추천시스템
                "forecasting": 0.15,        # 예측/예보
                "optimization": 0.15        # 최적화
            }
            
            min_score = min_score_map.get(question_type, 0.15)
            
            # 데이터/AI 키워드가 포함된 경우 임계값 조정
            data_ai_indicators = [
                "데이터", "분석", "머신러닝", "딥러닝", "AI", "모델", "예측", 
                "통계", "python", "sql", "pandas", "tensorflow", "spark"
            ]
            
            question_lower = question.lower()
            if any(indicator in question_lower for indicator in data_ai_indicators):
                min_score = max(min_score - 0.02, 0.10)  # 데이터/AI 관련 질문은 조금 더 관대하게
            
            # Use UnifiedVectorDB for direct semantic search with improved parameters
            search_results = self.vectordb.search_unified_profile(
                query=question,
                profile_name=profile_name,
                top_k=top_k,
                min_score=min_score,
                search_mode=search_mode  # 새로운 검색 모드 파라미터
            )
            
            # Convert to expected format with full data loading
            experiences = []
            for i, result in enumerate(search_results):
                # 완전한 데이터 로드 (메모리 최적화된 버전)
                entry_id = None
                for j, metadata in enumerate(self.vectordb.metadata):
                    if (metadata.get("profile_name") == result["metadata"].get("profile_name") and 
                        metadata.get("type") == result["metadata"].get("type") and
                        metadata.get("timestamp") == result["metadata"].get("timestamp")):
                        entry_id = j
                        break
                
                if entry_id is not None:
                    full_data = self.vectordb.get_entry_with_data(entry_id)
                    data = full_data.get("data", {})
                else:
                    data = {}  # 폴백
                
                experience_data = {
                    "type": result["metadata"].get("type", "unknown"),
                    "data": data,
                    "relevance_score": result["score"],
                    "search_method": result.get("search_method", "unknown"),
                    "text": result.get("text", "")[:100] + "...",  # 디버깅용
                    "question_type": question_type,  # 질문 유형 추가
                    "min_score_used": min_score     # 사용된 임계값 추가
                }
                
                # 하이브리드 검색 결과인 경우 추가 정보 포함
                if "semantic_score" in result:
                    experience_data.update({
                        "semantic_score": result.get("semantic_score", 0.0),
                        "keyword_score": result.get("keyword_score", 0.0),
                        "combined_score": result.get("combined_score", result["score"])
                    })
                elif "original_score" in result:
                    experience_data.update({
                        "original_score": result.get("original_score", result["score"]),
                        "type_weight": result.get("type_weight", 1.0)
                    })
                
                # 데이터/AI 특화 정보 추가
                if "keyword_bonus" in result:
                    experience_data["keyword_bonus"] = result["keyword_bonus"]
                
                experiences.append(experience_data)
            
            return experiences
            
        except Exception as e:
            print(f"⚠️  Advanced search failed: {e}. Falling back to light mode.")
            return self._find_experiences_light(profile_name, question, question_type, top_k)
    
    def _find_experiences_light(self, profile_name: str, question: str, 
                              question_type: str, top_k: int) -> List[Dict[str, Any]]:
        """Light mode: Keyword-based search."""
        profile_data = self.load_profile(profile_name)
        if not profile_data:
            return []
        
        # Extract keywords from question
        keywords = self._extract_keywords(question, question_type)
        
        experiences = []
        
        # Search work experiences
        for exp in profile_data.get("work_experience", []):
            score = self._calculate_keyword_score(exp, keywords)
            if score > 0:
                experiences.append({
                    "type": "work_experience",
                    "data": exp,
                    "relevance_score": score,
                    "search_method": "keyword_matching"
                })
        
        # Search projects
        for proj in profile_data.get("projects", []):
            score = self._calculate_keyword_score(proj, keywords)
            if score > 0:
                experiences.append({
                    "type": "project",
                    "data": proj,
                    "relevance_score": score,
                    "search_method": "keyword_matching"
                })
        
        # Sort by relevance score and return top_k
        experiences.sort(key=lambda x: x["relevance_score"], reverse=True)
        return experiences[:top_k]
    
    def _extract_keywords(self, question: str, question_type: str) -> List[str]:
        """Extract relevant keywords from question."""
        import re
        
        # Basic keyword extraction
        words = re.findall(r'\b[가-힣a-zA-Z]+\b', question.lower())
        
        # Filter out common words
        stop_words = {'이', '그', '저', '것', '수', '있', '하', '되', '될', '한', '일', '때', '중', '및', '등', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        # Add question type specific keywords
        type_keywords = {
            "motivation": ["동기", "이유", "지원"],
            "experience": ["경험", "프로젝트", "업무"],
            "challenge": ["어려움", "문제", "해결"],
            "strength": ["강점", "장점", "특기"]
        }
        
        if question_type in type_keywords:
            keywords.extend(type_keywords[question_type])
        
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_keyword_score(self, item_data: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate relevance score based on keyword matching."""
        if not keywords:
            return 0.0
        
        # Convert item data to searchable text
        searchable_text = ""
        
        # Add various fields to search text
        for field in ["company", "position", "name", "description", "role"]:
            if field in item_data and item_data[field]:
                searchable_text += f" {item_data[field]}"
        
        # Add list fields
        for field in ["responsibilities", "technologies", "achievements"]:
            if field in item_data and isinstance(item_data[field], list):
                for item in item_data[field]:
                    if isinstance(item, str):
                        searchable_text += f" {item}"
                    elif isinstance(item, dict):
                        searchable_text += f" {item.get('description', '')}"
        
        searchable_text = searchable_text.lower()
        
        # Calculate score
        score = 0.0
        for keyword in keywords:
            if keyword in searchable_text:
                # Higher score for exact matches
                count = searchable_text.count(keyword)
                score += count * 0.1
        
        # Normalize score
        return min(score, 1.0)
    
    def switch_mode(self, new_mode: str) -> bool:
        """
        Switch between light and advanced modes.
        
        Args:
            new_mode: "light" or "advanced"
            
        Returns:
            True if switch successful, False otherwise
        """
        if new_mode == self.mode:
            print(f"Already in {new_mode} mode")
            return True
        
        if new_mode == "advanced" and not VECTORDB_AVAILABLE:
            print("❌ Cannot switch to advanced mode: Vector DB dependencies not available")
            return False
        
        old_mode = self.mode
        self.mode = new_mode
        
        if new_mode == "advanced":
            try:
                self.vectordb = UnifiedVectorDB()
                print(f"✅ Switched from {old_mode} to {new_mode} mode")
                return True
            except Exception as e:
                print(f"❌ Failed to switch to advanced mode: {e}")
                self.mode = old_mode
                return False
        else:
            self.vectordb = None
            print(f"✅ Switched from {old_mode} to {new_mode} mode")
            return True
    
    def sync_all_profiles_to_vectordb(self) -> Dict[str, Any]:
        """Sync all profiles to vector DB (advanced mode only)."""
        if self.mode != "advanced" or not self.vectordb:
            return {"error": "Advanced mode not available"}
        
        profiles = self.list_profiles()
        results = {"synced": 0, "failed": 0, "errors": []}
        
        for profile_info in profiles:
            try:
                profile_name = profile_info["name"]
                profile_data = self.load_profile(profile_name)
                
                if profile_data:
                    self.vectordb.add_profile_to_vectordb(profile_data, profile_name)
                    
                    # Update sync timestamp
                    profile_data["profile_metadata"]["last_vectordb_sync"] = datetime.now().isoformat()
                    self.save_profile(profile_data, profile_name)
                    
                    results["synced"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Could not load profile: {profile_name}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Failed to sync {profile_info['name']}: {e}")
        
        print(f"✅ Sync complete: {results['synced']} synced, {results['failed']} failed")
        return results 
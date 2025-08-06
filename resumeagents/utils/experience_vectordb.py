"""
Experience Vector Database for semantic experience matching.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import faiss


class ExperienceVectorDB:
    """Vector database for semantic experience search and matching."""
    
    def __init__(self, db_path: str = "experience_db", model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # 다국어 지원 모델 로드
        self.encoder = SentenceTransformer(model_name)
        self.dimension = self.encoder.get_sentence_embedding_dimension()
        
        # FAISS 인덱스 초기화
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (cosine similarity)
        self.experiences = []  # 경험 데이터 저장
        self.experience_metadata = []  # 메타데이터 저장
        
        # 기존 DB 로드
        self._load_existing_db()
    
    def add_experience(self, experience: Dict[str, Any]) -> int:
        """Add experience to vector database."""
        # 경험을 텍스트로 변환
        experience_text = self._experience_to_text(experience)
        
        # 벡터화
        embedding = self.encoder.encode([experience_text])
        
        # FAISS 인덱스에 추가
        faiss.normalize_L2(embedding)  # L2 정규화
        self.index.add(embedding)
        
        # 메타데이터 저장
        experience_id = len(self.experiences)
        self.experiences.append(experience_text)
        self.experience_metadata.append(experience)
        
        return experience_id
    
    def add_profile_experiences(self, profile_data: Dict[str, Any]) -> List[int]:
        """Add all experiences from a profile."""
        experience_ids = []
        
        # 직장 경험 추가
        for exp in profile_data.get("work_experience", []):
            exp_with_type = {**exp, "type": "work_experience"}
            exp_id = self.add_experience(exp_with_type)
            experience_ids.append(exp_id)
        
        # 프로젝트 경험 추가
        for proj in profile_data.get("projects", []):
            proj_with_type = {**proj, "type": "project"}
            exp_id = self.add_experience(proj_with_type)
            experience_ids.append(exp_id)
        
        # 교육/자격증 경험 추가
        for edu in profile_data.get("education", []):
            edu_with_type = {**edu, "type": "education"}
            exp_id = self.add_experience(edu_with_type)
            experience_ids.append(exp_id)
        
        return experience_ids
    
    def search_relevant_experiences(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Search for relevant experiences based on query."""
        if self.index.ntotal == 0:
            return []
        
        # 쿼리 벡터화
        query_embedding = self.encoder.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # 검색
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:  # 유효한 인덱스인 경우
                results.append((self.experience_metadata[idx], float(score)))
        
        return results
    
    def find_experiences_for_question(self, question: str, question_type: str = "general", top_k: int = 3) -> List[Dict[str, Any]]:
        """Find most relevant experiences for a specific question."""
        # 질문 유형에 따른 검색 쿼리 확장
        expanded_query = self._expand_query_by_type(question, question_type)
        
        # 관련 경험 검색
        relevant_experiences = self.search_relevant_experiences(expanded_query, top_k)
        
        # 결과 포맷팅
        formatted_results = []
        for exp, score in relevant_experiences:
            formatted_results.append({
                "experience": exp,
                "relevance_score": score,
                "match_reason": f"Semantic similarity: {score:.3f}"
            })
        
        return formatted_results
    
    def _experience_to_text(self, experience: Dict[str, Any]) -> str:
        """Convert experience dict to searchable text."""
        text_parts = []
        
        exp_type = experience.get("type", "unknown")
        
        if exp_type == "work_experience":
            text_parts.append(f"직장 경험: {experience.get('company', '')} {experience.get('position', '')}")
            text_parts.extend(experience.get('responsibilities', []))
            
            for ach in experience.get('achievements', []):
                text_parts.append(f"성과: {ach.get('description', '')} {ach.get('metrics', '')}")
            
            text_parts.extend(experience.get('technologies', []))
            
        elif exp_type == "project":
            text_parts.append(f"프로젝트: {experience.get('name', '')} {experience.get('description', '')}")
            text_parts.extend(experience.get('technologies', []))
            text_parts.extend(experience.get('challenges', []))
            text_parts.extend(experience.get('learnings', []))
            
            for ach in experience.get('achievements', []):
                text_parts.append(f"성과: {ach.get('description', '')} {ach.get('metrics', '')}")
        
        elif exp_type == "education":
            text_parts.append(f"교육: {experience.get('university', '')} {experience.get('major', '')} {experience.get('degree', '')}")
            text_parts.extend(experience.get('relevant_courses', []))
            text_parts.extend(experience.get('honors', []))
        
        return " ".join(text_parts)
    
    def _expand_query_by_type(self, question: str, question_type: str) -> str:
        """Expand search query based on question type."""
        type_keywords = {
            "motivation": ["동기", "이유", "목표", "비전", "열정"],
            "experience": ["경험", "프로젝트", "업무", "성과", "역할"],
            "problem_solving": ["문제해결", "도전", "어려움", "극복", "개선"],
            "values": ["가치관", "원칙", "신념", "철학", "중요"],
            "skills": ["기술", "능력", "역량", "전문성", "스킬"],
            "leadership": ["리더십", "팀워크", "협업", "관리", "이끌기"],
            "growth": ["성장", "발전", "학습", "개발", "향상"]
        }
        
        keywords = type_keywords.get(question_type, [])
        expanded_query = question + " " + " ".join(keywords)
        
        return expanded_query
    
    def save_db(self):
        """Save vector database to disk."""
        # FAISS 인덱스 저장
        index_path = self.db_path / "faiss_index.bin"
        faiss.write_index(self.index, str(index_path))
        
        # 메타데이터 저장
        metadata_path = self.db_path / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "experiences": self.experiences,
                "experience_metadata": self.experience_metadata
            }, f, ensure_ascii=False, indent=2)
        
        print(f"Vector DB 저장 완료: {self.db_path}")
    
    def _load_existing_db(self):
        """Load existing vector database."""
        index_path = self.db_path / "faiss_index.bin"
        metadata_path = self.db_path / "metadata.json"
        
        if index_path.exists() and metadata_path.exists():
            try:
                # FAISS 인덱스 로드
                self.index = faiss.read_index(str(index_path))
                
                # 메타데이터 로드
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.experiences = data["experiences"]
                    self.experience_metadata = data["experience_metadata"]
                
                print(f"기존 Vector DB 로드 완료: {len(self.experiences)}개 경험")
            except Exception as e:
                print(f"DB 로드 실패, 새로 시작: {e}")
    
    def get_experience_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        type_counts = {}
        for exp in self.experience_metadata:
            exp_type = exp.get("type", "unknown")
            type_counts[exp_type] = type_counts.get(exp_type, 0) + 1
        
        return {
            "total_experiences": len(self.experiences),
            "experience_types": type_counts,
            "index_size": self.index.ntotal
        } 
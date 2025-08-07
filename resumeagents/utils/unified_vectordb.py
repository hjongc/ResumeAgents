"""
통합 벡터DB - JSON 프로필을 벡터DB에 통합

모든 사용자 정보(JSON 프로필 + 경험)를 하나의 벡터DB에 저장하여
에이전트들이 단일 소스에서 모든 정보를 검색할 수 있도록 합니다.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import faiss
import re
from collections import Counter
import math


class UnifiedVectorDB:
    """통합 벡터DB - JSON 프로필과 경험을 모두 벡터화하여 저장"""
    
    def __init__(self, db_path: str = "db", model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        # 다국어 지원 모델 로드
        self.encoder = SentenceTransformer(model_name)
        self.dimension = self.encoder.get_sentence_embedding_dimension()
        
        # FAISS 인덱스 초기화
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (cosine similarity)
        self.data_entries = []  # 모든 데이터 엔트리 저장
        self.metadata = []  # 메타데이터 저장
        
        # BM25를 위한 키워드 인덱스
        self.keyword_index = {}  # 단어 -> 문서 ID 리스트
        self.doc_frequencies = []  # 문서별 단어 빈도
        self.doc_lengths = []  # 문서별 길이
        self.avg_doc_length = 0
        
        # 쿼리 임베딩 캐시
        self.query_cache = {}
        
        # 기존 DB 로드
        self._load_existing_db()
    
    def add_profile_to_vectordb(self, profile_data: Dict[str, Any], profile_name: str) -> List[int]:
        """
        JSON 프로필을 벡터DB에 통합 저장
        
        Args:
            profile_data: JSON 프로필 데이터
            profile_name: 프로필 이름
        
        Returns:
            추가된 엔트리 ID 리스트
        """
        # 기존 프로필 엔트리 제거 (중복 방지)
        self._remove_profile_entries(profile_name)
        
        entry_ids = []
        
        # 1. 개인정보 추가
        personal_info = profile_data.get("personal_info", {})
        if personal_info:
            personal_text = self._personal_info_to_text(personal_info)
            entry_id = self._add_entry(personal_text, {
                "type": "personal_info",
                "profile_name": profile_name,
                "data": personal_info,
                "timestamp": datetime.now().isoformat()
            })
            entry_ids.append(entry_id)
        
        # 2. 학력 정보 추가
        for i, education in enumerate(profile_data.get("education", [])):
            education_text = self._education_to_text(education)
            entry_id = self._add_entry(education_text, {
                "type": "education",
                "profile_name": profile_name,
                "data": education,
                "index": i,
                "timestamp": datetime.now().isoformat()
            })
            entry_ids.append(entry_id)
        
        # 3. 경력 정보 추가
        for i, experience in enumerate(profile_data.get("work_experience", [])):
            experience_text = self._work_experience_to_text(experience)
            entry_id = self._add_entry(experience_text, {
                "type": "work_experience",
                "profile_name": profile_name,
                "data": experience,
                "index": i,
                "timestamp": datetime.now().isoformat()
            })
            entry_ids.append(entry_id)
        
        # 4. 프로젝트 정보 추가
        for i, project in enumerate(profile_data.get("projects", [])):
            project_text = self._project_to_text(project)
            entry_id = self._add_entry(project_text, {
                "type": "project",
                "profile_name": profile_name,
                "data": project,
                "index": i,
                "timestamp": datetime.now().isoformat()
            })
            entry_ids.append(entry_id)
        
        # 5. 기술 스택 추가
        skills = profile_data.get("skills", {})
        if skills:
            skills_text = self._skills_to_text(skills)
            entry_id = self._add_entry(skills_text, {
                "type": "skills",
                "profile_name": profile_name,
                "data": skills,
                "timestamp": datetime.now().isoformat()
            })
            entry_ids.append(entry_id)
        
        # 6. 자격증 추가
        for i, certification in enumerate(profile_data.get("certifications", [])):
            cert_text = self._certification_to_text(certification)
            entry_id = self._add_entry(cert_text, {
                "type": "certification",
                "profile_name": profile_name,
                "data": certification,
                "index": i,
                "timestamp": datetime.now().isoformat()
            })
            entry_ids.append(entry_id)
        
        # 7. 수상내역 추가
        for i, award in enumerate(profile_data.get("awards", [])):
            award_text = self._award_to_text(award)
            entry_id = self._add_entry(award_text, {
                "type": "award",
                "profile_name": profile_name,
                "data": award,
                "index": i,
                "timestamp": datetime.now().isoformat()
            })
            entry_ids.append(entry_id)
        
        # 8. 커리어 목표 추가
        career_goals = profile_data.get("career_goals", {})
        if career_goals:
            goals_text = self._career_goals_to_text(career_goals)
            entry_id = self._add_entry(goals_text, {
                "type": "career_goals",
                "profile_name": profile_name,
                "data": career_goals,
                "timestamp": datetime.now().isoformat()
            })
            entry_ids.append(entry_id)
        
        # 9. 관심사 추가
        interests = profile_data.get("interests", [])
        if interests:
            interests_text = self._interests_to_text(interests)
            entry_id = self._add_entry(interests_text, {
                "type": "interests",
                "profile_name": profile_name,
                "data": interests,
                "timestamp": datetime.now().isoformat()
            })
            entry_ids.append(entry_id)
        
        # 벡터DB 저장 (중요!)
        self.save_db()
        
        print(f"✅ 프로필 '{profile_name}' 통합 벡터DB에 추가 완료: {len(entry_ids)}개 엔트리")
        return entry_ids
    
    def search_unified_profile(self, query: str, profile_name: str = None, data_types: List[str] = None, 
                             top_k: int = 5, min_score: float = 0.1, search_mode: str = "hybrid") -> List[Dict[str, Any]]:
        """
        통합 벡터DB에서 하이브리드 검색 (의미적 + 키워드)
        
        Args:
            query: 검색 쿼리
            profile_name: 특정 프로필로 제한 (선택사항)
            data_types: 검색할 데이터 유형 리스트 (선택사항)
            top_k: 반환할 최대 결과 수
            min_score: 최소 관련도 점수 (기본값: 0.1)
            search_mode: "semantic", "keyword", "hybrid" (기본값: hybrid)
        
        Returns:
            검색 결과 리스트 (관련도 순 정렬)
        """
        if self.index.ntotal == 0:
            return []
        
        # 쿼리 확장 (동의어, 관련어 추가)
        expanded_query = self._expand_query(query)
        
        if search_mode == "hybrid":
            return self._hybrid_search(expanded_query, profile_name, data_types, top_k, min_score)
        elif search_mode == "semantic":
            return self._semantic_search(expanded_query, profile_name, data_types, top_k, min_score)
        elif search_mode == "keyword":
            return self._keyword_search(expanded_query, profile_name, data_types, top_k, min_score)
        else:
            return self._hybrid_search(expanded_query, profile_name, data_types, top_k, min_score)
    
    def _expand_query(self, query: str) -> str:
        """쿼리 확장 - 데이터/AI 특화 동의어, 관련어, 컨텍스트 기반 확장"""
        # 기술 분야 동의어 사전 (데이터/AI 특화 확장)
        synonyms = {
            # 기존 기술 동의어
            "백엔드": ["backend", "서버", "server", "API", "서버사이드"],
            "프론트엔드": ["frontend", "클라이언트", "client", "UI", "UX", "웹"],
            "파이썬": ["python", "django", "flask", "fastapi", "py"],
            "자바스크립트": ["javascript", "js", "node", "react", "vue", "angular"],
            "데이터베이스": ["database", "db", "mysql", "postgresql", "mongodb", "sql"],
            "클라우드": ["cloud", "aws", "azure", "gcp", "kubernetes", "docker"],
            "개발": ["development", "coding", "programming", "구현", "코딩"],
            "프로젝트": ["project", "작업", "업무", "개발", "시스템"],
            "경험": ["experience", "이력", "업무", "프로젝트", "참여"],
            "성능": ["performance", "최적화", "optimization", "속도", "튜닝"],
            "보안": ["security", "암호화", "인증", "authorization", "권한"],
            "최적화": ["optimization", "performance", "tuning", "개선", "향상"],
            "아키텍처": ["architecture", "설계", "design", "구조", "시스템"],
            
            # === 데이터/AI 특화 동의어 ===
            # 데이터 엔지니어링
            "데이터엔지니어": ["data engineer", "데이터엔지니어링", "data engineering", "ETL", "파이프라인"],
            "데이터파이프라인": ["data pipeline", "ETL", "ELT", "데이터플로우", "workflow", "airflow"],
            "ETL": ["extract transform load", "데이터파이프라인", "데이터처리", "배치처리"],
            "ELT": ["extract load transform", "데이터레이크", "클라우드데이터"],
            "스트리밍": ["streaming", "실시간", "real-time", "kafka", "kinesis", "spark streaming"],
            "배치처리": ["batch processing", "스케줄링", "cron", "airflow", "luigi"],
            
            # 데이터 사이언스
            "데이터사이언스": ["data science", "데이터분석", "통계분석", "예측모델링"],
            "데이터사이언티스트": ["data scientist", "분석가", "analyst", "연구원"],
            "데이터분석": ["data analysis", "analytics", "통계", "statistics", "시각화"],
            "통계": ["statistics", "통계학", "확률", "probability", "추론"],
            "예측모델링": ["predictive modeling", "forecasting", "예측", "모델링", "regression"],
            "분류": ["classification", "classifier", "supervised learning", "지도학습"],
            "회귀": ["regression", "linear regression", "예측", "연속값"],
            "클러스터링": ["clustering", "군집화", "unsupervised", "비지도학습"],
            
            # 머신러닝/AI
            "머신러닝": ["machine learning", "ML", "AI", "인공지능", "딥러닝", "모델", "학습"],
            "딥러닝": ["deep learning", "neural network", "신경망", "CNN", "RNN", "transformer"],
            "인공지능": ["artificial intelligence", "AI", "머신러닝", "딥러닝", "자동화"],
            "신경망": ["neural network", "딥러닝", "퍼셉트론", "레이어", "노드"],
            "자연어처리": ["NLP", "natural language processing", "텍스트분석", "언어모델"],
            "컴퓨터비전": ["computer vision", "CV", "이미지처리", "객체인식", "CNN"],
            "추천시스템": ["recommendation system", "collaborative filtering", "개인화", "추천엔진"],
            "강화학습": ["reinforcement learning", "RL", "에이전트", "보상", "정책"],
            
            # 빅데이터 기술
            "빅데이터": ["big data", "대용량데이터", "분산처리", "hadoop", "spark"],
            "하둡": ["hadoop", "HDFS", "mapreduce", "분산저장", "클러스터"],
            "스파크": ["spark", "apache spark", "분산처리", "인메모리", "실시간"],
            "카프카": ["kafka", "메시징", "스트리밍", "이벤트", "큐", "실시간"],
            "엘라스틱서치": ["elasticsearch", "검색엔진", "로그분석", "인덱싱", "kibana"],
            
            # 데이터베이스 특화
            "NoSQL": ["nosql", "mongodb", "cassandra", "redis", "비관계형"],
            "데이터웨어하우스": ["data warehouse", "DW", "OLAP", "dimensional modeling"],
            "데이터레이크": ["data lake", "S3", "저장소", "원시데이터", "스키마온리드"],
            "데이터마트": ["data mart", "부서별데이터", "요약데이터", "OLAP"],
            
            # 클라우드/MLOps
            "MLOps": ["mlops", "모델운영", "CI/CD", "모델배포", "모델관리"],
            "모델배포": ["model deployment", "serving", "추론", "production", "API"],
            "모델모니터링": ["model monitoring", "drift detection", "성능추적", "A/B테스트"],
            "피처엔지니어링": ["feature engineering", "변수생성", "전처리", "피처선택"],
            "하이퍼파라미터": ["hyperparameter", "튜닝", "최적화", "그리드서치"],
            
            # 시각화/BI
            "시각화": ["visualization", "차트", "그래프", "대시보드", "plotting"],
            "대시보드": ["dashboard", "BI", "business intelligence", "리포팅"],
            "BI": ["business intelligence", "대시보드", "리포팅", "분석도구"],
            "태블로": ["tableau", "시각화도구", "대시보드", "셀프서비스"],
            
            # 프로그래밍/도구
            "R": ["R언어", "통계분석", "데이터분석", "ggplot", "dplyr"],
            "SQL": ["데이터베이스", "쿼리", "조인", "집계", "분석"],
            "주피터": ["jupyter", "notebook", "ipython", "분석환경", "프로토타이핑"],
            "도커": ["docker", "컨테이너", "가상화", "배포", "환경관리"],
            "git": ["버전관리", "협업", "github", "gitlab", "소스관리"],
            
            # 도메인 특화
            "A/B테스트": ["AB test", "실험설계", "통계검정", "가설검증"],
            "추천엔진": ["recommendation engine", "협업필터링", "개인화", "추천시스템"],
            "이상탐지": ["anomaly detection", "outlier", "fraud detection", "비정상"],
            "시계열": ["time series", "시간데이터", "예측", "트렌드", "계절성"],
            "텍스트마이닝": ["text mining", "자연어처리", "감정분석", "토픽모델링"]
        }
        
        # 데이터/AI 기술 스택 관련어 (대폭 확장)
        tech_relations = {
            # Python 생태계
            "python": ["pandas", "numpy", "scikit-learn", "데이터분석", "머신러닝"],
            "pandas": ["데이터프레임", "전처리", "데이터조작", "분석"],
            "numpy": ["수치계산", "배열", "선형대수", "과학계산"],
            "scikit-learn": ["머신러닝", "분류", "회귀", "클러스터링"],
            "matplotlib": ["시각화", "플롯", "차트", "그래프"],
            "seaborn": ["통계시각화", "히트맵", "분포", "상관관계"],
            
            # 딥러닝 프레임워크
            "tensorflow": ["딥러닝", "신경망", "모델훈련", "케라스"],
            "pytorch": ["딥러닝", "동적그래프", "연구", "실험"],
            "keras": ["딥러닝", "고수준API", "빠른프로토타이핑"],
            
            # 빅데이터 생태계
            "spark": ["분산처리", "빅데이터", "인메모리", "스케일링"],
            "hadoop": ["분산저장", "HDFS", "맵리듀스", "클러스터"],
            "kafka": ["실시간스트리밍", "메시지큐", "이벤트처리"],
            "airflow": ["워크플로우", "스케줄링", "데이터파이프라인", "오케스트레이션"],
            
            # 데이터베이스
            "postgresql": ["관계형DB", "ACID", "복잡쿼리", "분석"],
            "mongodb": ["NoSQL", "문서DB", "스키마리스", "확장성"],
            "redis": ["인메모리", "캐시", "세션저장", "실시간"],
            "elasticsearch": ["검색엔진", "전문검색", "로그분석", "집계"],
            
            # 클라우드 플랫폼
            "aws": ["S3", "EMR", "Redshift", "SageMaker", "Lambda"],
            "gcp": ["BigQuery", "Dataflow", "AI Platform", "Cloud ML"],
            "azure": ["Synapse", "Data Factory", "Machine Learning", "Cognitive Services"],
            
            # BI/시각화 도구
            "tableau": ["대시보드", "셀프서비스BI", "드래그앤드롭", "시각화"],
            "powerbi": ["마이크로소프트", "비즈니스인텔리전스", "리포팅"],
            "looker": ["모던BI", "데이터모델링", "SQL기반"],
            
            # MLOps 도구
            "mlflow": ["모델라이프사이클", "실험추적", "모델레지스트리"],
            "kubeflow": ["쿠버네티스", "ML워크플로우", "파이프라인"],
            "dvc": ["데이터버전관리", "ML실험", "재현가능성"],
            
            # 특화 라이브러리
            "lightgbm": ["그래디언트부스팅", "빠른학습", "메모리효율"],
            "xgboost": ["앙상블", "부스팅", "구조화데이터", "경진대회"],
            "catboost": ["범주형데이터", "그래디언트부스팅", "자동화"],
            "spacy": ["자연어처리", "NER", "품사태깅", "언어모델"],
            "nltk": ["자연어처리", "토큰화", "형태소분석", "코퍼스"],
            "opencv": ["컴퓨터비전", "이미지처리", "객체인식", "영상분석"],
            
            # 통계/수학 도구
            "scipy": ["과학계산", "최적화", "통계", "신호처리"],
            "statsmodels": ["통계모델링", "회귀분석", "시계열", "가설검정"],
            "networkx": ["그래프분석", "네트워크", "소셜네트워크", "관계분석"]
        }
        
        expanded_terms = [query]
        query_lower = query.lower()
        
        # 기본 동의어 확장
        for key, values in synonyms.items():
            if key in query_lower:
                expanded_terms.extend(values[:4])  # 데이터 분야는 더 많은 동의어 사용
            for value in values:
                if value in query_lower:
                    expanded_terms.append(key)
                    expanded_terms.extend([v for v in values if v != value][:3])
        
        # 기술 스택 관련어 확장
        for tech, relations in tech_relations.items():
            if tech in query_lower:
                expanded_terms.extend(relations[:3])  # 관련 기술도 더 많이 포함
        
        # 데이터/AI 특화 컨텍스트 추론
        data_contexts = {
            "분석": ["데이터분석", "통계", "인사이트", "리포팅"],
            "모델": ["머신러닝", "예측", "알고리즘", "훈련"],
            "처리": ["전처리", "ETL", "파이프라인", "변환"],
            "시각화": ["차트", "대시보드", "그래프", "플롯"],
            "예측": ["모델링", "포캐스팅", "회귀", "분류"],
            "추천": ["개인화", "협업필터링", "랭킹", "매칭"]
        }
        
        for context, related_terms in data_contexts.items():
            if context in query_lower:
                expanded_terms.extend(related_terms[:2])
        
        # 중복 제거 및 가중치 적용
        unique_terms = list(dict.fromkeys(expanded_terms))  # 순서 유지하며 중복 제거
        
        # 데이터/AI 분야는 원본 쿼리에 더 높은 가중치 (5배 반복)
        weighted_query = f"{query} {query} {query} {query} {query} " + " ".join(unique_terms[1:])
        
        return weighted_query
    
    def _hybrid_search(self, query: str, profile_name: str, data_types: List[str], 
                      top_k: int, min_score: float) -> List[Dict[str, Any]]:
        """하이브리드 검색 (의미적 + 키워드)"""
        # 의미적 검색 결과
        semantic_results = self._semantic_search(query, profile_name, data_types, top_k * 2, min_score * 0.7)
        
        # 키워드 검색 결과
        keyword_results = self._keyword_search(query, profile_name, data_types, top_k * 2, min_score * 0.5)
        
        # 결과 병합 및 점수 조합
        combined_results = {}
        
        # 의미적 검색 결과 추가 (가중치 0.7)
        for result in semantic_results:
            key = self._get_result_key(result)
            combined_results[key] = {
                **result,
                "semantic_score": result["score"],
                "keyword_score": 0.0,
                "combined_score": result["score"] * 0.7
            }
        
        # 키워드 검색 결과 추가/업데이트 (가중치 0.3)
        for result in keyword_results:
            key = self._get_result_key(result)
            if key in combined_results:
                # 기존 결과 업데이트
                combined_results[key]["keyword_score"] = result["score"]
                combined_results[key]["combined_score"] = (
                    combined_results[key]["semantic_score"] * 0.7 + 
                    result["score"] * 0.3
                )
            else:
                # 새로운 결과 추가
                combined_results[key] = {
                    **result,
                    "semantic_score": 0.0,
                    "keyword_score": result["score"],
                    "combined_score": result["score"] * 0.3
                }
        
        # 점수 순으로 정렬
        final_results = list(combined_results.values())
        final_results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # 최종 점수로 업데이트
        for result in final_results:
            result["score"] = result["combined_score"]
            result["search_method"] = "hybrid_semantic_keyword"
        
        return final_results[:top_k]
    
    def _get_result_key(self, result: Dict[str, Any]) -> str:
        """결과 고유 키 생성"""
        metadata = result["metadata"]
        return f"{metadata.get('profile_name')}_{metadata.get('type')}_{metadata.get('timestamp')}"
    
    def get_profile_summary(self, profile_name: str) -> Dict[str, Any]:
        """특정 프로필의 요약 정보 반환"""
        profile_entries = [entry for entry in self.metadata if entry.get("profile_name") == profile_name]
        
        if not profile_entries:
            return {"error": f"프로필을 찾을 수 없습니다: {profile_name}"}
        
        # 유형별 통계
        type_counts = {}
        for entry in profile_entries:
            entry_type = entry.get("type", "unknown")
            type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
        
        # 개인정보 추출
        personal_info = None
        for entry in profile_entries:
            if entry.get("type") == "personal_info":
                personal_info = entry.get("data", {})
                break
        
        return {
            "profile_name": profile_name,
            "personal_info": personal_info or {},
            "type_counts": type_counts,
            "total_entries": len(profile_entries),
            "last_updated": max(entry.get("timestamp", "") for entry in profile_entries)
        }
    
    def get_agent_context(self, profile_name: str, agent_type: str, task_context: str = None) -> Dict[str, Any]:
        """
        에이전트별 맞춤형 컨텍스트 생성
        
        Args:
            profile_name: 프로필 이름
            agent_type: 에이전트 유형
            task_context: 작업 컨텍스트
        
        Returns:
            에이전트별 컨텍스트
        """
        # 에이전트별 검색 전략
        agent_strategies = {
            "company_analyst": {
                "query": "회사 분석에 필요한 경험과 목표",
                "data_types": ["work_experience", "career_goals", "personal_info"],
                "top_k": 5
            },
            "jd_analyst": {
                "query": "직무 요구사항에 맞는 기술과 경험",
                "data_types": ["work_experience", "skills", "projects"],
                "top_k": 5
            },
            "question_guide": {
                "query": task_context or "자기소개서 질문에 관련된 경험",
                "data_types": ["work_experience", "projects", "education"],
                "top_k": 5
            },
            "experience_guide": {
                "query": "STAR 방법론에 적합한 구체적 경험",
                "data_types": ["work_experience", "projects"],
                "top_k": 3
            },
            "writing_guide": {
                "query": "글쓰기 전략에 필요한 경험과 목표",
                "data_types": ["work_experience", "projects", "career_goals"],
                "top_k": 5
            }
        }
        
        strategy = agent_strategies.get(agent_type, {
            "query": "관련 경험",
            "data_types": ["work_experience", "projects"],
            "top_k": 3
        })
        
        # 통합 벡터DB에서 검색
        relevant_entries = self.search_unified_profile(
            query=strategy["query"],
            profile_name=profile_name,
            data_types=strategy["data_types"],
            top_k=strategy["top_k"]
        )
        
        # 컨텍스트 구성
        context = {
            "profile_name": profile_name,
            "agent_type": agent_type,
            "task_context": task_context,
            "relevant_entries": relevant_entries,
            "strategy": strategy,
            "vectordb_enabled": True,
            "context_timestamp": datetime.now().isoformat()
        }
        
        return context
    
    def _add_entry(self, text: str, metadata: Dict[str, Any]) -> int:
        """벡터DB에 엔트리 추가 (메모리 최적화 + 키워드 인덱스)"""
        # 텍스트 벡터화
        embedding = self.encoder.encode([text])
        faiss.normalize_L2(embedding)
        
        # FAISS 인덱스에 추가
        self.index.add(embedding)
        
        # 메타데이터 최적화 (큰 데이터는 ID만 저장)
        optimized_metadata = {
            "type": metadata.get("type"),
            "profile_name": metadata.get("profile_name"),
            "timestamp": metadata.get("timestamp"),
            "index": metadata.get("index")  # 배열 인덱스만 저장
        }
        
        # 데이터는 별도 저장 (필요시에만 로드)
        entry_id = len(self.data_entries)
        self.data_entries.append(text)
        self.metadata.append(optimized_metadata)
        
        # 키워드 인덱스 업데이트
        self._update_keyword_index(text, entry_id)
        
        # 원본 데이터는 별도 파일에 저장
        self._save_entry_data(entry_id, metadata.get("data", {}))
        
        return entry_id
    
    def _update_keyword_index(self, text: str, doc_id: int):
        """새 문서에 대해 키워드 인덱스 업데이트"""
        tokens = self._tokenize(text)
        doc_freq = Counter(tokens)
        
        # 문서 빈도와 길이 리스트 확장 (필요한 경우)
        while len(self.doc_frequencies) <= doc_id:
            self.doc_frequencies.append({})
            self.doc_lengths.append(0)
        
        self.doc_frequencies[doc_id] = doc_freq
        self.doc_lengths[doc_id] = len(tokens)
        
        # 평균 문서 길이 재계산
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        
        # 역색인 업데이트
        for token in set(tokens):
            if token not in self.keyword_index:
                self.keyword_index[token] = []
            if doc_id not in self.keyword_index[token]:
                self.keyword_index[token].append(doc_id)
    
    def _save_entry_data(self, entry_id: int, data: Dict[str, Any]):
        """엔트리 데이터를 별도 파일에 저장"""
        data_dir = self.db_path / "entry_data"
        data_dir.mkdir(exist_ok=True)
        
        data_file = data_dir / f"entry_{entry_id}.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    
    def _load_entry_data(self, entry_id: int) -> Dict[str, Any]:
        """엔트리 데이터를 별도 파일에서 로드"""
        data_file = self.db_path / "entry_data" / f"entry_{entry_id}.json"
        
        if not data_file.exists():
            return {}
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def get_entry_with_data(self, entry_id: int) -> Dict[str, Any]:
        """엔트리 ID로 완전한 데이터 조회"""
        if entry_id >= len(self.metadata):
            return {}
        
        metadata = self.metadata[entry_id].copy()
        metadata["data"] = self._load_entry_data(entry_id)
        metadata["text"] = self.data_entries[entry_id]
        
        return metadata
    
    def _personal_info_to_text(self, personal_info: Dict[str, Any]) -> str:
        """개인정보를 검색 가능한 텍스트로 변환"""
        parts = []
        parts.append(f"이름: {personal_info.get('name', '')}")
        parts.append(f"이메일: {personal_info.get('email', '')}")
        parts.append(f"전화번호: {personal_info.get('phone', '')}")
        parts.append(f"거주지: {personal_info.get('location', '')}")
        return " ".join(parts)
    
    def _education_to_text(self, education: Dict[str, Any]) -> str:
        """학력 정보를 검색 가능한 텍스트로 변환"""
        parts = []
        parts.append(f"학교: {education.get('university', '')}")
        parts.append(f"전공: {education.get('major', '')}")
        parts.append(f"학위: {education.get('degree', '')}")
        parts.append(f"졸업년도: {education.get('graduation_year', '')}")
        parts.append(f"학점: {education.get('gpa', '')}")
        parts.extend(education.get('relevant_courses', []))
        parts.extend(education.get('honors', []))
        return " ".join(parts)
    
    def _work_experience_to_text(self, experience: Dict[str, Any]) -> str:
        """경력 정보를 검색 가능한 텍스트로 변환"""
        parts = []
        parts.append(f"회사: {experience.get('company', '')}")
        parts.append(f"직책: {experience.get('position', '')}")
        parts.append(f"부서: {experience.get('department', '')}")
        parts.append(f"기간: {experience.get('duration', {}).get('start', '')} ~ {experience.get('duration', {}).get('end', '')}")
        parts.extend(experience.get('responsibilities', []))
        
        # 성과 정보
        for achievement in experience.get('achievements', []):
            parts.append(f"성과: {achievement.get('description', '')}")
            parts.append(f"지표: {achievement.get('metrics', '')}")
            parts.append(f"임팩트: {achievement.get('impact', '')}")
        
        parts.extend(experience.get('technologies', []))
        parts.append(f"팀규모: {experience.get('team_size', '')}")
        parts.extend(experience.get('key_projects', []))
        
        return " ".join(parts)
    
    def _project_to_text(self, project: Dict[str, Any]) -> str:
        """프로젝트 정보를 검색 가능한 텍스트로 변환"""
        parts = []
        parts.append(f"프로젝트명: {project.get('name', '')}")
        parts.append(f"유형: {project.get('type', '')}")
        parts.append(f"기간: {project.get('duration', {}).get('start', '')} ~ {project.get('duration', {}).get('end', '')}")
        parts.append(f"설명: {project.get('description', '')}")
        parts.append(f"역할: {project.get('role', '')}")
        parts.extend(project.get('technologies', []))
        parts.append(f"성과: {project.get('achievements', '')}")
        parts.append(f"팀규모: {project.get('team_size', '')}")
        
        return " ".join(parts)
    
    def _skills_to_text(self, skills: Dict[str, Any]) -> str:
        """기술 스택을 검색 가능한 텍스트로 변환"""
        parts = []
        for category, skill_list in skills.items():
            if isinstance(skill_list, list):
                parts.extend(skill_list)
        return " ".join(parts)
    
    def _certification_to_text(self, certification: Dict[str, Any]) -> str:
        """자격증 정보를 검색 가능한 텍스트로 변환"""
        parts = []
        parts.append(f"자격증명: {certification.get('name', '')}")
        parts.append(f"발급기관: {certification.get('issuer', '')}")
        parts.append(f"취득일: {certification.get('date', '')}")
        parts.append(f"점수: {certification.get('score', '')}")
        return " ".join(parts)
    
    def _award_to_text(self, award: Dict[str, Any]) -> str:
        """수상내역을 검색 가능한 텍스트로 변환"""
        parts = []
        parts.append(f"수상명: {award.get('name', '')}")
        parts.append(f"수여기관: {award.get('issuer', '')}")
        parts.append(f"수상일: {award.get('date', '')}")
        parts.append(f"내용: {award.get('description', '')}")
        return " ".join(parts)
    
    def _career_goals_to_text(self, goals: Dict[str, Any]) -> str:
        """커리어 목표를 검색 가능한 텍스트로 변환"""
        parts = []
        parts.append(f"단기목표: {goals.get('short_term', '')}")
        parts.append(f"장기목표: {goals.get('long_term', '')}")
        parts.extend(goals.get('target_companies', []))
        parts.extend(goals.get('preferred_roles', []))
        return " ".join(parts)
    
    def _interests_to_text(self, interests: List[str]) -> str:
        """관심사를 검색 가능한 텍스트로 변환"""
        return " ".join(interests)
    
    def save_db(self):
        """벡터DB 저장"""
        # FAISS 인덱스 저장
        index_path = self.db_path / "unified_faiss_index.bin"
        faiss.write_index(self.index, str(index_path))
        
        # 메타데이터 저장
        metadata_path = self.db_path / "unified_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "data_entries": self.data_entries,
                "metadata": self.metadata
            }, f, ensure_ascii=False, indent=2)
        
        print(f"통합 벡터DB 저장 완료: {self.db_path}")
    
    def _load_existing_db(self):
        """기존 통합 벡터DB 로드"""
        index_path = self.db_path / "unified_faiss_index.bin"
        metadata_path = self.db_path / "unified_metadata.json"
        
        if index_path.exists() and metadata_path.exists():
            try:
                # FAISS 인덱스 로드
                self.index = faiss.read_index(str(index_path))
                
                # 메타데이터 로드
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.data_entries = data["data_entries"]
                    self.metadata = data["metadata"]
                
                print(f"기존 통합 벡터DB 로드 완료: {len(self.data_entries)}개 엔트리")
            except Exception as e:
                print(f"DB 로드 실패, 새로 시작: {e}")
    
    def get_db_stats(self) -> Dict[str, Any]:
        """벡터DB 통계 반환"""
        type_counts = {}
        profile_counts = {}
        
        for entry in self.metadata:
            entry_type = entry.get("type", "unknown")
            profile_name = entry.get("profile_name", "unknown")
            
            type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
            profile_counts[profile_name] = profile_counts.get(profile_name, 0) + 1
        
        return {
            "total_entries": len(self.data_entries),
            "type_counts": type_counts,
            "profile_counts": profile_counts,
            "index_size": self.index.ntotal
        } 

    def _remove_profile_entries(self, profile_name: str):
        """특정 프로필의 모든 엔트리 제거"""
        if not self.metadata:
            return
        
        # 제거할 인덱스 찾기
        indices_to_remove = []
        for i, metadata in enumerate(self.metadata):
            if metadata.get("profile_name") == profile_name:
                indices_to_remove.append(i)
        
        if not indices_to_remove:
            return
        
        print(f"🗑️  기존 프로필 '{profile_name}' 엔트리 {len(indices_to_remove)}개 제거 중...")
        
        # 역순으로 제거 (인덱스 변경 방지)
        for idx in reversed(indices_to_remove):
            del self.data_entries[idx]
            del self.metadata[idx]
        
        # FAISS 인덱스 재구축 (비효율적이지만 정확함)
        self._rebuild_faiss_index()
    
    def _rebuild_faiss_index(self):
        """FAISS 인덱스 재구축"""
        if not self.data_entries:
            self.index = faiss.IndexFlatIP(self.dimension)
            return
        
        # 새로운 인덱스 생성
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # 모든 엔트리 다시 임베딩하여 추가
        embeddings = self.encoder.encode(self.data_entries)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings) 

    def _semantic_search(self, query: str, profile_name: str, data_types: List[str], 
                        top_k: int, min_score: float) -> List[Dict[str, Any]]:
        """의미적 검색 (데이터/AI 특화 가중치 적용)"""
        # 쿼리 임베딩 캐싱
        cache_key = f"semantic_{hash(query)}"
        if cache_key not in self.query_cache:
            query_embedding = self.encoder.encode([query])
            faiss.normalize_L2(query_embedding)
            self.query_cache[cache_key] = query_embedding
        else:
            query_embedding = self.query_cache[cache_key]
        
        # 검색 (더 많은 결과를 가져와서 필터링)
        search_k = min(top_k * 3, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, search_k)
        
        # 데이터/AI 특화 타입별 가중치
        type_weights = {
            # 데이터/AI 핵심 경험 (최고 가중치)
            "work_experience": 1.5,    # 실무 경험이 가장 중요
            "project": 1.4,            # 프로젝트 경험도 매우 중요
            
            # 기술적 역량
            "skills": 1.3,             # 기술 스택이 매우 중요
            "certifications": 1.2,     # 데이터/AI 자격증 중요
            
            # 학습/연구 배경
            "education": 1.1,          # 학문적 배경 중요 (통계, 수학, CS)
            "research": 1.3,           # 연구 경험 (새로운 타입)
            "publications": 1.2,       # 논문/출간물 (새로운 타입)
            
            # 부가적 요소
            "career_goals": 1.0,       # 커리어 목표
            "personal_info": 0.9,      # 개인정보
            "award": 1.1,              # 수상 경력 (데이터 경진대회 등)
            "interests": 0.8,          # 관심사
            
            # 데이터/AI 특화 새로운 타입들
            "kaggle_competitions": 1.3,  # 캐글 경진대회
            "data_projects": 1.4,        # 데이터 프로젝트
            "ml_models": 1.3,            # ML 모델 개발
            "analytics_reports": 1.1,    # 분석 리포트
            "data_pipelines": 1.2,       # 데이터 파이프라인
            "dashboards": 1.0,           # 대시보드 구축
            "ab_tests": 1.1,             # A/B 테스트 경험
            "feature_engineering": 1.2,  # 피처 엔지니어링
            "model_deployment": 1.3,     # 모델 배포
            "data_visualization": 1.0    # 데이터 시각화
        }
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and score >= min_score:
                metadata = self.metadata[idx]
                
                # 프로필 필터링
                if profile_name and metadata.get("profile_name") != profile_name:
                    continue
                
                # 데이터 유형 필터링
                if data_types and metadata.get("type") not in data_types:
                    continue
                
                # 타입별 가중치 적용
                entry_type = metadata.get("type", "unknown")
                weighted_score = float(score) * type_weights.get(entry_type, 1.0)
                
                # 데이터/AI 키워드 보너스 점수
                text = self.data_entries[idx].lower()
                data_ai_keywords = [
                    "python", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
                    "machine learning", "deep learning", "data science", "analytics",
                    "sql", "spark", "hadoop", "kafka", "airflow", "tableau", "powerbi",
                    "statistics", "regression", "classification", "clustering", "nlp",
                    "computer vision", "recommendation", "time series", "a/b test"
                ]
                
                keyword_bonus = 0.0
                for keyword in data_ai_keywords:
                    if keyword in text:
                        keyword_bonus += 0.05  # 각 키워드마다 5% 보너스
                
                final_score = weighted_score * (1.0 + min(keyword_bonus, 0.3))  # 최대 30% 보너스
                
                results.append({
                    "metadata": metadata,
                    "score": final_score,
                    "original_score": float(score),
                    "type_weight": type_weights.get(entry_type, 1.0),
                    "keyword_bonus": keyword_bonus,
                    "text": self.data_entries[idx],
                    "search_method": "semantic_similarity_data_ai"
                })
        
        # 가중치가 적용된 점수로 정렬
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _keyword_search(self, query: str, profile_name: str, data_types: List[str], 
                       top_k: int, min_score: float) -> List[Dict[str, Any]]:
        """BM25 기반 키워드 검색"""
        if not self.keyword_index:
            self._build_keyword_index()
        
        # 쿼리 토큰화
        query_tokens = self._tokenize(query)
        
        # BM25 점수 계산
        bm25_scores = self._calculate_bm25_scores(query_tokens)
        
        # 점수가 있는 문서들만 필터링
        candidate_docs = [(doc_id, score) for doc_id, score in enumerate(bm25_scores) if score > min_score]
        candidate_docs.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in candidate_docs[:top_k * 2]:  # 여유있게 가져오기
            if doc_id >= len(self.metadata):
                continue
                
            metadata = self.metadata[doc_id]
            
            # 프로필 필터링
            if profile_name and metadata.get("profile_name") != profile_name:
                continue
            
            # 데이터 유형 필터링
            if data_types and metadata.get("type") not in data_types:
                continue
            
            results.append({
                "metadata": metadata,
                "score": score,
                "text": self.data_entries[doc_id],
                "search_method": "keyword_bm25"
            })
        
        return results[:top_k]
    
    def _build_keyword_index(self):
        """키워드 인덱스 구축 (BM25용)"""
        self.keyword_index = {}
        self.doc_frequencies = []
        self.doc_lengths = []
        
        for doc_id, text in enumerate(self.data_entries):
            tokens = self._tokenize(text)
            doc_freq = Counter(tokens)
            self.doc_frequencies.append(doc_freq)
            self.doc_lengths.append(len(tokens))
            
            # 역색인 구축
            for token in set(tokens):
                if token not in self.keyword_index:
                    self.keyword_index[token] = []
                self.keyword_index[token].append(doc_id)
        
        # 평균 문서 길이 계산
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
    
    def _tokenize(self, text: str) -> List[str]:
        """텍스트 토큰화 (한글/영문 지원)"""
        # 한글, 영문, 숫자만 추출
        text = re.sub(r'[^\w\s가-힣]', ' ', text.lower())
        tokens = text.split()
        
        # 불용어 제거
        stop_words = {
            '이', '그', '저', '것', '수', '있', '하', '되', '될', '한', '일', '때', '중', '및', '등', 
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        }
        
        return [token for token in tokens if len(token) > 1 and token not in stop_words]
    
    def _calculate_bm25_scores(self, query_tokens: List[str]) -> List[float]:
        """BM25 점수 계산"""
        k1, b = 1.5, 0.75  # BM25 파라미터
        N = len(self.data_entries)  # 전체 문서 수
        
        scores = [0.0] * N
        
        for token in query_tokens:
            if token not in self.keyword_index:
                continue
            
            # 해당 토큰을 포함한 문서들
            docs_with_token = self.keyword_index[token]
            df = len(docs_with_token)  # 문서 빈도
            
            # IDF 계산
            idf = math.log((N - df + 0.5) / (df + 0.5))
            
            for doc_id in docs_with_token:
                # TF 계산
                tf = self.doc_frequencies[doc_id].get(token, 0)
                doc_len = self.doc_lengths[doc_id]
                
                # BM25 점수 계산
                score = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / self.avg_doc_length))
                scores[doc_id] += score
        
        return scores 
# ResumeAgents: AI 기반 취업 서류 작성 도구

> 🎉 **ResumeAgents** - 데이터/AI 분야에 특화된 멀티 에이전트 자기소개서 작성 프레임워크

## 🚀 주요 기능

### ✨ **핵심 특징**
- **🎯 자동 문항 분석**: AI가 자기소개서 질문 유형을 자동 분류하고 맞춤 가이드 제공
- **🔍 스마트 경험 매칭**: 하이브리드 검색으로 관련 경험을 정확하게 추천
- **📊 데이터/AI 특화**: 데이터 사이언스, 머신러닝, 빅데이터 분야 전문 최적화
- **📝 글자수 최적화**: 한글 기준 글자수 제한에 맞춘 구조적 작성 가이드
- **🤖 멀티 에이전트**: 전문화된 AI 에이전트들의 협업으로 고품질 결과 생성

### 🎯 **지원하는 분야**
- **데이터 사이언스**: Python, R, 통계, 머신러닝
- **데이터 엔지니어링**: Spark, Hadoop, ETL, 파이프라인
- **AI/ML**: TensorFlow, PyTorch, 딥러닝, NLP
- **빅데이터**: Kafka, Elasticsearch, 실시간 처리
- **클라우드/MLOps**: AWS, GCP, 모델 배포, 모니터링

## 📦 설치 및 설정

### 1. 프로젝트 설치
```bash
# 1) 프로젝트 클론
git clone https://github.com/hjongc/ResumeAgents.git
cd ResumeAgents

# 2) 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3) 의존성 설치
pip install -r requirements.txt

# 4) 고급 검색 기능 (선택사항)
pip install sentence-transformers faiss-cpu
```

### 2. API 키 설정
```bash
export OPENAI_API_KEY=your_api_key_here
```

## 🎯 사용법

### **Step 1: 프로필 생성**

```python
from resumeagents.utils import ProfileManager

# ProfileManager 초기화 (Advanced 모드 권장)
pm = ProfileManager(mode='advanced')

# 프로필 템플릿 생성
profile = pm.create_profile_template()

# 기본 정보 입력
profile['personal_info'] = {
    'name': '김데이터',
    'email': 'kim.data@example.com',
    'phone': '010-1234-5678',
    'github': 'https://github.com/kimdata'
}

# 경력 정보 추가
profile['work_experience'] = [
    {
        'company': '네이버',
        'position': '데이터 사이언티스트',
        'duration': {'start': '2022-03', 'end': '2024-12'},
        'responsibilities': [
            'Python pandas, numpy를 활용한 대용량 데이터 분석',
            'scikit-learn, TensorFlow로 머신러닝 모델 개발',
            'A/B 테스트 설계 및 통계적 가설 검정'
        ],
        'achievements': [
            {
                'description': '추천 시스템 정확도 개선',
                'metrics': '클릭률 25% 향상',
                'impact': '월간 매출 12억원 증대'
            }
        ],
        'technologies': ['Python', 'pandas', 'TensorFlow', 'SQL']
    }
]

# 프로젝트 경험 추가
profile['projects'] = [
    {
        'name': '실시간 추천 시스템',
        'description': '사용자 행동 데이터 기반 개인화 추천 엔진',
        'technologies': ['Python', 'TensorFlow', 'Kafka', 'Redis'],
        'achievements': ['추천 정확도 90% 달성', '일일 사용자 30% 증가']
    }
]

# 기술 스택 추가
profile['skills'] = {
    'programming_languages': [
        {'name': 'Python', 'proficiency': 'expert', 'years': 4},
        {'name': 'SQL', 'proficiency': 'expert', 'years': 3}
    ],
    'frameworks_libraries': [
        'pandas', 'numpy', 'scikit-learn', 'TensorFlow'
    ],
    'cloud_platforms': ['AWS', 'GCP'],
    'tools': ['Git', 'Docker', 'Jupyter', 'Tableau']
}

# 프로필 저장 (JSON + 벡터DB 자동 동기화)
pm.save_profile(profile, '김데이터_데이터사이언티스트')
```

### **Step 2: 자기소개서 작성**

#### 간단한 방법 (메인 프로그램 사용)
```bash
python main.py
```

#### 코드로 직접 사용
```python
import asyncio
from resumeagents.graph.resume_graph import ResumeAgentsGraph
from resumeagents.default_config import DEFAULT_CONFIG

# 설정
config = DEFAULT_CONFIG.copy()
config['analysis_depth'] = 'high'  # 분석 깊이
config['document_type'] = 'cover_letter'  # 자기소개서

# 지원 정보
company_name = "카카오"
job_title = "데이터 사이언티스트"
job_description = """
[필수 요건]
- Python, R을 활용한 데이터 분석 경험 3년 이상
- 머신러닝 모델 개발 및 운영 경험
- SQL을 활용한 데이터 추출 및 가공 경험

[우대 사항]
- TensorFlow, PyTorch 등 딥러닝 프레임워크 경험
- 클라우드 플랫폼(AWS, GCP) 활용 경험
"""

# 자기소개서 문항
candidate_info = {
    "name": "김데이터",
    "profile_name": "김데이터_데이터사이언티스트",
    "custom_questions": [
        {
            "question": "지원 동기와 입사 후 포부를 기술해 주십시오.",
            "type": "motivation",
            "char_limit": 1000
        },
        {
            "question": "데이터 분석 프로젝트 경험을 구체적으로 설명해 주세요.",
            "type": "data_analysis",
            "char_limit": 1500
        }
    ]
}

# ResumeAgents 실행
ra = ResumeAgentsGraph(debug=True, config=config)
final_state, decision = asyncio.run(ra.propagate(
    company_name=company_name,
    job_title=job_title,
    job_description=job_description,
    candidate_info=candidate_info
))

# 결과 확인
print(f"품질 점수: {decision['quality_score']:.1f}/100")
for guide in final_state.analysis_results["question_guides"]["guides"]:
    print(f"문항: {guide['question']['question']}")
    print(f"가이드: {guide['guide'][:200]}...")
```

### **Step 3: 고급 검색 활용**

```python
# 관련 경험 검색 (데이터/AI 특화)
results = pm.find_relevant_experiences_for_question(
    profile_name='김데이터_데이터사이언티스트',
    question='Python pandas를 사용한 데이터 전처리 경험이 있나요?',
    question_type='data_analysis',  # 데이터/AI 특화 질문 유형
    search_mode='hybrid',           # 하이브리드 검색 (추천)
    top_k=3
)

# 검색 결과 확인
for result in results:
    print(f"타입: {result['type']}")
    print(f"관련도: {result['relevance_score']:.3f}")
    print(f"내용: {result['data']}")
```

## 🎯 데이터/AI 특화 질문 유형

### **기술적 경험**
- `data_analysis`: 데이터 분석 경험
- `machine_learning`: 머신러닝 모델 개발
- `data_engineering`: 데이터 파이프라인 구축
- `statistics`: 통계 분석 및 가설 검정

### **프로그래밍 & 도구**
- `python`: Python 개발 경험
- `sql`: 데이터베이스 쿼리 및 분석
- `spark`: 빅데이터 처리 (Spark, Hadoop)
- `cloud`: 클라우드 플랫폼 활용

### **프로젝트 & 성과**
- `ml_project`: 머신러닝 프로젝트
- `data_project`: 데이터 분석 프로젝트
- `kaggle`: 캐글 경진대회 참여
- `ab_testing`: A/B 테스트 설계 및 분석

### **비즈니스 & 도메인**
- `visualization`: 데이터 시각화 (Tableau, PowerBI)
- `mlops`: 모델 배포 및 운영
- `recommendation`: 추천 시스템 개발
- `forecasting`: 예측 모델링

## 📊 출력 결과

### **문항별 맞춤 가이드**
- **문항 분석**: 질문 의도, 평가 포인트, 문항 유형 자동 분류
- **작성 전략**: 구조 추천, 내용 배분, 핵심 메시지
- **경험 매칭**: 하이브리드 검색으로 관련 경험 자동 추천
- **글자수 최적화**: 제한에 맞춘 섹션별 글자수 배분

### **결과 저장**
```
outputs/
└── 카카오_데이터사이언티스트_20250107_143052/
    ├── analysis_results.json      # 전체 분석 결과
    ├── question_guides.json       # 문항별 작성 가이드
    ├── experience_guides.json     # 경험 매칭 결과
    ├── writing_guides.json        # 최종 작성 가이드
    └── summary.txt               # 요약 정보
```

## ⚙️ 설정 옵션

### **분석 깊이**
- `low`: 빠른 분석 (기본 가이드)
- `medium`: 표준 분석 (균형잡힌 품질)
- `high`: 심층 분석 (최고 품질, 시간 소요)

### **검색 모드**
- `semantic`: 의미적 검색 (컨텍스트 이해 중시)
- `keyword`: 키워드 검색 (정확한 매칭 중시)
- `hybrid`: 하이브리드 검색 (추천, 최고 성능)

### **문서 유형**
- `resume`: 이력서 최적화
- `cover_letter`: 자기소개서 최적화

## 🛠️ 기술 스택

- **LangGraph**: 멀티 에이전트 워크플로우
- **OpenAI GPT-4o-mini**: 고성능 언어 모델
- **FAISS**: 벡터 유사도 검색 (고급 기능)
- **Sentence Transformers**: 다국어 텍스트 임베딩

## 📚 추가 문서

- [개발 전략](DEVELOPMENT_STRATEGY.md): 에이전트 구조 및 개발 방향
- [사용법 상세 가이드](USAGE_GUIDE.md): 단계별 상세 사용법

## 🤝 기여하기

버그 수정, 문서 개선, 새로운 기능 제안 등 모든 기여를 환영합니다!

## 📄 라이선스

Apache-2.0 라이선스

## 📖 인용

```
@misc{resumeagents2024,
      title={ResumeAgents: Multi-Agents LLM Resume & Job Application Framework}, 
      author={chai hyeon jong},
      year={2024},
      url={https://github.com/hjongc/ResumeAgents}, 
}
```

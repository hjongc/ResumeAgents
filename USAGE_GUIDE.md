# ResumeAgents 상세 사용법 가이드

이 가이드는 ResumeAgents를 처음 사용하는 사용자부터 고급 기능을 활용하고자 하는 사용자까지 모든 레벨의 사용자를 위한 단계별 가이드입니다.

## 📋 목차

1. [시작하기](#1-시작하기)
2. [프로필 생성 및 관리](#2-프로필-생성-및-관리)
3. [자기소개서 작성 프로세스](#3-자기소개서-작성-프로세스)
4. [고급 검색 기능 활용](#4-고급-검색-기능-활용)
5. [결과 분석 및 활용](#5-결과-분석-및-활용)
6. [문제 해결](#6-문제-해결)

## 1. 시작하기

### 1.1 환경 설정

```bash
# 1) 프로젝트 클론 및 이동
git clone https://github.com/hjongc/ResumeAgents.git
cd ResumeAgents

# 2) 가상환경 생성 (Python 3.8+ 필요)
python -m venv venv

# 3) 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4) 기본 의존성 설치
pip install -r requirements.txt

# 5) 고급 기능을 위한 추가 패키지 (권장)
pip install sentence-transformers faiss-cpu
```

### 1.2 API 키 설정

```bash
# 환경변수로 설정 (권장)
export OPENAI_API_KEY="your_openai_api_key_here"

# 또는 .env 파일에 저장
echo "OPENAI_API_KEY=your_openai_api_key_here" >> .env
```

### 1.3 첫 실행 테스트

```bash
# 간단한 테스트 실행
python main.py

# 또는 Python 코드로 테스트
python -c "
from resumeagents.utils import ProfileManager
pm = ProfileManager(mode='light')
print('✅ ResumeAgents 설치 완료!')
"
```

## 2. 프로필 생성 및 관리

### 2.1 ProfileManager 초기화

```python
from resumeagents.utils import ProfileManager

# Light Mode (기본): JSON 기반, 빠른 처리
pm_light = ProfileManager(mode='light')

# Advanced Mode (권장): JSON + 벡터DB, 고급 검색
pm_advanced = ProfileManager(mode='advanced')
```

### 2.2 프로필 템플릿 생성

```python
# 빈 프로필 템플릿 생성
profile = pm_advanced.create_profile_template()

# 템플릿 구조 확인
print("프로필 섹션:", list(profile.keys()))
# 출력: ['profile_metadata', 'personal_info', 'education', 'work_experience', 
#        'projects', 'skills', 'certifications', 'awards', 'career_goals', 'interests']
```

### 2.3 단계별 정보 입력

#### 2.3.1 기본 정보 입력

```python
profile['personal_info'] = {
    'name': '김데이터',
    'email': 'kim.data@example.com',
    'phone': '010-1234-5678',
    'address': '서울시 강남구',
    'linkedin': 'https://linkedin.com/in/kimdata',
    'github': 'https://github.com/kimdata',
    'portfolio': 'https://kimdata.github.io',
    'blog': 'https://medium.com/@kimdata'
}
```

#### 2.3.2 학력 정보 추가

```python
profile['education'] = [
    {
        'school': '서울대학교',
        'degree': '학사',
        'major': '컴퓨터공학과',
        'minor': '통계학과',  # 선택사항
        'duration': {'start': '2018-03', 'end': '2022-02'},
        'gpa': {'score': 3.8, 'scale': 4.3},
        'honors': ['magna cum laude', '학과 우수상'],
        'relevant_courses': [
            '데이터구조와 알고리즘',
            '데이터베이스 시스템',
            '머신러닝',
            '통계학',
            '선형대수학',
            '확률론'
        ],
        'thesis': {  # 졸업논문 (선택사항)
            'title': '딥러닝을 활용한 자연어 감정 분석',
            'advisor': '김교수'
        }
    }
]
```

#### 2.3.3 경력 정보 상세 입력

```python
profile['work_experience'] = [
    {
        'company': '네이버',
        'position': '데이터 사이언티스트',
        'duration': {'start': '2022-03', 'end': '2024-12'},
        'employment_type': 'full-time',
        'department': 'AI Lab',
        'team': '추천시스템팀',
        'responsibilities': [
            'Python pandas, numpy를 활용한 대용량 사용자 행동 데이터 분석',
            'scikit-learn, TensorFlow 기반 머신러닝 모델 개발 및 성능 최적화',
            'A/B 테스트 설계, 실행 및 통계적 유의성 검정',
            'Tableau를 활용한 비즈니스 인텔리전스 대시보드 구축 및 운영',
            '실시간 추천 시스템 알고리즘 개발 및 성능 모니터링'
        ],
        'achievements': [
            {
                'description': '개인화 추천 시스템 정확도 개선',
                'metrics': '클릭률 25% 향상, 전환율 18% 증가',
                'impact': '월간 활성 사용자 15% 증가, 매출 12억원 증대 기여',
                'period': '2023-06 ~ 2024-03'
            },
            {
                'description': '실시간 이상 탐지 시스템 구축',
                'metrics': '탐지 정확도 95%, 응답시간 100ms 이하',
                'impact': '시스템 장애 예방으로 연간 5억원 손실 방지',
                'period': '2023-01 ~ 2023-05'
            }
        ],
        'technologies': [
            'Python', 'pandas', 'numpy', 'scikit-learn', 'TensorFlow',
            'SQL', 'PostgreSQL', 'Redis', 'Apache Kafka', 'Docker',
            'Tableau', 'Jupyter', 'Git', 'AWS (S3, EC2, RDS)'
        ],
        'key_projects': [
            '실시간 추천 시스템 v2.0',
            '사용자 행동 예측 모델',
            '이상 거래 탐지 시스템'
        ]
    }
]
```

#### 2.3.4 프로젝트 경험 상세 입력

```python
profile['projects'] = [
    {
        'name': '실시간 개인화 추천 시스템',
        'description': '사용자 행동 데이터와 아이템 특성을 기반으로 한 실시간 개인화 추천 엔진 개발',
        'duration': {'start': '2023-06', 'end': '2024-03'},
        'role': '데이터 사이언티스트 (팀 리더)',
        'team_size': 5,
        'responsibilities': [
            '추천 알고리즘 설계 및 구현',
            '대용량 사용자 데이터 전처리 파이프라인 구축',
            '모델 성능 평가 및 A/B 테스트 설계',
            '실시간 서빙 시스템 아키텍처 설계'
        ],
        'technologies': [
            'Python', 'TensorFlow', 'Apache Kafka', 'Redis',
            'PostgreSQL', 'Docker', 'Kubernetes', 'Apache Airflow'
        ],
        'achievements': [
            '추천 정확도 90% 달성 (기존 대비 15% 향상)',
            '실시간 처리 지연시간 100ms 이하 달성',
            '일일 활성 사용자 30% 증가',
            'CTR(Click-Through Rate) 40% 개선'
        ],
        'challenges_solutions': [
            {
                'challenge': '대용량 실시간 데이터 처리',
                'solution': 'Apache Kafka와 Redis를 활용한 스트리밍 아키텍처 구축'
            },
            {
                'challenge': '콜드 스타트 문제',
                'solution': '하이브리드 필터링과 컨텐츠 기반 필터링 결합'
            }
        ],
        'links': {
            'github': 'https://github.com/kimdata/recommendation-system',
            'demo': 'https://demo.recommendation.com',
            'documentation': 'https://docs.recommendation.com'
        },
        'business_impact': '월간 매출 8억원 증대, 사용자 만족도 25% 향상'
    }
]
```

#### 2.3.5 기술 스택 상세 정보

```python
profile['skills'] = {
    'programming_languages': [
        {'name': 'Python', 'proficiency': 'expert', 'years': 4, 'projects_count': 15},
        {'name': 'R', 'proficiency': 'advanced', 'years': 2, 'projects_count': 8},
        {'name': 'SQL', 'proficiency': 'expert', 'years': 3, 'projects_count': 20},
        {'name': 'Java', 'proficiency': 'intermediate', 'years': 1, 'projects_count': 3}
    ],
    'frameworks_libraries': {
        'data_analysis': ['pandas', 'numpy', 'scipy', 'statsmodels'],
        'machine_learning': ['scikit-learn', 'TensorFlow', 'PyTorch', 'XGBoost', 'LightGBM'],
        'visualization': ['matplotlib', 'seaborn', 'plotly', 'bokeh'],
        'web_frameworks': ['Flask', 'FastAPI'],
        'others': ['Apache Spark', 'Apache Kafka', 'Apache Airflow']
    },
    'databases': [
        {'name': 'PostgreSQL', 'proficiency': 'expert', 'use_cases': ['OLTP', 'Analytics']},
        {'name': 'MySQL', 'proficiency': 'advanced', 'use_cases': ['Web Applications']},
        {'name': 'MongoDB', 'proficiency': 'intermediate', 'use_cases': ['Document Store']},
        {'name': 'Redis', 'proficiency': 'advanced', 'use_cases': ['Caching', 'Real-time']}
    ],
    'cloud_platforms': [
        {
            'name': 'AWS',
            'proficiency': 'advanced',
            'services': ['S3', 'EC2', 'RDS', 'Lambda', 'SageMaker', 'Kinesis']
        },
        {
            'name': 'Google Cloud Platform',
            'proficiency': 'intermediate', 
            'services': ['BigQuery', 'Cloud ML', 'Dataflow']
        }
    ],
    'tools': {
        'development': ['Git', 'Docker', 'Kubernetes', 'Jenkins'],
        'data_tools': ['Jupyter', 'Apache Spark', 'Apache Kafka', 'Apache Airflow'],
        'visualization': ['Tableau', 'PowerBI', 'Grafana'],
        'monitoring': ['Prometheus', 'ELK Stack']
    },
    'specializations': [
        '머신러닝 모델 개발 및 최적화',
        '대용량 데이터 처리 및 분석',
        '실시간 데이터 파이프라인 구축',
        'A/B 테스트 설계 및 분석',
        '추천 시스템 개발',
        '시계열 데이터 분석 및 예측'
    ]
}
```

### 2.4 프로필 저장 및 관리

```python
# 프로필 저장 (JSON + 벡터DB 자동 동기화)
profile_path = pm_advanced.save_profile(profile, '김데이터_데이터사이언티스트_v1')
print(f"프로필 저장됨: {profile_path}")

# 저장된 프로필 목록 확인
profiles = pm_advanced.list_profiles()
print("저장된 프로필들:", profiles)

# 특정 프로필 로드
loaded_profile = pm_advanced.load_profile('김데이터_데이터사이언티스트_v1')

# 프로필 업데이트 예시
loaded_profile['work_experience'].append({
    'company': '카카오',
    'position': 'Senior Data Scientist',
    # ... 새로운 경력 정보
})

# 업데이트된 프로필 저장 (벡터DB 자동 업데이트)
pm_advanced.save_profile(loaded_profile, '김데이터_데이터사이언티스트_v2')
```

## 3. 자기소개서 작성 프로세스

### 3.1 메인 프로그램 사용법

```bash
# 대화형 모드로 실행
python main.py
```

실행하면 다음과 같은 옵션들이 제공됩니다:

```
📋 데이터 입력 방법을 선택하세요:
1. 예시 데이터 사용 (빠른 테스트)
2. 기존 구조화된 프로필 사용
3. 새 구조화된 프로필 생성
4. 간단 정보 입력

⚙️ 시스템 설정:
- 문서 유형: resume / cover_letter
- 분석 깊이: low / medium / high
- 검색 모드: semantic / keyword / hybrid
```

### 3.2 코드를 통한 직접 실행

```python
import asyncio
from resumeagents.graph.resume_graph import ResumeAgentsGraph
from resumeagents.default_config import DEFAULT_CONFIG

# 설정 커스터마이징
config = DEFAULT_CONFIG.copy()
config.update({
    'analysis_depth': 'high',           # 분석 깊이
    'document_type': 'cover_letter',    # 문서 유형
    'web_search_enabled': True,         # 웹 검색 활성화
    'max_debate_rounds': 3,             # 토론 라운드
    'quality_threshold': 85             # 품질 임계값
})

# 지원 회사 및 직무 정보
company_name = "카카오"
job_title = "Senior Data Scientist"
job_description = """
[회사 소개]
카카오는 기술과 사람을 연결하여 더 나은 세상을 만드는 글로벌 IT 기업입니다.

[담당 업무]
- 대용량 사용자 데이터 분석 및 인사이트 도출
- 머신러닝 모델 개발, 검증 및 프로덕션 배포
- A/B 테스트 설계 및 실험 결과 분석
- 비즈니스 문제 해결을 위한 데이터 기반 솔루션 개발

[필수 요건]
- 컴퓨터공학, 통계학, 수학 등 관련 학과 학사 이상
- Python, R 등을 활용한 데이터 분석 경험 5년 이상
- 머신러닝 모델 개발 및 운영 경험 3년 이상
- SQL을 활용한 대용량 데이터 처리 경험

[우대 사항]
- TensorFlow, PyTorch 등 딥러닝 프레임워크 활용 경험
- 클라우드 플랫폼(AWS, GCP) 기반 ML 파이프라인 구축 경험
- 추천시스템, 검색 등 대규모 서비스 개발 경험
- 팀 리딩 또는 프로젝트 매니징 경험
"""

# 자기소개서 문항 설정
candidate_info = {
    "name": "김데이터",
    "profile_name": "김데이터_데이터사이언티스트_v2",
    "custom_questions": [
        {
            "question": "카카오에 지원한 동기와 입사 후 포부를 기술해 주십시오.",
            "type": "motivation",
            "char_limit": 1000,
            "char_limit_note": "공백 포함 1000자 이내"
        },
        {
            "question": "데이터 사이언스 관련 프로젝트 중 가장 도전적이었던 경험과 해결 과정을 구체적으로 설명해 주세요.",
            "type": "data_analysis",
            "char_limit": 1500,
            "char_limit_note": "공백 포함 1500자 이내"
        },
        {
            "question": "팀워크를 발휘하여 성과를 달성한 경험을 설명하고, 본인의 역할과 기여도를 기술해 주세요.",
            "type": "teamwork",
            "char_limit": 800,
            "char_limit_note": "공백 포함 800자 이내"
        },
        {
            "question": "카카오의 데이터 사이언티스트로서 어떤 가치를 창출하고 싶은지 기술해 주세요.",
            "type": "vision",
            "char_limit": 600,
            "char_limit_note": "공백 포함 600자 이내"
        }
    ]
}

# ResumeAgents 실행
async def run_resume_agents():
    ra = ResumeAgentsGraph(debug=True, config=config)
    
    final_state, decision = await ra.propagate(
        company_name=company_name,
        job_title=job_title,
        job_description=job_description,
        candidate_info=candidate_info
    )
    
    return final_state, decision

# 실행 및 결과 확인
final_state, decision = asyncio.run(run_resume_agents())

print(f"\n🎯 최종 결과")
print(f"품질 점수: {decision['quality_score']:.1f}/100")
print(f"결과 저장 위치: {final_state.output_dir}")
```

## 4. 고급 검색 기능 활용

### 4.1 기본 경험 검색

```python
# 관련 경험 검색
results = pm_advanced.find_relevant_experiences_for_question(
    profile_name='김데이터_데이터사이언티스트_v2',
    question='Python을 사용한 대용량 데이터 처리 경험이 있나요?',
    question_type='data_engineering',
    search_mode='hybrid',
    top_k=5
)

# 결과 분석
for i, result in enumerate(results, 1):
    print(f"\n{i}. 검색 결과:")
    print(f"   타입: {result['type']}")
    print(f"   관련도: {result['relevance_score']:.3f}")
    
    if 'semantic_score' in result:
        print(f"   의미적 점수: {result['semantic_score']:.3f}")
        print(f"   키워드 점수: {result['keyword_score']:.3f}")
    
    print(f"   내용 미리보기: {result['text'][:100]}...")
    print(f"   상세 데이터: {result['data']}")
```

### 4.2 데이터/AI 특화 질문 유형별 검색

```python
# 다양한 데이터/AI 질문 유형으로 검색
search_scenarios = [
    {
        'question': 'TensorFlow나 PyTorch를 사용한 딥러닝 모델 개발 경험',
        'type': 'machine_learning'
    },
    {
        'question': 'Apache Spark를 활용한 빅데이터 처리 프로젝트',
        'type': 'data_engineering'
    },
    {
        'question': 'Tableau이나 PowerBI로 만든 대시보드',
        'type': 'visualization'
    },
    {
        'question': '캐글 경진대회나 데이터 사이언스 대회 참여 경험',
        'type': 'kaggle'
    },
    {
        'question': 'A/B 테스트를 설계하고 분석한 경험',
        'type': 'ab_testing'
    }
]

for scenario in search_scenarios:
    print(f"\n🔍 검색: {scenario['question']}")
    print("-" * 60)
    
    results = pm_advanced.find_relevant_experiences_for_question(
        profile_name='김데이터_데이터사이언티스트_v2',
        question=scenario['question'],
        question_type=scenario['type'],
        search_mode='hybrid',
        top_k=3
    )
    
    if results:
        best_match = results[0]
        print(f"✅ 최고 매칭: [{best_match['type']}] 점수: {best_match['relevance_score']:.3f}")
        print(f"   {best_match['text'][:150]}...")
    else:
        print("❌ 관련 경험을 찾을 수 없습니다.")
```

### 4.3 검색 모드별 성능 비교

```python
def compare_search_modes(question, profile_name):
    """다른 검색 모드들의 성능을 비교"""
    modes = ['semantic', 'keyword', 'hybrid']
    
    print(f"🔍 질문: {question}")
    print("=" * 80)
    
    for mode in modes:
        results = pm_advanced.find_relevant_experiences_for_question(
            profile_name=profile_name,
            question=question,
            question_type='data_analysis',
            search_mode=mode,
            top_k=3
        )
        
        print(f"\n📊 {mode.upper()} 모드 결과:")
        if results:
            for i, result in enumerate(results[:2], 1):
                score_info = f"{result['relevance_score']:.3f}"
                if 'semantic_score' in result:
                    score_info += f" (의미:{result['semantic_score']:.3f} + 키워드:{result['keyword_score']:.3f})"
                
                print(f"   {i}. [{result['type']}] {score_info}")
                print(f"      {result['text'][:100]}...")
        else:
            print("   결과 없음")

# 검색 모드 비교 실행
compare_search_modes(
    "pandas와 numpy를 사용한 데이터 전처리 경험",
    "김데이터_데이터사이언티스트_v2"
)
```

## 5. 결과 분석 및 활용

### 5.1 생성된 가이드 분석

```python
# 결과 파일 로드
import json
from pathlib import Path

# 최신 결과 디렉토리 찾기
output_base = Path("outputs")
latest_output = max(output_base.glob("*"), key=lambda x: x.stat().st_mtime)

print(f"📁 결과 디렉토리: {latest_output}")

# 문항별 가이드 분석
with open(latest_output / "question_guides.json", 'r', encoding='utf-8') as f:
    question_guides = json.load(f)

for i, guide in enumerate(question_guides['guides'], 1):
    print(f"\n📝 문항 {i}: {guide['question']['question']}")
    print(f"   유형: {guide['question']['type']}")
    print(f"   글자수 제한: {guide['question'].get('char_limit', '제한 없음')}")
    print(f"   가이드 길이: {len(guide['guide'])}자")
    print(f"   핵심 포인트: {len(guide.get('key_points', []))}개")
    
    # 핵심 포인트 출력
    if 'key_points' in guide:
        for j, point in enumerate(guide['key_points'][:3], 1):
            print(f"      {j}. {point}")

# 경험 매칭 결과 분석
with open(latest_output / "experience_guides.json", 'r', encoding='utf-8') as f:
    experience_guides = json.load(f)

print(f"\n🔍 경험 매칭 통계:")
total_matches = sum(len(guide.get('relevant_experiences', [])) for guide in experience_guides['guides'])
print(f"   총 매칭된 경험: {total_matches}개")

for guide in experience_guides['guides']:
    experiences = guide.get('relevant_experiences', [])
    if experiences:
        avg_score = sum(exp['relevance_score'] for exp in experiences) / len(experiences)
        print(f"   문항별 평균 관련도: {avg_score:.3f}")
```

### 5.2 품질 점수 분석

```python
# 품질 분석 결과 로드
with open(latest_output / "analysis_results.json", 'r', encoding='utf-8') as f:
    analysis_results = json.load(f)

# 품질 점수 분석
quality_scores = analysis_results.get('quality_analysis', {})
print(f"\n📊 품질 분석 결과:")
print(f"   전체 품질 점수: {quality_scores.get('overall_score', 'N/A')}/100")

# 세부 품질 지표
quality_metrics = quality_scores.get('detailed_scores', {})
for metric, score in quality_metrics.items():
    print(f"   {metric}: {score}/100")

# 개선 제안사항
improvements = quality_scores.get('improvement_suggestions', [])
if improvements:
    print(f"\n💡 개선 제안사항:")
    for i, suggestion in enumerate(improvements, 1):
        print(f"   {i}. {suggestion}")
```

### 5.3 결과 내보내기

```python
def export_results_to_markdown(output_dir):
    """결과를 마크다운 형식으로 내보내기"""
    
    # 파일들 로드
    with open(output_dir / "question_guides.json", 'r', encoding='utf-8') as f:
        question_guides = json.load(f)
    
    # 마크다운 생성
    markdown_content = f"""# 자기소개서 작성 가이드

> 생성 일시: {question_guides['metadata']['created_at']}
> 회사: {question_guides['metadata']['company_name']}
> 직무: {question_guides['metadata']['job_title']}

"""
    
    for i, guide in enumerate(question_guides['guides'], 1):
        question = guide['question']
        markdown_content += f"""
## {i}. {question['question']}

**문항 유형:** {question['type']}  
**글자수 제한:** {question.get('char_limit', '제한 없음')}자

### 📝 작성 가이드

{guide['guide']}

### 🎯 핵심 포인트

"""
        
        for j, point in enumerate(guide.get('key_points', []), 1):
            markdown_content += f"{j}. {point}\n"
        
        markdown_content += "\n---\n"
    
    # 파일 저장
    output_file = output_dir / "자기소개서_작성_가이드.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"📄 마크다운 가이드 생성: {output_file}")

# 내보내기 실행
export_results_to_markdown(latest_output)
```

## 6. 문제 해결

### 6.1 일반적인 문제들

#### 문제 1: API 키 오류
```
Error: OpenAI API key not found
```

**해결방법:**
```bash
# 환경변수 확인
echo $OPENAI_API_KEY

# 환경변수 설정
export OPENAI_API_KEY="your_api_key_here"

# .env 파일 생성
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

#### 문제 2: 벡터DB 초기화 실패
```
Error: sentence-transformers not found
```

**해결방법:**
```bash
# 필요한 패키지 설치
pip install sentence-transformers faiss-cpu

# 또는 Light 모드 사용
pm = ProfileManager(mode='light')
```

#### 문제 3: 메모리 부족
```
Error: Out of memory
```

**해결방법:**
```python
# 분석 깊이를 낮춤
config['analysis_depth'] = 'low'

# 또는 Light 모드 사용
pm = ProfileManager(mode='light')
```

### 6.2 성능 최적화 팁

#### 6.2.1 검색 성능 향상
```python
# 캐시 활용을 위해 동일한 ProfileManager 인스턴스 재사용
pm = ProfileManager(mode='advanced')

# 검색 범위 제한
results = pm.find_relevant_experiences_for_question(
    profile_name='profile_name',
    question='question',
    question_type='specific_type',  # 구체적인 타입 지정
    top_k=3,  # 필요한 만큼만 검색
    search_mode='hybrid'
)
```

#### 6.2.2 프로필 관리 최적화
```python
# 프로필 업데이트 시 배치 처리
# 여러 변경사항을 한 번에 저장
profile['work_experience'].append(new_experience_1)
profile['work_experience'].append(new_experience_2)
profile['projects'].append(new_project)

# 한 번에 저장 (벡터DB도 한 번에 업데이트)
pm.save_profile(profile, 'profile_name')
```

### 6.3 디버깅 모드

```python
# 상세한 로그를 위한 디버그 모드
ra = ResumeAgentsGraph(debug=True, config=config)

# 또는 로깅 레벨 설정
import logging
logging.basicConfig(level=logging.DEBUG)
```

이 가이드를 통해 ResumeAgents의 모든 기능을 효과적으로 활용하실 수 있습니다. 추가 질문이나 문제가 있으시면 GitHub Issues를 통해 문의해 주세요! 
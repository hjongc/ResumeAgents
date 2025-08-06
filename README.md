# ResumeAgents: Multi-Agents LLM Resume & Job Application Framework

> 🎉 **ResumeAgents** - 취업 서류 작성에 특화된 멀티 에이전트 프레임워크
> 
> TradingAgents에서 영감을 받아 취업 준비생들을 위한 AI 기반 서류 작성 도구입니다.

## 🚀 주요 기능

### 🎯 자기소개서 문항별 맞춤 가이드
- **자동 문항 분석**: AI가 질문 유형을 자동으로 분류 (동기, 경험, 문제해결, 가치관, 기술 등)
- **글자수 최적화**: 한글 기준 글자수 제한에 맞춘 구조 및 내용 가이드
- **경험 매칭**: 벡터 검색을 통한 관련 경험 자동 추천

### 📊 하이브리드 프로필 관리
- **구조화된 프로필**: JSON 기반 체계적 이력 관리
- **벡터 데이터베이스**: 의미적 경험 검색 및 매칭
- **재사용성**: 한 번 작성한 프로필로 여러 기업 지원

### 🤖 멀티 에이전트 시스템
- **분석팀**: 기업, 채용공고, 시장 분석
- **평가팀**: 후보자, 문화, 트렌드 분석  
- **연구팀**: 강점/약점 연구 및 전략 수립
- **제작팀**: 문서 작성 및 품질 관리
- **가이드팀**: 문항별 맞춤 가이드 생성

## ResumeAgents Framework

ResumeAgents는 실제 취업 서류 작성 과정을 모방하는 멀티 에이전트 프레임워크입니다. 전문화된 LLM 기반 에이전트들이 협력하여: 기업 분석가, JD 분석가, 인재상 분석가, 트렌드 분석가, 경험 분석가, 서류 작성가, 품질 관리팀 등이 기업과 직무를 분석하고 최적의 서류를 작성합니다.

> ResumeAgents 프레임워크는 연구 목적으로 설계되었습니다. 실제 취업 성공률은 선택된 언어 모델, 모델 설정, 분석 기간, 데이터 품질 등 다양한 요인에 따라 달라질 수 있습니다.

### 분석팀 (Analysis Team)

* **기업 분석가 (Company Analyst)**: 기업의 재무상태, 성과 지표, 사업 모델을 평가하여 기업의 가치와 잠재적 위험 요소를 식별합니다.
* **JD 분석가 (Job Description Analyst)**: 채용공고를 분석하여 요구사항, 책임, 필요한 스킬을 파악하고 매칭도를 평가합니다.
* **시장 분석가 (Market Analyst)**: 최신 산업 동향, 기술 트렌드, 시장 변화를 모니터링하여 지원 전략에 반영합니다.

### 평가팀 (Evaluation Team)

* **후보자 분석가 (Candidate Analyst)**: 후보자의 경력, 기술, 성과를 분석하여 고유한 강점과 차별화 요소를 식별합니다.
* **문화 분석가 (Culture Analyst)**: 기업의 조직문화와 인재상을 분석하여 후보자와의 적합성을 평가합니다.
* **트렌드 분석가 (Trend Analyst)**: 산업 및 기술 트렌드를 분석하여 후보자의 미래 대응 능력을 평가합니다.

### 연구팀 (Research Team)

* 분석팀의 인사이트를 비판적으로 평가하는 강점 연구원과 약점 연구원으로 구성됩니다. 구조화된 토론을 통해 잠재적 기회와 위험을 균형있게 평가합니다.

### 제작팀 (Production Team)

* **문서 작성가 (Document Writer)**: 분석가들과 연구원들의 보고서를 종합하여 정보에 기반한 서류 작성 결정을 내립니다.
* **품질 관리자 (Quality Manager)**: 지속적으로 서류 품질을 평가하여 명확성, 일관성, 임팩트를 검토합니다.

### 가이드팀 (Guide Team)

* **문항 가이드 (Question Guide)**: 자기소개서 문항을 분석하고 작성 전략을 제공합니다.
* **경험 가이드 (Experience Guide)**: 관련 경험을 매칭하고 효과적인 표현 방법을 안내합니다.
* **작성 가이드 (Writing Guide)**: 최종적인 작성 구조와 전략을 제시합니다.

## 설치 및 사용법

### 설치

ResumeAgents 클론:

```bash
git clone https://github.com/hjongc/ResumeAgents.git
cd ResumeAgents
```

가상환경 생성:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

의존성 설치:

```bash
pip install -r requirements.txt

# 선택사항: 벡터DB 기능을 위한 추가 라이브러리
pip install sentence-transformers faiss-cpu
```

### 필요한 API

OpenAI API가 모든 에이전트에 필요합니다:

```bash
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
```

### 사용법

#### 1. 간단한 실행

```bash
python main.py
```

이 명령어를 실행하면 다음과 같은 옵션이 제공됩니다:

**📋 데이터 입력 방법:**
1. **예시 데이터**: 미리 준비된 샘플 데이터로 빠른 테스트
2. **기존 프로필 사용**: 저장된 구조화된 프로필 활용
3. **새 구조화된 프로필 생성**: 체계적인 프로필 생성 및 저장
4. **간단 입력**: 기본적인 정보만 입력

**⚙️ 시스템 설정:**
- 문서 유형 선택 (resume/cover_letter)
- 분석 깊이 설정 (low/medium/high)

#### 2. 구조화된 프로필 생성

```bash
python main.py
# 3번 선택: "새 구조화된 프로필 생성"
```

**프로필에 포함되는 정보:**
- 기본 정보 (이름, 연락처 등)
- 학력 정보 (학교, 전공, GPA, 수상 등)
- 경력 정보 (회사, 직책, 기간, 업무, 성과 등)
- 프로젝트 경험 (이름, 기간, 역할, 기술스택, 성과 등)
- 기술 스킬 (언어, 프레임워크, 도구, 숙련도 등)
- 자격증 및 어학 능력
- 수상 경력 및 관심사
- 커리어 목표 및 포트폴리오 링크

#### 3. 글자수 제한 기능

각 자기소개서 문항에 대해 글자수 제한을 설정할 수 있습니다:

```
💡 글자수 제한 안내: 한글 기준 (한글 1글자 = 영어 1글자 = 숫자 1글자 = 1자)
글자수 제한 (없으면 Enter, 예: 1000): 800
📏 예시: '안녕하세요. 저는 김개발입니다.' = 17자
```

**지원하는 기능:**
- 한글 표준 글자수 계산 (Python `len()` 기준)
- 글자수별 맞춤 작성 전략 제공
- 섹션별 글자수 배분 가이드
- 실시간 글자수 검증

#### 4. Python 코드에서 직접 사용

```python
import asyncio
from resumeagents.graph.resume_graph import ResumeAgentsGraph
from resumeagents.default_config import DEFAULT_CONFIG

# 기본 설정으로 초기화
ra = ResumeAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# 데이터 준비
company_name = "삼성전자"
job_title = "소프트웨어 엔지니어"
job_description = "채용공고 내용..."
candidate_info = {
    "name": "김개발",
    "education": "서울대학교 컴퓨터공학과 졸업",
    "experience": "경력 정보...",
    "skills": "Java, Python, Android",
    "projects": "프로젝트 정보...",
    "custom_questions": [
        {
            "question": "지원 동기와 입사 후 포부를 기술해 주십시오.",
            "type": "auto",
            "char_limit": 1000,
            "char_limit_note": "공백 포함 1000자 이내"
        }
    ]
}

# 분석 실행
final_state, decision = asyncio.run(ra.propagate(
    company_name=company_name,
    job_title=job_title,
    job_description=job_description,
    candidate_info=candidate_info
))

# 결과 확인
print(f"품질 점수: {decision['quality_score']:.1f}/100")
print("문항별 가이드:")
for guide in final_state.analysis_results["question_guides"]["guides"]:
    print(f"- {guide['question']['question']}")
    print(f"  가이드: {guide['guide'][:100]}...")
```

#### 5. 커스텀 설정 사용

```python
from resumeagents.graph.resume_graph import ResumeAgentsGraph
from resumeagents.default_config import DEFAULT_CONFIG

# 커스텀 설정 생성
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"  # 모델 설정
config["document_type"] = "cover_letter"  # 자기소개서 작성
config["analysis_depth"] = "high"  # 높은 분석 깊이
config["web_search_enabled"] = True  # 웹 검색 활성화

# 커스텀 설정으로 초기화
ra = ResumeAgentsGraph(debug=True, config=config)
```

## 🎯 출력 결과

### 문항별 가이드 생성
- **문항 분석**: 질문 의도, 평가 포인트, 문항 유형
- **작성 전략**: 구조 추천, 내용 배분, 핵심 포인트
- **경험 매칭**: 관련 경험 추천 및 활용 방안
- **글자수 최적화**: 제한에 맞춘 구체적인 작성 가이드

### 결과 저장
모든 분석 결과는 구조화된 디렉토리에 자동 저장됩니다:

```
outputs/
└── 삼성전자_소프트웨어엔지니어_20250127_143052/
    ├── analysis_results.json      # 전체 분석 결과
    ├── question_guides.json       # 문항별 가이드
    ├── experience_guides.json     # 경험별 가이드
    ├── writing_guides.json        # 작성 가이드
    ├── summary.txt               # 요약 정보
    └── README.md                 # 결과 설명
```

## ResumeAgents 패키지

### 구현 세부사항

LangGraph를 사용하여 ResumeAgents를 구축하여 유연성과 모듈성을 보장합니다. 실험에는 `gpt-4o`와 `gpt-4o-mini`를 사용하지만, 비용 절약을 위해 `gpt-4o-mini`를 기본으로 사용합니다.

### 설정 옵션

전체 설정 목록은 `resumeagents/default_config.py`에서 확인할 수 있습니다:

- **LLM 모델**: `deep_think_llm`, `quick_think_llm`
- **에이전트 설정**: `max_debate_rounds`, `analysis_depth`
- **문서 설정**: `document_type`, `language`, `format`
- **분석 설정**: `include_company_analysis`, `include_jd_analysis` 등
- **품질 설정**: `quality_threshold`, `max_revision_rounds`
- **웹 검색**: `web_search_enabled`

### 프로필 관리

#### 구조화된 프로필 (JSON)
- 체계적인 정보 관리
- 재사용 가능한 프로필
- 버전 관리 및 업데이트 추적

#### 벡터 데이터베이스 (선택사항)
- 의미적 경험 검색
- 자동 관련 경험 매칭
- 확장 가능한 검색 시스템

## 🛠️ 기술 스택

### 핵심 기술
- **LangGraph**: 멀티 에이전트 워크플로우 관리
- **LangChain**: LLM 통합 및 프롬프트 관리
- **OpenAI GPT-4o-mini**: 고성능 언어 모델 (비용 최적화)
- **Pydantic**: 데이터 검증 및 상태 관리

### 고급 기능 (선택사항)
- **FAISS**: 벡터 유사도 검색
- **Sentence Transformers**: 다국어 텍스트 임베딩
- **JSON Templates**: 구조화된 출력 관리

## 기여하기

커뮤니티의 기여를 환영합니다! 버그 수정, 문서 개선, 새로운 기능 제안 등 어떤 것이든 이 프로젝트를 더 나은 방향으로 만들어주는 여러분의 의견을 기다립니다.

## 라이선스

Apache-2.0 라이선스

## 인용

ResumeAgents가 도움이 되었다면 우리의 작업을 인용해주세요 :)

```
@misc{resumeagents2024,
      title={ResumeAgents: Multi-Agents LLM Resume & Job Application Framework}, 
      author={chai hyeon jong},
      year={2024},
      url={https://github.com/hjongc/ResumeAgents}, 
}
```

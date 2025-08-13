"""
Output Manager for ResumeAgents framework.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class OutputManager:
    """Manager for saving analysis results and guides."""
    
    def __init__(self, base_dir: str = "outputs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def create_output_directory(self, company_name: str, job_title: str) -> Path:
        """Create output directory based on company, job, and date."""
        # 현재 날짜
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 디렉토리명 생성 (특수문자 제거)
        safe_company = self._sanitize_filename(company_name)
        safe_job = self._sanitize_filename(job_title)
        
        dir_name = f"{safe_company}_{safe_job}_{current_date}"
        output_dir = self.base_dir / dir_name
        output_dir.mkdir(exist_ok=True)
        
        return output_dir
    
    def _sanitize_filename(self, filename: str) -> str:
        """파일명에서 사용할 수 없는 특수문자를 제거합니다."""
        import re
        # 특수문자 제거 및 공백을 언더스코어로 변경
        sanitized = re.sub(r'[^\w\s-]', '', filename)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized.strip('_')
    
    def save_analysis_results(self, output_dir: Path, analysis_results: Dict[str, Any]):
        """분석 결과를 JSON 파일로 저장합니다."""
        results_file = output_dir / "analysis_results.json"
        
        # JSON 직렬화 가능하도록 데이터 정리
        serializable_results = {}
        for key, value in analysis_results.items():
            if isinstance(value, dict) and "result" in value:
                serializable_results[key] = {
                    "analyst": value.get("analyst", ""),
                    "result": value.get("result", ""),
                    "timestamp": value.get("timestamp", ""),
                    "data_sources": value.get("data_sources", "")
                }
            else:
                serializable_results[key] = value
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        print(f"분석 결과 저장: {results_file}")
    
    def save_guides(self, output_dir: Path, guides_data: Dict[str, Any]):
        """가이드 결과를 개별 파일로 저장합니다."""
        guides_dir = output_dir / "guides"
        guides_dir.mkdir(exist_ok=True)
        
        for guide_type, guide_info in guides_data.items():
            if "guides" in guide_info:
                guides = guide_info["guides"]
                for i, guide_data in enumerate(guides):
                    q_obj = guide_data.get("question")
                    # question이 dict 또는 문자열인 경우 모두 처리
                    if isinstance(q_obj, dict):
                        question = q_obj.get("question", f"문항_{i+1}")
                    else:
                        question = q_obj if isinstance(q_obj, str) and q_obj else f"문항_{i+1}"
                    safe_question = self._sanitize_filename(question[:50])  # 질문명을 파일명으로 사용
                    
                    filename = f"{guide_type}_{i+1}_{safe_question}.json"
                    filepath = guides_dir / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(guide_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"가이드 저장: {filepath}")
    
    def save_cover_letters(self, output_dir: Path, cover_letter_result: Dict[str, Any]):
        """자기소개서(문항별 답변)를 별도 파일로 저장합니다.
        - 합본: cover_letter.txt (제목+본문 그대로)
        - 문항별: cover_letters/cover_q{n}_{질문요약}.txt (답변 본문만)
        """
        if not isinstance(cover_letter_result, dict):
            return
        # 합본 저장 (formatted_document 우선)
        formatted = cover_letter_result.get("formatted_document")
        if isinstance(formatted, str) and formatted.strip():
            combined_path = output_dir / "cover_letter.txt"
            with open(combined_path, 'w', encoding='utf-8') as f:
                f.write(formatted)
            print(f"자기소개서 합본 저장: {combined_path}")
        
        # 문항별 저장
        responses = cover_letter_result.get("responses", [])
        if isinstance(responses, list) and responses:
            cl_dir = output_dir / "cover_letters"
            cl_dir.mkdir(exist_ok=True)
            for idx, item in enumerate(responses, 1):
                if not isinstance(item, dict):
                    continue
                q_text = item.get("question") or f"문항_{idx}"
                safe_q = self._sanitize_filename(str(q_text)[:50])
                body = item.get("response", "")
                file_path = cl_dir / f"cover_q{idx}_{safe_q}.txt"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(body))
                print(f"자기소개서 문항 저장: {file_path}")
    
    def save_summary(self, output_dir: Path, final_state, decision: Dict[str, Any]):
        """최종 요약 정보를 저장합니다."""
        def _shorten(text: str, limit: int = 200) -> str:
            s = str(text)
            return (s[:limit] + "...") if len(s) > limit else s

        analysis_summary: Dict[str, Any] = {}
        for key, value in final_state.analysis_results.items():
            # 표준 result 필드 선호
            if isinstance(value, dict):
                if "result" in value:
                    analysis_summary[key] = _shorten(value.get("result", ""))
                elif "formatted_document" in value:
                    analysis_summary[key] = _shorten(value.get("formatted_document", ""))
                else:
                    # dict 전체를 요약 문자열로 직렬화
                    try:
                        analysis_summary[key] = _shorten(json.dumps(value, ensure_ascii=False))
                    except Exception:
                        analysis_summary[key] = _shorten(str(value))
            else:
                # 문자열/숫자 등 단순 타입
                analysis_summary[key] = _shorten(value)

        summary = {
            "company_name": final_state.company_name,
            "job_title": final_state.job_title,
            "analysis_date": datetime.now().isoformat(),
            "quality_score": decision.get("quality_score", 0.0),
            "total_questions": len(final_state.candidate_info.get("custom_questions", [])),
            "analysis_summary": analysis_summary,
        }
        
        summary_file = output_dir / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"요약 정보 저장: {summary_file}")
    
    def create_readme(self, output_dir: Path, company_name: str, job_title: str):
        """README 파일을 생성합니다."""
        readme_content = f"""# ResumeAgents 분석 결과

## 분석 정보
- **기업명**: {company_name}
- **직무**: {job_title}
- **분석 날짜**: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")}

## 파일 구조
```
{output_dir.name}/
├── analysis_results.json    # 전체 분석 결과
├── summary.json             # 요약 정보
├── cover_letter.txt         # 자기소개서 합본(문항별 답변 포함)
├── cover_letters/           # 문항별 자기소개서 텍스트
└── guides/                  # 가이드 파일들
    ├── question_guides_*.json
    ├── experience_guides_*.json
    └── writing_guides_*.json
```

## 사용 방법
1. `cover_letter.txt`: 문항별 답변이 하나의 문서로 합쳐진 자기소개서
2. `cover_letters/`: 각 문항별 개별 답변 텍스트
3. `analysis_results.json`: 전체 분석 결과(내부용)
4. `summary.json`: 핵심 정보 요약
5. `guides/`: 문항별 상세 가이드

## 주의사항
- 모든 파일은 UTF-8 인코딩으로 저장되었습니다
- JSON 파일은 가독성을 위해 들여쓰기가 적용되었습니다
"""
        
        readme_file = output_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"README 파일 생성: {readme_file}")
    
    def save_all_results(self, company_name: str, job_title: str, final_state, decision: Dict[str, Any]):
        """모든 결과를 저장합니다."""
        output_dir = self.create_output_directory(company_name, job_title)
        
        # 분석 결과 저장
        self.save_analysis_results(output_dir, final_state.analysis_results)
        
        # 가이드 결과 저장
        guides_data = {}
        for key, value in final_state.analysis_results.items():
            if "guides" in key:
                guides_data[key] = value
        
        if guides_data:
            self.save_guides(output_dir, guides_data)
        
        # 자기소개서 별도 저장 (합본 + 문항별)
        cover_letter_result = final_state.analysis_results.get("cover_letter_writing")
        if cover_letter_result:
            self.save_cover_letters(output_dir, cover_letter_result)
        
        # 요약 정보 저장
        self.save_summary(output_dir, final_state, decision)
        
        # README 생성
        self.create_readme(output_dir, company_name, job_title)
        
        print(f"\n모든 결과가 저장되었습니다: {output_dir}")
        return output_dir 
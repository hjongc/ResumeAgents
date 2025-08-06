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
                    question = guide_data.get("question", {}).get("question", f"문항_{i+1}")
                    safe_question = self._sanitize_filename(question[:50])  # 질문명을 파일명으로 사용
                    
                    filename = f"{guide_type}_{i+1}_{safe_question}.json"
                    filepath = guides_dir / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(guide_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"가이드 저장: {filepath}")
    
    def save_summary(self, output_dir: Path, final_state, decision: Dict[str, Any]):
        """최종 요약 정보를 저장합니다."""
        summary = {
            "company_name": final_state.company_name,
            "job_title": final_state.job_title,
            "analysis_date": datetime.now().isoformat(),
            "quality_score": decision.get("quality_score", 0.0),
            "total_questions": len(final_state.candidate_info.get("custom_questions", [])),
            "analysis_summary": {
                key: value.get("result", "")[:200] + "..." if len(str(value.get("result", ""))) > 200 
                else value.get("result", "")
                for key, value in final_state.analysis_results.items()
            }
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
├── summary.json            # 요약 정보
└── guides/                 # 가이드 파일들
    ├── question_guides/     # 문항 가이드
    ├── experience_guides/   # 경험 가이드
    └── writing_guides/     # 작성 가이드
```

## 사용 방법
1. `analysis_results.json`: 전체 분석 결과를 확인
2. `summary.json`: 핵심 정보 요약
3. `guides/` 폴더: 각 문항별 상세 가이드

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
        
        # 요약 정보 저장
        self.save_summary(output_dir, final_state, decision)
        
        # README 생성
        self.create_readme(output_dir, company_name, job_title)
        
        print(f"\n모든 결과가 저장되었습니다: {output_dir}")
        return output_dir 
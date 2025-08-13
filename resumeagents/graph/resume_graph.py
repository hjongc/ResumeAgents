"""
ResumeAgents Graph Implementation with Stage-wise Evaluation and Revision System.
통합 벡터DB를 활용한 에이전트별 맞춤형 컨텍스트 제공 시스템.
"""

import asyncio
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from ..agents.base_agent import AgentState
from ..agents.analysis import CompanyAnalyst, JDAnalyst, MarketAnalyst
from ..agents.matching import CandidateAnalyst, CultureAnalyst, TrendAnalyst
from ..agents.strategy import StrengthResearcher, WeaknessResearcher
from ..agents.production import ResumeWriter, CoverLetterWriter, QualityManager
from ..agents.guides import QuestionGuide, ExperienceGuide, WritingGuide
from ..agents.evaluators import (
    AnalysisEvaluator, MatchingEvaluator, StrategyEvaluator, 
    GuideEvaluator, ProductionEvaluator
)
from ..utils import get_model_for_agent, supports_temperature

# 통합 벡터DB import
try:
    from ..utils.unified_vectordb import UnifiedVectorDB
    UNIFIED_VECTORDB_AVAILABLE = True
except ImportError:
    UNIFIED_VECTORDB_AVAILABLE = False


class ResumeAgentsGraph:
    """Main graph for ResumeAgents framework with stage-wise evaluation and unified vector DB integration."""
    
    def __init__(self, debug: bool = False, config: Optional[Dict[str, Any]] = None):
        
        self.debug = debug  # debug 속성을 먼저 정의
        self.config = config or {}
        
        # 통합 벡터DB 초기화
        self.unified_vectordb = None
        if UNIFIED_VECTORDB_AVAILABLE:
            try:
                self.unified_vectordb = UnifiedVectorDB()
                if debug:
                    print("✅ 통합 벡터DB 활성화 - 에이전트별 맞춤형 컨텍스트 제공")
            except Exception as e:
                if debug:
                    print(f"⚠️  통합 벡터DB 초기화 실패: {e}")
        elif debug:
            print("ℹ️  통합 벡터DB 라이브러리 없음 - 기본 프로필 정보만 사용")
        
        # Research depth에 따른 모델 선택
        research_depth = self.config.get("research_depth", "MEDIUM")
        quick_model = self.config.get("quick_think_model", "gpt-4o-mini")
        deep_model = self.config.get("deep_think_model", "o4-mini")
        web_search_model = self.config.get("web_search_model", "gpt-4o-mini")
        
        # Initialize LLMs with conditional temperature support
        # Quick Think model (웹 검색 지원 모델)
        quick_llm_config = {
            "model": quick_model,
            "max_tokens": self.config.get("max_tokens", 4000)
        }
        if supports_temperature(quick_model):
            quick_llm_config["temperature"] = self.config.get("temperature", 0.7)
        
        self.quick_think_llm = ChatOpenAI(**quick_llm_config)
        
        # Deep Think model (reasoning 모델)
        deep_llm_config = {
            "model": deep_model,
            "max_tokens": self.config.get("max_tokens", 4000)
        }
        if supports_temperature(deep_model):
            deep_llm_config["temperature"] = self.config.get("temperature", 0.7)
        
        self.deep_think_llm = ChatOpenAI(**deep_llm_config)
        
        # Web Search model (웹 검색 전용 모델)
        web_search_llm_config = {
            "model": web_search_model,
            "max_tokens": self.config.get("web_search_max_tokens", 3000)
        }
        if supports_temperature(web_search_model):
            web_search_llm_config["temperature"] = self.config.get("temperature", 0.7)
        
        self.web_search_llm = ChatOpenAI(**web_search_llm_config)
        
        # Research depth 정보 출력
        if self.debug:
            print(f"Research Depth: {research_depth}")
            print(f"Quick Think Model: {quick_model}")
            print(f"Deep Think Model: {deep_model}")
            print(f"Web Search Model: {web_search_model}")
            print(f"Max Tokens: {self.config.get('max_tokens', 4000)}")
            print(f"Max Revision Rounds: {self.config.get('max_revision_rounds', 2)}")
        
        # Initialize agents and evaluators
        self.agents = self._initialize_agents()
        self.evaluators = self._initialize_evaluators()
        
        # Build the graph
        self.graph = self._build_graph()

    def log(self, message: str):
        """Log message if debug is enabled."""
        if self.debug:
            print(f"[GRAPH] {message}")
    
    def _initialize_evaluators(self) -> Dict[str, Any]:
        """평가자들을 초기화합니다."""
        from ..utils import get_research_depth_config
        
        # Research depth 설정 가져오기
        research_config = get_research_depth_config(self.config.get("research_depth", "MEDIUM"))
        
        # 평가용 모델 설정 (depth별)
        eval_llm_config = {
            "model": research_config.get("evaluator_model", "gpt-4o-mini"),
            "max_tokens": research_config.get("evaluator_max_tokens", 2000)
        }
        
        # Temperature 지원 여부 확인 후 추가
        evaluator_model = research_config.get("evaluator_model", "gpt-4o-mini")
        if supports_temperature(evaluator_model):
            eval_llm_config["temperature"] = research_config.get("evaluator_temperature", 0.3)
        
        eval_llm = ChatOpenAI(**eval_llm_config)
        
        if self.debug:
            print(f"[DEBUG] Evaluator Model: {evaluator_model}")
            print(f"[DEBUG] Evaluator Max Tokens: {research_config.get('evaluator_max_tokens', 2000)}")
            print(f"[DEBUG] Evaluator Temperature: {research_config.get('evaluator_temperature', 0.3)}")
        
        return {
            "analysis_evaluator": AnalysisEvaluator(llm=eval_llm, config=self.config),
            "matching_evaluator": MatchingEvaluator(llm=eval_llm, config=self.config),
            "strategy_evaluator": StrategyEvaluator(llm=eval_llm, config=self.config),
            "guide_evaluator": GuideEvaluator(llm=eval_llm, config=self.config),
            "production_evaluator": ProductionEvaluator(llm=eval_llm, config=self.config)
        }
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents with appropriate models for each stage."""
        from ..utils import get_research_depth_config
        
        # Get research depth configuration
        research_config = get_research_depth_config(self.config.get("research_depth", "MEDIUM"))
        
        agents = {}
        
        # Analysis agents
        agents["company_analyst"] = CompanyAnalyst(
            llm=self._get_llm_for_agent("company_analysis", research_config),
            config=self.config
        )
        agents["jd_analyst"] = JDAnalyst(
            llm=self._get_llm_for_agent("jd_analysis", research_config),
            config=self.config
        )
        agents["market_analyst"] = MarketAnalyst(
            llm=self._get_llm_for_agent("market_analysis", research_config),
            config=self.config
        )
        
        # Evaluation agents
        agents["candidate_analyst"] = CandidateAnalyst(
            llm=self._get_llm_for_agent("candidate_analysis", research_config),
            config=self.config
        )
        agents["culture_analyst"] = CultureAnalyst(
            llm=self._get_llm_for_agent("culture_analysis", research_config),
            config=self.config
        )
        agents["trend_analyst"] = TrendAnalyst(
            llm=self._get_llm_for_agent("trend_analysis", research_config),
            config=self.config
        )
        
        # Research agents
        agents["strength_researcher"] = StrengthResearcher(
            llm=self._get_llm_for_agent("strength_research", research_config),
            config=self.config
        )
        agents["weakness_researcher"] = WeaknessResearcher(
            llm=self._get_llm_for_agent("weakness_research", research_config),
            config=self.config
        )
        
        # Guide agents
        agents["question_guide"] = QuestionGuide(
            llm=self._get_llm_for_agent("question_guide", research_config),
            config=self.config
        )
        agents["experience_guide"] = ExperienceGuide(
            llm=self._get_llm_for_agent("experience_guide", research_config),
            config=self.config
        )
        agents["writing_guide"] = WritingGuide(
            llm=self._get_llm_for_agent("writing_guide", research_config),
            config=self.config
        )
        
        # Production agents
        agents["document_writer"] = ResumeWriter(
            llm=self._get_llm_for_agent("document_writing", research_config),
            config=self.config
        )
        agents["cover_letter_writer"] = CoverLetterWriter(
            llm=self._get_llm_for_agent("cover_letter_writing", research_config),
            config=self.config
        )
        agents["quality_manager"] = QualityManager(
            llm=self._get_llm_for_agent("quality_management", research_config),
            config=self.config
        )
        
        return agents
    
    def _get_llm_for_agent(self, agent_name: str, research_config: dict) -> ChatOpenAI:
        """Get appropriate LLM for specific agent based on research depth configuration."""
        from ..utils import get_model_for_agent

        # 에이전트별 최적 모델 선택
        model_name = get_model_for_agent(agent_name, research_config)

        # LLM 설정 구성
        llm_config = {
            "model": model_name,
            "max_tokens": research_config.get("max_tokens", 4000)
        }

        # Temperature 지원 여부 확인 후 추가
        if supports_temperature(model_name):
            llm_config["temperature"] = self.config.get("temperature", 0.7)

        if self.debug:
            print(f"[DEBUG] {agent_name} -> {model_name}")

        return ChatOpenAI(**llm_config)
    
    def _create_stage_evaluation_node(self, stage_name: str, team_name: str, evaluator_key: str):
        """팀별 평가 노드를 생성합니다."""
        async def team_evaluation(state: AgentState) -> AgentState:
            """특정 팀의 결과를 평가합니다."""
            if self.debug:
                print(f"Running {stage_name}_evaluation...")

            # 해당 팀의 모든 결과를 수집
            team_agents = self._get_team_agents(team_name)
            team_results = {}
            
            for agent_key in team_agents:
                agent_result_key = agent_key.replace("_analyst", "_analysis").replace("_researcher", "_research")
                # 가이드 에이전트들의 특별한 키 매핑 처리
                if agent_key == "question_guide":
                    agent_result_key = "question_guides"
                elif agent_key == "experience_guide":
                    agent_result_key = "experience_guides"
                elif agent_key == "writing_guide":
                    agent_result_key = "writing_guides"
                # production 에이전트들의 특별한 키 매핑 처리
                elif agent_key == "document_writer":
                    agent_result_key = "resume_writing"  # ResumeWriter로 변경됨에 따라 수정
                elif agent_key == "cover_letter_writer":
                    agent_result_key = "cover_letter_writing"
                elif agent_key == "quality_manager":
                    agent_result_key = "quality_assessment"
                
                if hasattr(state, 'analysis_results') and agent_result_key in state.analysis_results:
                    team_results[agent_result_key] = state.analysis_results[agent_result_key]

            if not team_results:
                self.log(f"⚠️ {stage_name} 팀 결과 없음 - 평가 스킵")
                return state

            # 평가자 실행 (팀 전체 결과를 평가)
            evaluator = self.evaluators[evaluator_key]
            needs_revision, feedback, scores = await evaluator.evaluate_stage(
                state, team_results, team_name
            )

            # 리비전이 필요한 경우 피드백 저장
            if needs_revision:
                revision_key = f"{team_name}_revision_feedback"
                state.analysis_results[revision_key] = {
                    "feedback": feedback,
                    "scores": scores,
                    "needs_revision": True,
                    "evaluator": evaluator.name,
                    "timestamp": "2024-01-15"
                }

                # 리비전 카운터 초기화
                revision_count_key = f"{team_name}_revision_count"
                if revision_count_key not in state.analysis_results:
                    state.analysis_results[revision_count_key] = 0
                    
                self.log(f"❌ {stage_name} 팀 평가 미달 - 리비전 필요")
            else:
                self.log(f"✅ {stage_name} 팀 평가 통과")

            return state

        return team_evaluation
    
    def _create_stage_revision_node(self, team_name: str):
        """팀별 리비전 노드를 생성합니다."""
        async def team_revision(state: AgentState) -> AgentState:
            """특정 팀을 리비전합니다."""
            if self.debug:
                print(f"Running {team_name}_revision...")

            # 리비전 피드백 가져오기
            revision_key = f"{team_name}_revision_feedback"
            revision_data = state.analysis_results.get(revision_key, {})
            feedback = revision_data.get("feedback", [])

            # 리비전 카운터 증가
            revision_count_key = f"{team_name}_revision_count"
            current_count = state.analysis_results.get(revision_count_key, 0)
            state.analysis_results[revision_count_key] = current_count + 1

            # 팀별 에이전트 매핑
            team_agents = self._get_team_agents(team_name)
            
            # 팀의 모든 에이전트를 다시 실행
            for agent_key in team_agents:
                if agent_key in self.agents:
                    agent = self.agents[agent_key]
                    
                    # 에이전트의 analyze 메서드에 피드백 전달
                    original_analyze = agent.analyze

                    async def analyze_with_feedback(state_param):
                        # 피드백을 state에 임시 저장
                        if feedback:
                            state_param.revision_feedback = feedback
                            state_param.is_revision = True
                            state_param.revision_count = current_count + 1

                        return await original_analyze(state_param)

                    agent.analyze = analyze_with_feedback
                    result_state = await agent.analyze(state)
                    agent.analyze = original_analyze  # 원래 메서드로 복원
                    
                    state = result_state

            self.log(f"🔄 {team_name} 리비전 완료 (시도 {current_count + 1})")
            return state

        return team_revision
    
    def _get_team_agents(self, team_name: str) -> list:
        """팀별 에이전트 목록을 반환합니다."""
        team_mapping = {
            "analysis_team": ["company_analyst", "market_analyst", "jd_analyst"],
            "matching_team": ["candidate_analyst", "culture_analyst", "trend_analyst"],
            "strategy_team": ["strength_researcher", "weakness_researcher"],
            "guide_team": ["question_guide", "experience_guide", "writing_guide"],
            "production_team": ["document_writer", "cover_letter_writer", "quality_manager"]
        }
        return team_mapping.get(team_name, [])

    def _should_revise_stage(self, team_name: str):
        """팀별 리비전 필요성을 판단합니다."""
        def should_revise(state: AgentState) -> str:
            revision_key = f"{team_name}_revision_feedback"
            revision_data = state.analysis_results.get(revision_key, {})
            needs_revision = revision_data.get("needs_revision", False)

            # 최대 리비전 횟수 확인
            revision_count_key = f"{team_name}_revision_count"
            current_count = state.analysis_results.get(revision_count_key, 0)
            max_revisions = self.config.get("max_revision_rounds", 2)

            if needs_revision and current_count < max_revisions:
                return "revise"
            else:
                return "continue"

        return should_revise
    
    def _build_graph(self) -> StateGraph:
        """전략 문서에 따른 순차적 워크플로우 그래프를 구성합니다."""
        graph = StateGraph(AgentState)
        
        # === Phase 1: Analysis Team (External Information Analysis) ===
        # Company → Market → JD 순서로 컨텍스트 누적
        graph.add_node("company_analysis", self._company_analysis_node)
        graph.add_node("market_analysis", self.agents["market_analyst"].analyze)
        graph.add_node("jd_analysis", self._jd_analysis_node)
        
        # Analysis Phase Evaluation
        graph.add_node("analysis_evaluation", self._create_stage_evaluation_node("analysis", "analysis_team", "analysis_evaluator"))
        graph.add_node("analysis_revision", self._create_stage_revision_node("analysis_team"))
        
        # === Phase 2: Matching Team (Candidate-Company Matching) ===
        graph.add_node("candidate_analysis", self._candidate_analysis_node)
        graph.add_node("culture_analysis", self.agents["culture_analyst"].analyze)
        graph.add_node("trend_analysis", self.agents["trend_analyst"].analyze)
        
        # Matching Phase Evaluation
        graph.add_node("matching_evaluation", self._create_stage_evaluation_node("matching", "matching_team", "matching_evaluator"))
        graph.add_node("matching_revision", self._create_stage_revision_node("matching_team"))
        
        # === Phase 3: Strategy Team (Strategic Positioning) ===
        graph.add_node("strength_research", self.agents["strength_researcher"].analyze)
        graph.add_node("weakness_research", self.agents["weakness_researcher"].analyze)
        
        # Strategy Phase Evaluation
        graph.add_node("strategy_evaluation", self._create_stage_evaluation_node("strategy", "strategy_team", "strategy_evaluator"))
        graph.add_node("strategy_revision", self._create_stage_revision_node("strategy_team"))
        
        # === Phase 4: Guide Team (Writing Guidance) ===
        graph.add_node("question_guide", self._question_guide_node)
        graph.add_node("experience_guide", self.agents["experience_guide"].analyze)
        graph.add_node("writing_guide", self.agents["writing_guide"].analyze)
        
        # Guide Phase Evaluation
        graph.add_node("guide_evaluation", self._create_stage_evaluation_node("guide", "guide_team", "guide_evaluator"))
        graph.add_node("guide_revision", self._create_stage_revision_node("guide_team"))
        
        # === Phase 5: Production Team (Document Creation) ===
        graph.add_node("resume_writing", self.agents["document_writer"].analyze)
        graph.add_node("cover_letter_writing", self.agents["cover_letter_writer"].analyze)
        graph.add_node("quality_management", self.agents["quality_manager"].analyze)
        
        # Production Phase Evaluation
        graph.add_node("production_evaluation", self._create_stage_evaluation_node("production", "production_team", "production_evaluator"))
        graph.add_node("production_revision", self._create_stage_revision_node("production_team"))
        
        # === 워크플로우 연결 ===
        # Phase 1: Analysis Team (순차 실행 + 평가)
        graph.add_edge("company_analysis", "market_analysis")
        graph.add_edge("market_analysis", "jd_analysis")
        graph.add_edge("jd_analysis", "analysis_evaluation")
        
        # Analysis evaluation with revision loop
        graph.add_conditional_edges(
            "analysis_evaluation",
            self._should_revise_stage("analysis_team"),
            {
                "revise": "analysis_revision",
                "continue": "candidate_analysis"
            }
        )
        graph.add_edge("analysis_revision", "analysis_evaluation")
        
        # Phase 2: Matching Team (순차 실행 + 평가)
        graph.add_edge("candidate_analysis", "culture_analysis")
        graph.add_edge("culture_analysis", "trend_analysis")
        graph.add_edge("trend_analysis", "matching_evaluation")
        
        # Matching evaluation with revision loop
        graph.add_conditional_edges(
            "matching_evaluation",
            self._should_revise_stage("matching_team"),
            {
                "revise": "matching_revision",
                "continue": "strength_research"
            }
        )
        graph.add_edge("matching_revision", "matching_evaluation")
        
        # Phase 3: Strategy Team (순차 실행 + 평가)
        graph.add_edge("strength_research", "weakness_research")
        graph.add_edge("weakness_research", "strategy_evaluation")
        
        # Strategy evaluation with revision loop
        graph.add_conditional_edges(
            "strategy_evaluation",
            self._should_revise_stage("strategy_team"),
            {
                "revise": "strategy_revision",
                "continue": "question_guide"
            }
        )
        graph.add_edge("strategy_revision", "strategy_evaluation")
        
        # Phase 4: Guide Team (순차 실행 + 평가)
        graph.add_edge("question_guide", "experience_guide")
        graph.add_edge("experience_guide", "writing_guide")
        graph.add_edge("writing_guide", "guide_evaluation")
        
        # Guide evaluation with revision loop
        graph.add_conditional_edges(
            "guide_evaluation",
            self._should_revise_stage("guide_team"),
            {
                "revise": "guide_revision",
                "continue": "workflow_decision"
            }
        )
        graph.add_edge("guide_revision", "guide_evaluation")
        
        # === User Selection Workflow Decision ===
        graph.add_node("workflow_decision", lambda state: state)  # Pass-through node
        graph.add_conditional_edges(
            "workflow_decision",
            self._decide_workflow,
            {
                "guide_only": END,
                "create_document": "production_start"
            }
        )
        
        # Production entry: decide start node based on config
        graph.add_node("production_start", lambda state: state)
        graph.add_conditional_edges(
            "production_start",
            self._decide_production_entry,
            {
                "resume": "resume_writing",
                "cover_letter": "cover_letter_writing"
            }
        )
        
        # Phase 5: Production Team (순차 실행 + 평가)
        graph.add_edge("resume_writing", "cover_letter_writing")
        graph.add_edge("cover_letter_writing", "quality_management")
        graph.add_edge("quality_management", "production_evaluation")
        
        # Production evaluation with revision loop
        graph.add_conditional_edges(
            "production_evaluation",
            self._should_revise_stage("production_team"),
            {
                "revise": "production_revision",
                "continue": END
            }
        )
        graph.add_edge("production_revision", "production_evaluation")
        
        # 시작점 설정
        graph.set_entry_point("company_analysis")
        
        return graph.compile()
    
    def _decide_workflow(self, state: AgentState) -> str:
        """사용자 선택에 따라 워크플로우를 결정합니다."""
        workflow_type = self.config.get("workflow_type", "both")
        
        if workflow_type == "guide_only":
            self.log("📋 Guide-Only 워크플로우 선택")
            return "guide_only"
        else:
            self.log("📄 Document Creation 워크플로우 선택")
            return "create_document"
    
    def _decide_production_entry(self, state: AgentState) -> str:
        """Decide whether to start production at resume or cover letter based on document_type.
        - resume: 이력서만 필요하거나 먼저 생성할 때
        - cover_letter: 문항 답변만 생성하고 싶은 경우
        """
        doc_type = self.config.get("document_type", "resume").lower()
        if doc_type == "cover_letter":
            self.log("🧭 Production entry: cover_letter_writing")
            return "cover_letter"
        else:
            self.log("🧭 Production entry: resume_writing")
            return "resume"

    async def run(self, initial_state: AgentState) -> AgentState:
        """그래프를 실행합니다."""
        self.log("🚀 ResumeAgents 워크플로우 시작")
        
        try:
            result = await self.graph.ainvoke(initial_state)
            self.log("✅ 워크플로우 완료")
            return result
        except Exception as e:
            self.log(f"❌ 워크플로우 실행 중 오류: {e}")
            raise 

    def _get_agent_context(self, state: AgentState, agent_type: str, task_context: str = None) -> Dict[str, Any]:
        """
        에이전트별 맞춤형 컨텍스트 생성 (DEVELOPMENT_STRATEGY.md 준수)
        
        Args:
            state: 현재 상태
            agent_type: 에이전트 유형
            task_context: 작업 컨텍스트
        
        Returns:
            에이전트별 맞춤형 컨텍스트
        """
        # 프로필 이름 추출
        profile_name = state.candidate_info.get("name", "default_profile")
        
        # 통합 벡터DB 사용 가능한 경우
        if self.unified_vectordb:
            try:
                context = self.unified_vectordb.get_agent_context(
                    profile_name=profile_name,
                    agent_type=agent_type,
                    task_context=task_context
                )
                
                # 기본 상태 정보도 포함
                context.update({
                    "company_name": state.company_name,
                    "job_title": state.job_title,
                    "job_description": state.job_description,
                    "analysis_results": state.analysis_results
                })
                
                return context
                
            except Exception as e:
                if self.debug:
                    print(f"⚠️  벡터DB 컨텍스트 생성 실패: {e}")
        
        # 폴백: 기본 candidate_info 사용
        return {
            "profile_name": profile_name,
            "agent_type": agent_type,
            "task_context": task_context,
            "candidate_info": state.candidate_info,
            "company_name": state.company_name,
            "job_title": state.job_title,
            "job_description": state.job_description,
            "analysis_results": state.analysis_results,
            "vectordb_enabled": False
        }

    # 에이전트 노드들을 컨텍스트 기반으로 수정
    async def _company_analysis_node(self, state: AgentState) -> AgentState:
        """회사 분석 노드 - 통합 벡터DB 컨텍스트 활용"""
        if self.debug:
            print("🏢 회사 분석 시작")
        
        # 에이전트별 맞춤 컨텍스트 생성
        context = self._get_agent_context(
            state=state,
            agent_type="company_analyst",
            task_context="회사 분석에 필요한 경험과 목표"
        )
        
        # 컨텍스트를 state에 임시 저장
        state.agent_context = context
        
        # 회사 분석 실행
        result_state = await self.agents["company_analyst"].analyze(state)
        
        # 임시 컨텍스트 제거
        if hasattr(result_state, 'agent_context'):
            delattr(result_state, 'agent_context')
        
        return result_state

    async def _jd_analysis_node(self, state: AgentState) -> AgentState:
        """JD 분석 노드 - 통합 벡터DB 컨텍스트 활용"""
        if self.debug:
            print("📋 JD 분석 시작")
        
        # 에이전트별 맞춤 컨텍스트 생성
        context = self._get_agent_context(
            state=state,
            agent_type="jd_analyst",
            task_context="직무 요구사항에 맞는 기술과 경험"
        )
        
        state.agent_context = context
        result_state = await self.agents["jd_analyst"].analyze(state)
        
        if hasattr(result_state, 'agent_context'):
            delattr(result_state, 'agent_context')
        
        return result_state

    async def _candidate_analysis_node(self, state: AgentState) -> AgentState:
        """지원자 분석 노드 - 통합 벡터DB 컨텍스트 활용"""
        if self.debug:
            print("👤 지원자 분석 시작")
        
        # 에이전트별 맞춤 컨텍스트 생성
        context = self._get_agent_context(
            state=state,
            agent_type="candidate_analyst",
            task_context="지원자 경험과 스킬 분석"
        )
        
        state.agent_context = context
        result_state = await self.agents["candidate_analyst"].analyze(state)
        
        if hasattr(result_state, 'agent_context'):
            delattr(result_state, 'agent_context')
        
        return result_state

    async def _question_guide_node(self, state: AgentState) -> AgentState:
        """질문 가이드 노드 - 통합 벡터DB 컨텍스트 활용"""
        if self.debug:
            print("❓ 질문 가이드 분석 시작")
        
        # 질문별 맞춤 컨텍스트 생성
        questions = state.candidate_info.get("custom_questions", [])
        question_context = " ".join([q.get("question", "") for q in questions])
        
        context = self._get_agent_context(
            state=state,
            agent_type="question_guide",
            task_context=f"자기소개서 질문 분석: {question_context}"
        )
        
        state.agent_context = context
        result_state = await self.agents["question_guide"].analyze(state)
        
        if hasattr(result_state, 'agent_context'):
            delattr(result_state, 'agent_context')
        
        return result_state 
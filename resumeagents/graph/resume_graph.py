"""
Main graph for ResumeAgents framework.
"""

import asyncio
from typing import Dict, Any, Tuple, Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph import START

from ..agents.base_agent import AgentState
from ..agents import (
    CompanyAnalyst,
    JDAnalyst,
    MarketAnalyst,
    CandidateAnalyst,
    CultureAnalyst,
    TrendAnalyst,
    StrengthResearcher,
    WeaknessResearcher,
    DocumentWriter,
    QualityManager,
    QuestionGuideAgent,
    ExperienceGuideAgent,
    WritingGuideAgent,
)


class ResumeAgentsGraph:
    """Main graph for ResumeAgents framework."""
    
    def __init__(self, debug: bool = False, config: Optional[Dict[str, Any]] = None):
        self.debug = debug
        self.config = config or {}
        
        # Initialize LLMs
        self.deep_think_llm = ChatOpenAI(
            model=self.config.get("deep_think_llm", "gpt-4o-mini"),
            temperature=self.config.get("temperature", 0.7),
            max_tokens=self.config.get("max_tokens", 4000)
        )
        
        self.quick_think_llm = ChatOpenAI(
            model=self.config.get("quick_think_llm", "gpt-4o-mini"),
            temperature=self.config.get("temperature", 0.7),
            max_tokens=self.config.get("max_tokens", 4000)
        )
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Build graph
        self.graph = self._build_graph()
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents."""
        agents = {}
        
        # Analysis agents
        agents["company_analyst"] = CompanyAnalyst(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        agents["jd_analyst"] = JDAnalyst(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        agents["market_analyst"] = MarketAnalyst(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        # Evaluation agents
        agents["candidate_analyst"] = CandidateAnalyst(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        agents["culture_analyst"] = CultureAnalyst(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        agents["trend_analyst"] = TrendAnalyst(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        # Research agents
        agents["strength_researcher"] = StrengthResearcher(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        agents["weakness_researcher"] = WeaknessResearcher(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        # Production agents
        agents["document_writer"] = DocumentWriter(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        agents["quality_manager"] = QualityManager(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        # Guide agents (for self-introduction questions)
        agents["question_guide"] = QuestionGuideAgent(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        agents["experience_guide"] = ExperienceGuideAgent(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        agents["writing_guide"] = WritingGuideAgent(
            llm=self.deep_think_llm,
            config=self.config
        )
        
        return agents
    
    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph."""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for analysis phase
        workflow.add_node("company_analysis", self._run_agent("company_analyst"))
        workflow.add_node("jd_analysis", self._run_agent("jd_analyst"))
        workflow.add_node("market_analysis", self._run_agent("market_analyst"))
        
        # Add nodes for evaluation phase
        workflow.add_node("candidate_analysis", self._run_agent("candidate_analyst"))
        workflow.add_node("culture_analysis", self._run_agent("culture_analyst"))
        workflow.add_node("trend_analysis", self._run_agent("trend_analyst"))
        
        # Add nodes for research phase
        workflow.add_node("strength_research", self._run_agent("strength_researcher"))
        workflow.add_node("weakness_research", self._run_agent("weakness_researcher"))
        
        # Add nodes for production phase
        workflow.add_node("document_writing", self._run_agent("document_writer"))
        workflow.add_node("quality_management", self._run_agent("quality_manager"))
        
        # Add nodes for guide phase (self-introduction questions)
        workflow.add_node("question_guide", self._run_agent("question_guide"))
        workflow.add_node("experience_guide", self._run_agent("experience_guide"))
        workflow.add_node("writing_guide", self._run_agent("writing_guide"))
        
        # Define the workflow
        workflow.set_entry_point("company_analysis")
        
        # Analysis phase - sequential execution
        workflow.add_edge("company_analysis", "jd_analysis")
        workflow.add_edge("jd_analysis", "market_analysis")
        
        # Evaluation phase
        workflow.add_edge("market_analysis", "candidate_analysis")
        workflow.add_edge("candidate_analysis", "culture_analysis")
        workflow.add_edge("culture_analysis", "trend_analysis")
        
        # Research phase
        workflow.add_edge("trend_analysis", "strength_research")
        workflow.add_edge("strength_research", "weakness_research")
        
        # Production phase
        workflow.add_edge("weakness_research", "document_writing")
        workflow.add_edge("document_writing", "quality_management")
        
        # Guide phase (for self-introduction questions)
        workflow.add_edge("quality_management", "question_guide")
        workflow.add_edge("question_guide", "experience_guide")
        workflow.add_edge("experience_guide", "writing_guide")
        
        # End
        workflow.add_edge("writing_guide", END)
        
        return workflow.compile()
    
    def _run_agent(self, agent_name: str):
        """Create a function to run a specific agent."""
        async def run_agent(state: AgentState) -> AgentState:
            if self.debug:
                print(f"Running {agent_name}...")
            
            agent = self.agents[agent_name]
            return await agent.analyze(state)
        
        return run_agent
    
    async def propagate(self, company_name: str, job_title: str, job_description: str, candidate_info: Dict[str, Any]) -> Tuple[AgentState, Any]:
        """Execute the complete resume analysis workflow."""
        
        # Initialize state with ProfileManager
        from ..utils.profile_manager import ProfileManager
        profile_manager = ProfileManager()
        
        initial_state = AgentState(
            company_name=company_name,
            job_title=job_title,
            job_description=job_description,
            candidate_info=candidate_info,
            analysis_results={},
            quality_score=None,
            profile_manager=profile_manager  # ProfileManager 추가
        )
        
        if self.debug:
            print(f"Starting analysis for {company_name} - {job_title}")
        
        # Execute workflow
        result = await self.graph.ainvoke(initial_state)
        
        # Extract final state and decision
        final_state = result
        
        # Create decision object
        decision = {
            "company_name": final_state.company_name,
            "job_title": final_state.job_title,
            "analysis_results": final_state.analysis_results,
            "quality_score": final_state.quality_score or 0.0,
            "final_document": final_state.analysis_results.get("final_document", ""),
            "recommendations": final_state.analysis_results.get("recommendations", [])
        }
        
        return final_state, decision
    
    def run_sync(
        self,
        company_name: str,
        job_title: str,
        job_description: str,
        candidate_info: Dict[str, Any],
        date: Optional[str] = None
    ) -> Tuple[AgentState, Dict[str, Any]]:
        """
        Synchronous version of propagate.
        """
        return asyncio.run(self.propagate(
            company_name=company_name,
            job_title=job_title,
            job_description=job_description,
            candidate_info=candidate_info,
            date=date
        )) 
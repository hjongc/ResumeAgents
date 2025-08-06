"""
ResumeAgents agents module.
"""

# Import all agent teams
from .analysis import CompanyAnalyst, JDAnalyst, MarketAnalyst
from .evaluation import CandidateAnalyst, CultureAnalyst, TrendAnalyst
from .research import StrengthResearcher, WeaknessResearcher
from .production import DocumentWriter, QualityManager
from .guide import QuestionGuideAgent, ExperienceGuideAgent, WritingGuideAgent

__all__ = [
    # Analysis Team
    "CompanyAnalyst",
    "JDAnalyst", 
    "MarketAnalyst",
    
    # Evaluation Team
    "CandidateAnalyst",
    "CultureAnalyst",
    "TrendAnalyst",
    
    # Research Team
    "StrengthResearcher",
    "WeaknessResearcher",
    
    # Production Team
    "DocumentWriter",
    "QualityManager",
    
    # Guide Team
    "QuestionGuideAgent",
    "ExperienceGuideAgent",
    "WritingGuideAgent",
] 
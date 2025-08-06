"""
ResumeAgents - Multi-agent framework for job application document creation.
"""

# Analysis Team - External Information Analysis
from .analysis import CompanyAnalyst, JDAnalyst, MarketAnalyst

# Matching Team - Candidate-Company Matching  
from .matching import CandidateAnalyst, CultureAnalyst, TrendAnalyst

# Strategy Team - Strategic Positioning
from .strategy import StrengthResearcher, WeaknessResearcher

# Guide Team - Writing Guidance
from .guides import QuestionGuide, ExperienceGuide, WritingGuide

# Production Team - Document Creation
from .production import DocumentWriter, QualityManager

__all__ = [
    # Analysis Team
    "CompanyAnalyst", 
    "JDAnalyst", 
    "MarketAnalyst",
    
    # Matching Team
    "CandidateAnalyst",
    "CultureAnalyst", 
    "TrendAnalyst",
    
    # Strategy Team
    "StrengthResearcher",
    "WeaknessResearcher",
    
    # Guide Team
    "QuestionGuide",
    "ExperienceGuide",
    "WritingGuide",
    
    # Production Team
    "DocumentWriter",
    "QualityManager",
] 
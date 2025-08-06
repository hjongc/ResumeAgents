"""
ResumeAgents: Multi-Agents LLM Resume & Job Application Framework

A multi-agent framework for creating optimized job application documents
through collaborative analysis and discussion.
"""

__version__ = "0.1.0"
__author__ = "chai hyeon jong"
__email__ = "chaihyeonjong@gmail.com"

from .graph.resume_graph import ResumeAgentsGraph
from .default_config import DEFAULT_CONFIG

__all__ = ["ResumeAgentsGraph", "DEFAULT_CONFIG"] 
"""
HirePath Agent - Career acceleration backend module
Provides end-to-end analysis: resume parsing, GitHub evaluation, ATS scoring, skill gap analysis, and job matching
"""

__version__ = "1.0.0"
__author__ = "HirePath Team"

from .resume_parser import parse_resume
from .github_fetcher import fetch_github_data
from .ats_scorer import calculate_ats_score
from .skill_gap import compute_skill_gap, generate_learning_path
from .job_matcher import match_jobs
from .ollama_client import analyze_github_projects, generate_career_roadmap

__all__ = [
    'parse_resume',
    'fetch_github_data',
    'calculate_ats_score',
    'compute_skill_gap',
    'generate_learning_path',
    'match_jobs',
    'analyze_github_projects',
    'generate_career_roadmap'
]

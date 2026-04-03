"""
Job Matcher Standalone Module

A self-contained module for fetching and ranking job listings based on resume skills.

Usage:
    from job_matcher_standalone import fetch_and_rank_jobs
    
    jobs = fetch_and_rank_jobs(
        resume_text="Your resume text...",
        resume_skills=["Python", "Docker", "AWS"],
        target_role="Software Engineer"
    )

For detailed documentation, see README.md
"""

from .job_matcher import fetch_and_rank_jobs

__version__ = "1.0.0"
__all__ = ["fetch_and_rank_jobs"]

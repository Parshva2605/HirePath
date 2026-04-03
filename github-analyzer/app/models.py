"""
GitHub Profile Analyzer - Data Models
File: app/models.py
"""
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request model for profile analysis"""
    github_url: str
    target_domain: str
    target_companies: List[str]


class RepositoryData(BaseModel):
    """Repository information"""
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int
    forks: int
    topics: List[str] = []
    is_fork: bool
    created_at: datetime
    updated_at: datetime
    has_readme: bool


class ProfileData(BaseModel):
    """GitHub profile information"""
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    followers: int
    following: int
    public_repos: int
    public_gists: int
    created_at: datetime
    repositories: List[RepositoryData]
    languages: Dict[str, int]
    total_stars: int
    total_forks: int


class RatingBreakdown(BaseModel):
    """Detailed rating breakdown"""
    repository_quality: float
    tech_stack_alignment: float
    contribution_consistency: float
    documentation_quality: float
    domain_relevance: float


class ProjectRecommendation(BaseModel):
    """AI-generated project recommendation"""
    title: str
    description: str
    technologies: List[str]
    difficulty: str
    impact: str
    reasoning: str


class AnalysisResult(BaseModel):
    """Complete analysis result"""
    profile_data: ProfileData
    overall_rating: float
    rating_breakdown: RatingBreakdown
    strengths: List[str]
    weaknesses: List[str]
    project_recommendations: List[ProjectRecommendation]
    company_alignment: Dict[str, str]
    improvement_suggestions: List[str]

"""
Job matcher - Match user skills against job listings in local job folder.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import List, Dict, Any

import requests
def _normalize_location(location: str) -> str:
    return (location or "").strip() or "India"


def _location_is_india(location: str) -> bool:
    normalized = _normalize_location(location).lower()
    return "india" in normalized or "remote" in normalized or normalized == ""


def _fetch_remotive_jobs(role: str, preferred_location: str = "India") -> List[Dict[str, Any]]:
    try:
        response = requests.get(
            "https://remotive.com/api/remote-jobs",
            params={"search": role, "limit": 10},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        results = []
        for job in data.get("jobs", [])[:10]:
            results.append({
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "domain": role,
                "location": "Remote / India",
                "employment_type": "Full-time",
                "salary_range": job.get("salary", "Not disclosed"),
                "description": job.get("description", ""),
                "required_skills": _extract_skills_from_text(f"{job.get('title', '')} {job.get('description', '')}"),
                "nice_to_have": [],
                "url": job.get("url", ""),
                "source": "Remotive"
            })
        return results
    except Exception:
        return []


def _get_india_demo_jobs(role: str) -> List[Dict[str, Any]]:
    return [
        {
            "id": "india_001",
            "title": f"{role} - Product Engineering",
            "company": "BharatTech",
            "domain": role.lower(),
            "location": "Bengaluru, India",
            "employment_type": "Full-time",
            "salary_range": "₹12,00,000 - ₹22,00,000",
            "description": f"Build product features for a fast-growing India-first platform. Strong fundamentals in {role} are required.",
            "required_skills": ["React", "TypeScript", "Python", "API Design", "Git", "Testing"],
            "nice_to_have": ["Next.js", "Docker", "System Design"],
            "url": "https://www.linkedin.com/jobs/search/?keywords=india%20product%20engineer"
        },
        {
            "id": "india_002",
            "title": f"Senior {role}",
            "company": "Nexa Software",
            "domain": role.lower(),
            "location": "Hyderabad, India",
            "employment_type": "Full-time",
            "salary_range": "₹15,00,000 - ₹28,00,000",
            "description": f"Deliver reliable, scalable systems for India customers with strong engineering practices.",
            "required_skills": ["Python", "System Design", "Docker", "SQL", "AWS", "CI/CD"],
            "nice_to_have": ["Kubernetes", "Observability", "Microservices"],
            "url": "https://www.linkedin.com/jobs/search/?keywords=india%20software%20engineer"
        },
        {
            "id": "india_003",
            "title": f"{role} Intern",
            "company": "CodeOrbit India",
            "domain": role.lower(),
            "location": "Pune, India",
            "employment_type": "Internship",
            "salary_range": "₹25,000 - ₹60,000 / month",
            "description": f"Entry-level role for candidates with strong project work and willingness to learn {role} skills.",
            "required_skills": ["Git", "Problem Solving", "Communication", "Basics of Python", "Basics of JavaScript"],
            "nice_to_have": ["Projects", "Open source", "Deployment"],
            "url": "https://www.linkedin.com/jobs/search/?keywords=india%20internship%20engineer"
        }
    ]


def _extract_skills_from_text(text: str) -> List[str]:
    skills_db = [
        "Python", "JavaScript", "TypeScript", "React", "Next.js", "Node.js", "FastAPI", "Django",
        "Flask", "SQL", "PostgreSQL", "MongoDB", "Redis", "AWS", "Azure", "GCP", "Docker",
        "Kubernetes", "CI/CD", "Git", "Testing", "System Design", "Microservices", "API Design",
        "Data Structures", "Algorithms", "HTML", "CSS", "Linux"
    ]
    text_lower = (text or "").lower()
    matched = []
    for skill in skills_db:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            matched.append(skill)
    return matched


def _score_job(user_skills: List[str], job: Dict[str, Any], domain: str) -> Dict[str, Any]:
    job_text = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('required_skills', []))} {' '.join(job.get('nice_to_have', []))}"
    job_skills = set(skill.lower() for skill in _extract_skills_from_text(job_text))
    user_skills_lower = set(skill.lower() for skill in user_skills)

    matched_skills = sorted(user_skills_lower & job_skills)
    missing_skills = sorted(job_skills - user_skills_lower)
    skill_overlap = round((len(matched_skills) / max(len(job_skills), 1)) * 100, 1)

    domain_keywords = {
        "frontend": ["react", "next.js", "typescript", "ui", "frontend", "javascript"],
        "backend": ["fastapi", "python", "api", "database", "microservices", "system design"],
        "fullstack": ["react", "node.js", "python", "next.js", "api", "database"],
        "devops": ["docker", "kubernetes", "ci/cd", "linux", "terraform", "aws"],
        "aiml": ["python", "machine learning", "tensorflow", "pytorch", "nlp", "model"]
    }
    domain_terms = domain_keywords.get(domain.lower(), [])
    domain_match = round((sum(1 for term in domain_terms if term in job_text.lower()) / max(len(domain_terms), 1)) * 100, 1)
    total_score = round(min(99, skill_overlap * 0.65 + domain_match * 0.35), 1)

    return {
        "title": job.get("title", ""),
        "company": job.get("company", ""),
        "domain": job.get("domain", domain),
        "description": job.get("description", ""),
        "location": _normalize_location(job.get("location", "India")),
        "url": job.get("url", ""),
        "required_skills": job.get("required_skills", []),
        "match_score": total_score,
        "skill_overlap": skill_overlap,
        "domain_match": domain_match,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_breakdown": {
            "skill_overlap_contribution": round(skill_overlap * 0.65, 1),
            "domain_match_contribution": round(domain_match * 0.35, 1)
        }
    }


def load_job_listings(job_folder: str = None) -> List[Dict[str, Any]]:
    """
    Load all job listings from folder.
    
    Args:
        job_folder: Path to folder containing job JSON files
    
    Returns:
        List of job listings
    """
    if job_folder is None:
        job_folder = Path(__file__).parent.parent / "job_folder"  # Default fallback
    
    job_folder = Path(job_folder)
    jobs = []
    
    if not job_folder.exists():
        print(f"Job folder not found: {job_folder}")
        return []
    
    # Load JSON files
    for json_file in job_folder.glob("**/*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    jobs.extend(data)
                else:
                    jobs.append(data)
        except Exception as e:
            print(f"Error loading {json_file}: {str(e)}")
    
    return jobs


def calculate_skill_overlap(user_skills: List[str], job_skills: List[str]) -> tuple:
    """
    Calculate skill overlap between user and job.
    
    Args:
        user_skills: User's skills
        job_skills: Job required skills
    
    Returns:
        Tuple of (overlap_percentage, matched_skills, missing_skills)
    """
    user_skills_lower = set(s.lower() for s in user_skills)
    job_skills_lower = set(s.lower() for s in job_skills)
    
    if not job_skills_lower:
        return 0, [], []
    
    matched = user_skills_lower & job_skills_lower
    missing = job_skills_lower - user_skills_lower
    
    overlap_percent = (len(matched) / len(job_skills_lower)) * 100
    
    return round(overlap_percent, 1), list(matched), list(missing)


def calculate_domain_match(user_skills: List[str], job_description: str, domain: str) -> float:
    """
    Calculate how well the job matches the target domain.
    
    Args:
        user_skills: User's skills
        job_description: Job description text
        domain: Target domain
    
    Returns:
        Match score (0-100)
    """
    job_text = (job_description or "").lower()
    
    # Domain keywords
    domain_keywords = {
        "aiml": ["machine learning", "deep learning", "nlp", "computer vision", "ai", "neural", "tensorflow", "pytorch"],
        "devops": ["devops", "kubernetes", "docker", "ci/cd", "infrastructure", "deployment", "cloud"],
        "frontend": ["react", "frontend", "ui", "ux", "javascript", "typescript", "css"],
        "backend": ["backend", "api", "server", "database", "nodejs", "python", "microservices"],
        "fullstack": ["fullstack", "full-stack", "full stack", "backend", "frontend"],
        "data": ["data engineer", "data science", "analytics", "etl", "pipeline", "spark", "hadoop"]
    }
    
    domain_lower = domain.lower()
    keywords = domain_keywords.get(domain_lower, [])
    
    matched_keywords = sum(1 for kw in keywords if kw in job_text)
    match_score = (matched_keywords / len(keywords) * 100) if keywords else 0
    
    return round(min(100, match_score), 1)


def match_jobs(
    user_skills: List[str],
    domain: str,
    job_folder: str = None,
    top_n: int = 10,
    min_match_threshold: float = 30
) -> List[Dict[str, Any]]:
    """
    Find and rank jobs matching user profile.
    
    Args:
        user_skills: User's skills
        domain: Target domain
        job_folder: Path to job listing folder
        top_n: Number of top matches to return
        min_match_threshold: Minimum match percentage to include
    
    Returns:
        List of matched jobs with scores
    """
    jobs = load_job_listings(job_folder)
    jobs.extend(_get_india_demo_jobs(domain))
    jobs.extend(_fetch_remotive_jobs(domain))

    if not jobs:
        return []
    
    scored_jobs = []
    
    for job in jobs:
        scored = _score_job(user_skills, job, domain)
        if scored["match_score"] >= min_match_threshold and _location_is_india(scored.get("location", "")):
            scored_jobs.append(scored)
    
    # Sort by score descending
    scored_jobs.sort(key=lambda x: -x["match_score"])
    
    return scored_jobs[:top_n]


def get_top_missing_skills_across_jobs(
    user_skills: List[str],
    matched_jobs: List[Dict[str, Any]],
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Find most frequently required skills across matched jobs.
    
    Args:
        user_skills: User's skills
        matched_jobs: List of matched jobs
        top_n: Number of top missing skills to return
    
    Returns:
        List of missing skills ranked by frequency
    """
    user_skills_lower = set(s.lower() for s in user_skills)
    missing_skill_count = Counter()
    
    for job in matched_jobs:
        for skill in job.get("missing_skills", []):
            missing_skill_count[skill.lower()] += 1
    
    # Get top missing skills
    top_missing = missing_skill_count.most_common(top_n)
    
    return [
        {
            "skill": skill,
            "frequency": count,
            "appears_in": f"{count}/{len(matched_jobs)} jobs"
        }
        for skill, count in top_missing
    ]


def find_reachable_jobs(
    matched_jobs: List[Dict[str, Any]],
    learn_skills: List[str],
    score_threshold: float = 60
) -> List[Dict[str, Any]]:
    """
    Find jobs that would be reachable if user learns specified skills.
    
    Args:
        matched_jobs: Current matched jobs
        learn_skills: Skills the user plans to learn
        score_threshold: Score threshold for reachable jobs
    
    Returns:
        Jobs that would become available with new skills
    """
    learn_skills_lower = set(s.lower() for s in learn_skills)
    reachable = []
    
    for job in matched_jobs:
        updated_missing = set(s.lower() for s in job.get("missing_skills", [])) - learn_skills_lower
        
        # If missing skills would drop significantly with new skills
        original_missing = len(job.get("missing_skills", []))
        new_missing = len(updated_missing)
        
        if new_missing < original_missing and original_missing > 0:
            improvement = ((original_missing - new_missing) / original_missing) * 100
            
            if improvement >= 30:  # At least 30% improvement
                reachable.append({
                    "job": job.get("title", ""),
                    "company": job.get("company", ""),
                    "current_score": job.get("match_score", 0),
                    "current_missing_skills": original_missing,
                    "new_missing_skills": new_missing,
                    "improvement_percent": round(improvement, 1),
                    "url": job.get("url", "")
                })
    
    return sorted(reachable, key=lambda x: -x["improvement_percent"])[:5]


def get_job_match_summary(matched_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics for matched jobs.
    
    Args:
        matched_jobs: List of matched jobs
    
    Returns:
        Summary statistics
    """
    if not matched_jobs:
        return {
            "total_matches": 0,
            "avg_score": 0,
            "score_range": "N/A"
        }
    
    scores = [job.get("match_score", 0) for job in matched_jobs]
    companies = set(job.get("company", "") for job in matched_jobs)
    
    return {
        "total_matches": len(matched_jobs),
        "unique_companies": len(companies),
        "companies": list(companies),
        "average_match_score": round(sum(scores) / len(scores), 1),
        "best_match": matched_jobs[0].get("match_score", 0) if matched_jobs else 0,
        "jobs_over_70": sum(1 for s in scores if s >= 70),
        "jobs_over_50": sum(1 for s in scores if s >= 50),
        "score_distribution": {
            "80-100": sum(1 for s in scores if s >= 80),
            "60-79": sum(1 for s in scores if 60 <= s < 80),
            "40-59": sum(1 for s in scores if 40 <= s < 60),
            "below_40": sum(1 for s in scores if s < 40)
        }
    }


if __name__ == "__main__":
    print("Job matcher module loaded successfully")

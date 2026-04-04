"""
Skill gap analysis - compare user skills against domain and company requirements.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


SKILL_ALIASES = {
    "js": "javascript",
    "nodejs": "node.js",
    "node": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "nextjs": "next.js",
    "next.js": "next.js",
    "ts": "typescript",
    "py": "python",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "k8s": "kubernetes",
    "cicd": "ci/cd",
    "ci cd": "ci/cd",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "tf": "terraform"
}


def normalize_skill(skill: str) -> str:
    normalized = (skill or "").strip().lower().replace("_", " ")
    return SKILL_ALIASES.get(normalized, normalized)


def normalize_skill_list(skills: List[str]) -> List[str]:
    return [normalize_skill(skill) for skill in skills if skill]


def load_skill_requirements(domain: str, company: str = None, db_path: str = None) -> Dict[str, Any]:
    """
    Load skill requirements from JSON database.
    
    Args:
        domain: Target domain (e.g., "aiml", "devops")
        company: Target company (optional)
        db_path: Path to skill_gap_db folder
    
    Returns:
        Dictionary with required skills
    """
    if db_path is None:
        db_path = Path(__file__).parent.parent / "skill_gap_db"
    else:
        db_path = Path(db_path)
    
    # Load domain requirements
    domain_file = db_path / "domains" / f"{domain.lower()}.json"
    domain_reqs = {}
    
    if domain_file.exists():
        with open(domain_file) as f:
            domain_reqs = json.load(f)
    
    # Load company-specific requirements if provided
    company_reqs = {}
    if company:
        company_file = db_path / "companies" / f"{company.lower()}.json"
        if company_file.exists():
            with open(company_file) as f:
                company_reqs = json.load(f)
    
    return {
        "domain": domain_reqs,
        "company": company_reqs
    }


def compute_skill_gap(
    user_skills: List[str],
    user_github_languages: List[tuple],
    domain: str,
    company: str = None,
    db_path: str = None
) -> Dict[str, Any]:
    """
    Compute skill gap between user and domain/company requirements.
    
    Args:
        user_skills: List of skills from resume
        user_github_languages: List of (language, count) tuples from GitHub
        domain: Target domain
        company: Target company (optional)
        db_path: Path to skill_gap_db
    
    Returns:
        Dictionary with skill gap analysis
    """
    requirements = load_skill_requirements(domain, company, db_path)
    domain_reqs = requirements.get("domain", {})
    company_reqs = requirements.get("company", {})
    
    # Normalize user skills
    user_skills_lower = normalize_skill_list(user_skills)
    user_languages = [normalize_skill(lang) for lang, _ in user_github_languages]
    all_user_skills = set(user_skills_lower + user_languages)
    
    # Extract required skills
    must_have = set(normalize_skill(s) for s in domain_reqs.get("required_skills", {}).get("must_have", []))
    good_to_have = set(normalize_skill(s) for s in domain_reqs.get("required_skills", {}).get("good_to_have", []))
    advanced = set(normalize_skill(s) for s in domain_reqs.get("required_skills", {}).get("advanced", []))
    
    # Company overrides (if available)
    if company_reqs and "specific_requirements" in company_reqs:
        company_specific = company_reqs["specific_requirements"].get(domain, {})
        if "extra_skills" in company_specific:
            must_have.update(normalize_skill(s) for s in company_specific["extra_skills"])
    
    # Calculate gaps
    missing_must = must_have - all_user_skills
    have_must = must_have & all_user_skills
    missing_good = good_to_have - all_user_skills
    have_good = good_to_have & all_user_skills
    have_advanced = advanced & all_user_skills
    learning_opportunity = advanced - all_user_skills
    
    # Gap percentage
    if must_have:
        gap_percentage = round((len(missing_must) / len(must_have)) * 100, 1)
    else:
        gap_percentage = 0
    
    # Readiness score (0-100)
    # 40% must-have coverage, 30% good-to-have coverage, 30% advanced skills
    must_score = (len(have_must) / len(must_have) * 100) if must_have else 0
    good_score = (len(have_good) / len(good_to_have) * 100) if good_to_have else 100
    adv_score = (len(have_advanced) / len(advanced) * 100) if advanced else 0
    
    readiness_score = round(must_score * 0.4 + good_score * 0.3 + adv_score * 0.3, 1)
    
    return {
        "user_skills": list(all_user_skills),
        "must_have": {
            "required": list(must_have),
            "have": list(have_must),
            "missing": list(missing_must),
            "coverage": round((len(have_must) / len(must_have)) * 100, 1) if must_have else 0
        },
        "good_to_have": {
            "required": list(good_to_have),
            "have": list(have_good),
            "missing": list(missing_good),
            "coverage": round((len(have_good) / len(good_to_have)) * 100, 1) if good_to_have else 0
        },
        "advanced": {
            "required": list(advanced),
            "have": list(have_advanced),
            "missing": list(learning_opportunity),
            "coverage": round((len(have_advanced) / len(advanced)) * 100, 1) if advanced else 0
        },
        "gap_percentage": gap_percentage,
        "readiness_score": readiness_score,
        "readiness_level": get_readiness_level(readiness_score),
        "domain": domain,
        "company": company,
        "summary": {
            "total_required_skills": len(must_have) + len(good_to_have) + len(advanced),
            "skills_covered": len(have_must) + len(have_good) + len(have_advanced),
            "skills_missing": len(missing_must) + len(missing_good) + len(learning_opportunity)
        }
    }


def get_readiness_level(score: float) -> str:
    """
    Convert readiness score to level.
    
    Args:
        score: Readiness score (0-100)
    
    Returns:
        Readiness level
    """
    if score >= 90:
        return "Excellent - Ready to apply"
    elif score >= 75:
        return "Good - Minor gaps, apply with focus"
    elif score >= 60:
        return "Fair - Moderate gaps, upskill first"
    elif score >= 40:
        return "Poor - Major gaps, structured learning needed"
    else:
        return "Very Poor - Significant transformation required"


def get_priority_skills_to_learn(gap_analysis: Dict) -> List[Dict[str, Any]]:
    """
    Get prioritized list of skills to learn.
    
    Args:
        gap_analysis: Result from compute_skill_gap()
    
    Returns:
        List of skills with priority levels
    """
    priority_skills = []
    
    # Priority 1: Missing must-have skills
    for skill in gap_analysis["must_have"]["missing"]:
        priority_skills.append({
            "skill": skill,
            "priority": 1,
            "category": "must_have",
            "importance": "Critical - required for most positions"
        })
    
    # Priority 2: High-value good-to-have skills
    high_value_good = gap_analysis["good_to_have"]["missing"][:5]
    for skill in high_value_good:
        priority_skills.append({
            "skill": skill,
            "priority": 2,
            "category": "good_to_have",
            "importance": "Important - differentiator in interviews"
        })
    
    # Priority 3: Advanced skills
    for skill in gap_analysis["advanced"]["missing"][:3]:
        priority_skills.append({
            "skill": skill,
            "priority": 3,
            "category": "advanced",
            "importance": "Nice-to-have - advanced career growth"
        })
    
    return priority_skills


def generate_learning_path(gap_analysis: Dict, timeframe_weeks: int = 12) -> Dict[str, Any]:
    """
    Generate a structured learning path based on gaps.
    
    Args:
        gap_analysis: Result from compute_skill_gap()
        timeframe_weeks: Total weeks available for learning
    
    Returns:
        Learning path with phases
    """
    priority_skills = get_priority_skills_to_learn(gap_analysis)
    
    # Distribute learning across phases (roughly)
    must_learn = [s for s in priority_skills if s["priority"] == 1]
    good_to_learn = [s for s in priority_skills if s["priority"] == 2]
    advanced_to_learn = [s for s in priority_skills if s["priority"] == 3]
    
    weeks_per_phase = timeframe_weeks // 3 if timeframe_weeks >= 9 else 2
    
    return {
        "total_weeks": timeframe_weeks,
        "phases": [
            {
                "name": "Phase 1: Foundations",
                "duration_weeks": weeks_per_phase,
                "focus": "Must-have skills",
                "skills": must_learn[:3],
                "goal": "Cover critical skill gaps",
                "approach": "Fundamentals, hands-on projects"
            },
            {
                "name": "Phase 2: Depth & Breadth",
                "duration_weeks": weeks_per_phase,
                "focus": "Good-to-have + projects",
                "skills": good_to_learn[:3],
                "goal": "Build portfolio, gain practical experience",
                "approach": "Real projects, open source contributions"
            },
            {
                "name": "Phase 3: Polish & Advanced",
                "duration_weeks": weeks_per_phase,
                "focus": "Advanced skills + interview prep",
                "skills": advanced_to_learn[:2],
                "goal": "Competitive edge and system design",
                "approach": "Advanced concepts, mock interviews"
            }
        ],
        "readiness_timeline": {
            "current_score": gap_analysis["readiness_score"],
            "target_score": 85,
            "estimated_weeks_to_target": timeframe_weeks if gap_analysis["readiness_score"] < 85 else 0
        }
    }


if __name__ == "__main__":
    print("Skill gap analysis module loaded successfully")

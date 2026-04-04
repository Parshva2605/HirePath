"""
ATS (Applicant Tracking System) score calculator.
Scores resume based on keyword match, format, quantification, length, and action verbs.
"""

import re
from typing import Dict, Any, List
from collections import defaultdict


# Domain-specific keyword dictionaries
DOMAIN_KEYWORDS = {
    "aiml": [
        "machine learning", "deep learning", "pytorch", "tensorflow", "nlp",
        "computer vision", "scikit-learn", "pandas", "numpy", "llm", "transformers",
        "data pipeline", "model training", "feature engineering", "mlops", "bert",
        "gpt", "neural network", "gradient descent", "backpropagation", "optimization",
        "classification", "regression", "clustering", "supervised learning", "unsupervised learning",
        "reinforcement learning", "overfitting", "regularization", "cross-validation",
        "jupyter", "anaconda", "opencv", "hugging face", "kaggle"
    ],
    "devops": [
        "kubernetes", "docker", "ci/cd", "jenkins", "terraform", "ansible",
        "aws", "azure", "gcp", "monitoring", "prometheus", "grafana", "helm",
        "linux", "bash", "shell scripting", "infrastructure as code", "iac",
        "logging", "splunk", "elk stack", "datadog", "cloudwatch",
        "load balancing", "auto scaling", "deployment", "orchestration",
        "container", "virtualization", "networking", "security", "observability"
    ],
    "frontend": [
        "react", "nextjs", "typescript", "tailwind", "css", "html",
        "vue", "angular", "webpack", "testing", "accessibility", "jest",
        "responsive design", "ui/ux", "component library", "state management",
        "redux", "graphql", "rest api", "fetch", "axios", "web performance",
        "optimization", "seo", "pwa", "progressive web app", "sass", "less"
    ],
    "backend": [
        "api", "rest", "graphql", "nodejs", "python", "java", "spring",
        "fastapi", "django", "flask", "postgresql", "redis", "microservices",
        "database", "sql", "nosql", "mongodb", "mysql", "authentication",
        "oauth", "jwt", "websocket", "message queue", "rabbitmq", "kafka",
        "caching", "load balancing", "scalability", "architecture", "design patterns"
    ],
    "data_engineering": [
        "spark", "hadoop", "airflow", "dbt", "etl", "data pipeline",
        "big data", "distributed computing", "data warehouse", "snowflake",
        "redshift", "bigquery", "sql", "nosql", "kafka", "streaming",
        "apache", "hive", "presto", "scala", "pyspark", "data quality",
        "validation", "monitoring", "documentation"
    ],
    "cloud": [
        "aws", "azure", "gcp", "cloud computing", "cloud architecture",
        "ec2", "s3", "lambda", "cloudformation", "terraform", "azure devops",
        "virtual machines", "containers", "networking", "security",
        "compliance", "disaster recovery", "backup", "storage"
    ],
    "fullstack": [
        "react", "nextjs", "node", "express", "fastapi", "django",
        "postgresql", "mongodb", "docker", "devops", "api", "graphql",
        "typescript", "javascript", "python", "full stack", "end-to-end",
        "deployment", "ci/cd", "testing", "authentication"
    ]
}

# Strong action verbs
ACTION_VERBS = [
    "built", "designed", "developed", "led", "optimized", "reduced",
    "increased", "deployed", "implemented", "architected", "automated",
    "created", "engineered", "launched", "scaled", "improved",
    "enhanced", "accelerated", "streamlined", "invented", "pioneered",
    "managed", "directed", "coordinated", "mentored", "delivered",
    "resolved", "solved", "analyzed", "evaluated", "documented"
]

# Required resume sections
REQUIRED_SECTIONS = ["experience", "education", "skills"]


def calculate_keyword_score(resume_text: str, domain: str) -> tuple:
    """
    Calculate keyword match score.
    
    Args:
        resume_text: Full resume text
        domain: Target domain (e.g., "aiml", "devops")
    
    Returns:
        Tuple of (score, matched_keywords, missing_keywords)
    """
    text_lower = resume_text.lower()
    keywords = DOMAIN_KEYWORDS.get(domain.lower(), [])
    
    matched = [kw for kw in keywords if kw in text_lower]
    missing = [kw for kw in keywords if kw not in text_lower]
    
    if not keywords:
        return 0, [], keywords
    
    score = min(100, (len(matched) / len(keywords)) * 100)
    return round(score, 1), matched, missing


def calculate_format_score(resume_text: str) -> tuple:
    """
    Calculate format quality score based on required sections.
    
    Args:
        resume_text: Full resume text
    
    Returns:
        Tuple of (score, found_sections)
    """
    text_lower = resume_text.lower()
    found_sections = []
    
    for section in REQUIRED_SECTIONS:
        if section in text_lower:
            found_sections.append(section)
    
    score = (len(found_sections) / len(REQUIRED_SECTIONS)) * 100
    return round(score, 1), found_sections


def calculate_quantification_score(resume_text: str) -> float:
    """
    Calculate percentage of bullets with quantifiable metrics.
    
    Args:
        resume_text: Full resume text
    
    Returns:
        Quantification score (0-100)
    """
    # Find all bullet points
    bullets = re.findall(r'[\•\-\*]\s.*', resume_text)
    
    if not bullets:
        return 0.0
    
    # Count bullets with numbers
    bullets_with_numbers = sum(1 for bullet in bullets if re.search(r'\d+', bullet))
    
    score = (bullets_with_numbers / len(bullets)) * 100
    return round(min(100, score), 1)


def calculate_length_score(word_count: int, ideal_min: int = 400, ideal_max: int = 700) -> float:
    """
    Calculate length appropriateness score.
    
    Args:
        word_count: Total word count in resume
        ideal_min: Minimum ideal word count
        ideal_max: Maximum ideal word count
    
    Returns:
        Length score (0-100)
    """
    if ideal_min <= word_count <= ideal_max:
        return 100.0
    
    # Penalty for being too short or too long
    ideal_mid = (ideal_min + ideal_max) / 2
    deviation = abs(word_count - ideal_mid)
    
    score = max(0, 100 - (deviation / 5))
    return round(score, 1)


def calculate_action_verb_score(resume_text: str) -> tuple:
    """
    Calculate action verb usage score.
    
    Args:
        resume_text: Full resume text
    
    Returns:
        Tuple of (score, verb_count, matched_verbs)
    """
    text_lower = resume_text.lower()
    matched_verbs = []
    verb_count = 0
    
    for verb in ACTION_VERBS:
        pattern = r'\b' + re.escape(verb) + r'\b'
        occurrences = len(re.findall(pattern, text_lower))
        if occurrences > 0:
            matched_verbs.append(verb)
            verb_count += occurrences
    
    # Score: up to 30 verbs = 100%
    score = min(100, (verb_count / 30) * 100)
    return round(score, 1), verb_count, matched_verbs


def calculate_ats_score(resume_data: Dict[str, Any], domain: str) -> Dict[str, Any]:
    """
    Calculate overall ATS score with detailed breakdown.
    
    Args:
        resume_data: Dictionary from resume_parser.parse_resume()
        domain: Target domain
    
    Returns:
        Dictionary with total score and component breakdown
    """
    raw_text = resume_data.get("raw_text", "")
    word_count = resume_data.get("word_count", len(raw_text.split()))
    
    # Calculate component scores
    keyword_score, matched_kw, missing_kw = calculate_keyword_score(raw_text, domain)
    format_score, found_sections = calculate_format_score(raw_text)
    quant_score = calculate_quantification_score(raw_text)
    length_score = calculate_length_score(word_count)
    verb_score, verb_count, matched_verbs = calculate_action_verb_score(raw_text)
    
    # Weighted total (as per specification)
    total_score = (
        keyword_score * 0.4 +
        format_score * 0.2 +
        quant_score * 0.2 +
        length_score * 0.1 +
        verb_score * 0.1
    )
    
    # Missing verbs (for recommendations)
    missing_verbs = [v for v in ACTION_VERBS if v not in matched_verbs]
    
    return {
        "total_score": round(total_score, 1),
        "word_count": word_count,
        "breakdown": {
            "keyword_match": keyword_score,
            "format": format_score,
            "quantification": quant_score,
            "length": length_score,
            "action_verbs": verb_score
        },
        "keyword_analysis": {
            "matched": matched_kw,
            "missing": missing_kw[:10],  # Top 10 missing keywords
            "matched_count": len(matched_kw),
            "missing_count": len(missing_kw)
        },
        "found_sections": found_sections,
        "missing_sections": [s for s in REQUIRED_SECTIONS if s not in found_sections],
        "action_verbs_analysis": {
            "matched_verbs": matched_verbs,
            "missing_verbs": missing_verbs[:5],  # Top 5 to add
            "total_count": verb_count
        },
        "quantification_metrics": {
            "score": quant_score,
            "word_count": word_count,
            "length_status": "Good" if 400 <= word_count <= 700 else ("Too short" if word_count < 400 else "Too long")
        },
        "recommendations": {
            "top_priority": generate_top_recommendation(keyword_score, format_score, quant_score),
            "quick_wins": generate_quick_wins(found_sections, verb_count, missing_kw)
        },
        "domain": domain
    }


def generate_top_recommendation(keyword_score: float, format_score: float, quant_score: float) -> str:
    """Generate the single most impactful improvement."""
    scores = {
        "keyword_match": keyword_score,
        "formatting": format_score,
        "quantification": quant_score
    }
    
    min_area = min(scores, key=scores.get)
    
    if min_area == "keyword_match":
        return "Add more domain-specific keywords to match job descriptions"
    elif min_area == "formatting":
        return "Improve structure - ensure clear Experience, Education, and Skills sections"
    else:
        return "Add quantifiable metrics to bullet points (numbers, percentages, impact)"


def generate_quick_wins(found_sections: list, verb_count: int, missing_keywords: list) -> list:
    """Generate list of quick, high-impact improvements."""
    wins = []
    
    if len(found_sections) < 3:
        wins.append("Add missing resume sections (Experience, Education, Skills)")
    
    if verb_count < 10:
        wins.append("Replace weak verbs with strong action words (built, designed, optimized)")
    
    if missing_keywords:
        wins.append(f"Incorporate top missing keywords: {', '.join(missing_keywords[:3])}")
    
    if not wins:
        wins.append("Resume structure looks solid - focus on tailoring content for specific roles")
    
    return wins


def compare_ats_scores(score1: Dict, score2: Dict) -> Dict[str, Any]:
    """
    Compare two ATS scores (e.g., before/after optimization).
    
    Args:
        score1: First ATS score result
        score2: Second ATS score result
    
    Returns:
        Comparison with improvements
    """
    improvements = {}
    
    for metric in ["keyword_match", "format", "quantification", "length", "action_verbs"]:
        old = score1["breakdown"].get(metric, 0)
        new = score2["breakdown"].get(metric, 0)
        improvements[metric] = {
            "before": old,
            "after": new,
            "improvement": round(new - old, 1)
        }
    
    return {
        "total_before": score1["total_score"],
        "total_after": score2["total_score"],
        "total_improvement": round(score2["total_score"] - score1["total_score"], 1),
        "metrics": improvements
    }


if __name__ == "__main__":
    print("ATS Scorer module loaded successfully")
    print(f"Domains supported: {list(DOMAIN_KEYWORDS.keys())}")
    print(f"Action verbs tracked: {len(ACTION_VERBS)}")

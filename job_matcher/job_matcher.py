"""
Standalone Job Matcher Module
Fetches real job listings and ranks them by match score against candidate's resume skills.

This module is completely self-contained and can be copied into any project.
No dependencies on other HirePath modules.
"""

import re
import requests
from typing import List, Dict, Optional
from datetime import datetime


def fetch_and_rank_jobs(
    resume_text: str,
    resume_skills: List[str],
    target_role: str,
    location: str = "India",
    goal_type: str = "job"
) -> List[Dict]:
    """
    Fetch jobs from multiple sources and rank by match score.
    
    Args:
        resume_text: Full resume text (used for additional matching)
        resume_skills: List of skills from resume (e.g., ["Python", "Docker", "AWS"])
        target_role: Job role to search for (e.g., "Software Engineer")
        location: Location preference (default: "India")
        goal_type: One of "internship", "job", "promotion" (default: "job")
        
    Returns:
        List of top 10 ranked job dicts, each containing:
        - title: Job title
        - company: Company name
        - location: Job location
        - url: Application URL
        - match_score: Integer 0-99 indicating match percentage
        - match_label: Human-readable label (e.g., "Strong Match 🟢")
        - match_explanation: One-line explanation of the match
        - salary: Salary range or "Not disclosed"
        - posted_date: When job was posted
        - platform: Source platform (e.g., "Remotive", "Demo")
        - description_snippet: First 150 chars of description
    """
    all_jobs = []
    
    # Fetch from Remotive (free API, no key required)
    try:
        remotive_jobs = _fetch_remotive_jobs(target_role)
        all_jobs.extend(remotive_jobs)
    except Exception:
        pass
    
    # Fetch from demo data as fallback
    if len(all_jobs) < 5:
        demo_jobs = _get_demo_jobs(target_role, location)
        all_jobs.extend(demo_jobs)
    
    # Filter for internships if needed
    if goal_type == "internship":
        filtered_jobs = []
        for job in all_jobs:
            title_lower = job.get('title', '').lower()
            desc_lower = job.get('description', '').lower()
            if 'intern' in title_lower or 'intern' in desc_lower:
                filtered_jobs.append(job)
        
        # If we have internship-specific jobs, use those; otherwise use all
        if filtered_jobs:
            all_jobs = filtered_jobs
    
    # Score and rank each job
    ranked_jobs = []
    for job in all_jobs:
        match_score = _calculate_job_match(resume_text, resume_skills, job)
        
        # Extract skills from job description
        job_skills = _extract_skills_from_text(job.get('description', ''))
        
        # Get match label and explanation
        match_label = _get_match_label(match_score)
        match_explanation = _get_match_explanation(resume_skills, job_skills, match_score)
        
        # Build result dict
        ranked_jobs.append({
            'title': job.get('title', ''),
            'company': job.get('company', ''),
            'salary': job.get('salary', 'Not disclosed'),
            'location': job.get('location', location),
            'match_score': int(match_score),  # Integer 0-99
            'match_label': match_label,
            'match_explanation': match_explanation,
            'url': job.get('url', ''),
            'posted_date': job.get('posted_date', 'Recently'),
            'platform': job.get('source', 'Job Board'),
            'description_snippet': job.get('description', '')[:150]
        })
    
    # Sort by match_score descending
    ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Return top 10
    return ranked_jobs[:10]


def _calculate_job_match(
    resume_text: str,
    resume_skills: List[str],
    job: Dict
) -> float:
    """
    Calculate match score between resume and job.
    
    Algorithm:
    1. Combine job title + description into single text
    2. Count how many resume skills appear in job text (word boundary matching)
    3. Calculate percentage: (matched_skills / total_resume_skills) * 100
    4. Cap at 99 to avoid showing 100% match
    
    Args:
        resume_text: Full resume text
        resume_skills: List of skills from resume
        job: Job dict with description
        
    Returns:
        Match score from 0 to 99
    """
    job_description = job.get('description', '')
    job_title = job.get('title', '')
    
    if not job_description:
        return 0.0
    
    # Combine job title and description for matching
    job_text = (job_title + ' ' + job_description).lower()
    
    # Count how many resume skills appear in job text
    matched = 0
    for skill in resume_skills:
        skill_lower = skill.lower()
        # Use word boundary matching to avoid partial matches
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', job_text):
            matched += 1
    
    # Calculate match percentage
    total_skills = max(len(resume_skills), 1)  # Avoid division by zero
    match_score = (matched / total_skills) * 100
    
    # Cap at 99 to avoid showing 100% match
    match_score = min(match_score, 99)
    
    return match_score


def _get_match_label(score: float) -> str:
    """Get human-readable match label based on score."""
    if score >= 80:
        return "Strong Match 🟢"
    elif score >= 60:
        return "Good Match 🟡"
    elif score >= 40:
        return "Partial Match 🟠"
    else:
        return "Weak Match 🔴"


def _get_match_explanation(
    resume_skills: List[str],
    job_skills: List[str],
    score: float
) -> str:
    """Generate one-line explanation for match score."""
    resume_skills_set = set(s.lower() for s in resume_skills)
    job_skills_set = set(s.lower() for s in job_skills)
    
    matched_skills = resume_skills_set & job_skills_set
    missing_skills = job_skills_set - resume_skills_set
    
    matched_count = len(matched_skills)
    total_count = len(job_skills_set) if job_skills_set else 1
    
    if score >= 70:
        return f"Strong match — you have {matched_count} of {total_count} required skills"
    elif score >= 40:
        missing_top_3 = list(missing_skills)[:3]
        if missing_top_3:
            return f"Partial match — missing {', '.join(missing_top_3)}"
        else:
            return f"Partial match — {matched_count} of {total_count} skills matched"
    else:
        if missing_skills:
            top_missing = list(missing_skills)[0]
            return f"Weak match — role requires {top_missing} which is not in your resume"
        else:
            return "Weak match — limited skill overlap with job requirements"


def _extract_skills_from_text(text: str) -> List[str]:
    """
    Extract technical skills from job description text.
    Uses a curated list of 200+ common tech skills.
    """
    text_lower = text.lower()
    skills_db = _get_skills_database()
    matched_skills = set()
    
    # Match against skills database (case insensitive)
    for skill in skills_db:
        skill_lower = skill.lower()
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            matched_skills.add(skill_lower)
    
    return sorted(list(matched_skills))


def _get_skills_database() -> List[str]:
    """Return comprehensive database of 200+ tech skills."""
    return [
        # Programming Languages
        "Python", "JavaScript", "Java", "C++", "C#", "TypeScript", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl",
        "Dart", "Objective-C", "Shell", "Bash", "PowerShell", "Groovy",
        
        # Web Frontend
        "React", "Angular", "Vue.js", "Next.js", "Nuxt.js", "Svelte", "jQuery",
        "HTML", "CSS", "SASS", "LESS", "Tailwind CSS", "Bootstrap", "Material-UI",
        "Redux", "MobX", "Webpack", "Vite", "Babel",
        
        # Web Backend
        "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
        "ASP.NET", "Ruby on Rails", "Laravel", "NestJS", "Gin", "Echo",
        
        # Databases
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "DynamoDB",
        "Oracle", "SQL Server", "SQLite", "MariaDB", "Elasticsearch",
        "Neo4j", "Firebase", "Supabase",
        
        # Cloud & DevOps
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab CI",
        "GitHub Actions", "CircleCI", "Terraform", "Ansible", "Helm",
        "Prometheus", "Grafana", "Datadog",
        
        # Data Science & ML
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy",
        "Matplotlib", "Jupyter", "Apache Spark", "Hadoop", "Kafka", "Airflow",
        
        # Mobile Development
        "React Native", "Flutter", "Ionic", "SwiftUI", "Android SDK", "iOS SDK",
        
        # Testing
        "Jest", "Pytest", "JUnit", "Selenium", "Cypress", "Playwright",
        
        # Version Control
        "Git", "GitHub", "GitLab", "Bitbucket",
        
        # Methodologies
        "Agile", "Scrum", "Kanban", "DevOps", "CI/CD", "TDD", "Microservices",
        "REST API", "GraphQL", "gRPC"
    ]


def _fetch_remotive_jobs(role: str) -> List[Dict]:
    """
    Fetch remote jobs from Remotive API (free, no key required).
    
    Args:
        role: Job role to search for
        
    Returns:
        List of normalized job dicts (empty on failure)
    """
    try:
        url = "https://remotive.com/api/remote-jobs"
        params = {
            "search": role,
            "limit": 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        jobs = data.get('jobs', [])
        
        results = []
        for job in jobs[:10]:
            results.append({
                'title': job.get('title', ''),
                'company': job.get('company_name', ''),
                'location': 'Remote',
                'description': job.get('description', ''),
                'source': 'Remotive',
                'url': job.get('url', ''),
                'salary': job.get('salary', 'Not disclosed'),
                'posted_date': job.get('publication_date', 'Recently')
            })
        
        return results
        
    except Exception:
        return []


def _get_demo_jobs(role: str, location: str) -> List[Dict]:
    """
    Return realistic demo job descriptions as fallback.
    
    Args:
        role: Job role
        location: Location
        
    Returns:
        List of 5 demo job descriptions
    """
    return [
        {
            "title": f"{role}",
            "company": "TechCorp Solutions",
            "location": location,
            "description": f"""We are seeking a talented {role} to join our dynamic team.

Key Responsibilities:
• Design, develop, and maintain scalable applications
• Collaborate with cross-functional teams to define and ship new features
• Write clean, maintainable, and efficient code
• Participate in code reviews and technical documentation
• Troubleshoot and debug applications

Required Skills:
• Strong proficiency in Python, JavaScript, or Java
• Experience with React, Node.js, Django, or Spring Boot
• Solid understanding of RESTful APIs and microservices
• Familiarity with AWS, Azure, or GCP
• Knowledge of Docker, Kubernetes, and CI/CD
• Excellent problem-solving skills""",
            "source": "Demo",
            "url": "https://techcorp.com/careers",
            "salary": "₹8,00,000 - ₹15,00,000 per annum",
            "posted_date": "2 days ago"
        },
        {
            "title": f"Senior {role}",
            "company": "InnovateLabs",
            "location": location,
            "description": f"""Join InnovateLabs as a Senior {role} and work on cutting-edge projects.

What You'll Do:
• Lead design and implementation of complex software systems
• Mentor junior developers
• Architect scalable solutions
• Optimize application performance
• Implement security best practices

Technical Requirements:
• 5+ years of software development experience
• Expert knowledge of modern frameworks
• Strong experience with cloud infrastructure
• Proficiency in database design and optimization
• Experience with distributed systems""",
            "source": "Demo",
            "url": "https://innovatelabs.com/careers",
            "salary": "₹15,00,000 - ₹25,00,000 per annum",
            "posted_date": "1 week ago"
        },
        {
            "title": f"{role} - Full Stack",
            "company": "DataFlow Systems",
            "location": location,
            "description": f"""DataFlow Systems is looking for a passionate {role} to build innovative solutions.

Core Responsibilities:
• Develop responsive web applications
• Build robust backend services and APIs
• Integrate third-party services
• Implement automated testing
• Monitor application performance

Must-Have Skills:
• JavaScript/TypeScript and Python or Java
• React, Angular, or Vue.js
• Node.js, Django, or FastAPI
• PostgreSQL, MongoDB, Redis
• AWS, Azure, or GCP
• Docker and Kubernetes""",
            "source": "Demo",
            "url": "https://dataflow.com/careers",
            "salary": "₹10,00,000 - ₹18,00,000 per annum",
            "posted_date": "3 days ago"
        },
        {
            "title": f"{role} - Cloud Platform",
            "company": "CloudNine Technologies",
            "location": location,
            "description": f"""CloudNine Technologies seeks a {role} for our cloud platform team.

Responsibilities:
• Design and implement cloud-native applications
• Work with microservices architecture
• Optimize system performance and scalability
• Implement monitoring and logging solutions
• Collaborate with DevOps team

Skills Required:
• Strong programming skills in Go, Python, or Java
• Experience with Kubernetes and Docker
• Knowledge of AWS, GCP, or Azure
• Understanding of CI/CD pipelines
• Experience with Terraform or CloudFormation""",
            "source": "Demo",
            "url": "https://cloudnine.com/careers",
            "salary": "₹12,00,000 - ₹20,00,000 per annum",
            "posted_date": "5 days ago"
        },
        {
            "title": f"Junior {role}",
            "company": "StartupHub",
            "location": location,
            "description": f"""StartupHub is hiring a Junior {role} to join our growing team.

What You'll Learn:
• Modern software development practices
• Agile methodologies
• Cloud technologies
• Testing and deployment
• Team collaboration

Requirements:
• 0-2 years of experience
• Knowledge of Python, JavaScript, or Java
• Basic understanding of web technologies
• Familiarity with Git
• Eagerness to learn and grow""",
            "source": "Demo",
            "url": "https://startuphub.com/careers",
            "salary": "₹5,00,000 - ₹8,00,000 per annum",
            "posted_date": "1 day ago"
        }
    ]

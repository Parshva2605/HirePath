"""
Ollama client - Local LLM inference for GitHub analysis and career roadmap generation.
"""

import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin

import requests


OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"
TIMEOUT = 60


def _request_chat_completion(
    prompt: str,
    system: str,
    model: str,
    base_url: str,
    temperature: float,
) -> str:
    """Send a prompt using the available Ollama text endpoint."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system} if system else {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_k": 40,
            "top_p": 0.9
        }
    }

    chat_url = urljoin(base_url.rstrip("/") + "/", "api/chat")
    response = requests.post(chat_url, json=payload, timeout=TIMEOUT)
    if response.status_code == 404:
        generate_payload = {
            "model": model,
            "prompt": f"{system}\n\n{prompt}".strip(),
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_k": 40,
                "top_p": 0.9
            }
        }
        generate_url = urljoin(base_url.rstrip("/") + "/", "api/generate")
        response = requests.post(generate_url, json=generate_payload, timeout=TIMEOUT)

    response.raise_for_status()
    result = response.json()
    if "message" in result:
        return result.get("message", {}).get("content", "")
    return result.get("response", "")


def check_ollama_connection(base_url: str = OLLAMA_BASE_URL) -> bool:
    """
    Check if Ollama is running and accessible.
    
    Args:
        base_url: Ollama server URL
    
    Returns:
        True if Ollama is running, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Ollama connection failed: {str(e)}")
        return False


def list_available_models(base_url: str = OLLAMA_BASE_URL) -> list:
    """
    List all available models in Ollama.
    
    Args:
        base_url: Ollama server URL
    
    Returns:
        List of available model names
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        data = response.json()
        models = [m.get("name", "") for m in data.get("models", [])]
        return models
    except Exception as e:
        print(f"Failed to list models: {str(e)}")
        return []


def ollama_chat(
    prompt: str,
    system: str = "",
    model: str = DEFAULT_MODEL,
    base_url: str = OLLAMA_BASE_URL,
    temperature: float = 0.7
) -> str:
    """
    Send a prompt to Ollama and get a response (non-streaming).
    
    Args:
        prompt: User prompt/question
        system: System message to set behavior
        model: Ollama model name
        base_url: Ollama server URL
        temperature: Sampling temperature (0-2), lower = more deterministic
    
    Returns:
        Model response text
    """
    try:
        return _request_chat_completion(prompt, system, model, base_url, temperature)

    except requests.exceptions.Timeout:
        return "Error: Request timed out. Ollama might be overloaded."
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Ensure it's running on " + base_url
    except Exception as e:
        return f"Error: {str(e)}"


def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    """Safely extract a JSON object from a text response."""
    if not text:
        return None

    try:
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        if start_idx >= 0 and end_idx > start_idx:
            return json.loads(text[start_idx:end_idx])
        return json.loads(text)
    except Exception:
        return None


def _resolve_github_quality(github_analysis: Dict[str, Any]) -> Any:
    if not github_analysis:
        return "Not analyzed"

    if isinstance(github_analysis, dict):
        if "quality_score" in github_analysis:
            return github_analysis.get("quality_score", "N/A")

        nested = github_analysis.get("analysis")
        if isinstance(nested, dict):
            return nested.get("quality_score", "N/A")

    return "Not analyzed"


def _fallback_github_analysis(github_data: Dict[str, Any], domain: str, company: str) -> Dict[str, Any]:
    repos = github_data.get("repos", [])
    top_languages = [lang for lang, _ in github_data.get("top_languages", [])[:5]]
    total_repos = github_data.get("total_repos_fetched", 0)
    stars = github_data.get("total_stars", 0)

    quality_score = 35
    quality_score += min(25, total_repos * 2)
    quality_score += min(15, stars * 2)
    quality_score += min(10, len(top_languages) * 2)
    quality_score = max(0, min(100, quality_score))

    strongest = [
        repo.get("name", "")
        for repo in sorted(repos, key=lambda item: (item.get("stars", 0), len(item.get("readme_content", ""))), reverse=True)[:3]
        if repo.get("name")
    ]
    if not strongest:
        strongest = [f"Profile fit for {domain} at {company}"]

    skills_to_learn = top_languages or ["System design", "Testing", "Documentation", "Deployment", "Security"]
    projects_to_build = [
        {
            "title": f"{domain.title()} portfolio project for {company}",
            "stack": ", ".join(top_languages[:3]) or "Your current stack",
            "impact": "Shows job-relevant architecture, quality, and deployment readiness"
        },
        {
            "title": "Production-style resume helper",
            "stack": "Next.js, FastAPI, ATS scoring",
            "impact": "Proves product thinking and practical delivery"
        },
        {
            "title": "Interview-ready case study",
            "stack": "README, screenshots, metrics",
            "impact": "Explains tradeoffs clearly during hiring rounds"
        }
    ]

    return {
        "quality_score": quality_score,
        "strongest_projects": strongest,
        "weak_spots": [
            "Add clearer README files and pinned repositories",
            "Show deployment links or demos",
            "Document measurable impact in each repo"
        ],
        "projects_to_build": projects_to_build,
        "skills_to_learn": skills_to_learn[:5],
        "recommendations": f"Strengthen the {domain} portfolio for {company} with production-ready repos, deployment evidence, and clearer project stories."
    }


def analyze_github_projects(
    github_data: Dict[str, Any],
    domain: str,
    company: str,
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Analyze GitHub projects using Ollama to provide project quality assessment.
    
    Args:
        github_data: GitHub profile data from github_fetcher
        domain: Target domain
        company: Target company
        model: Ollama model to use
    
    Returns:
        Analysis results including quality score and recommendations
    """
    # Prepare repos summary (top 15)
    repos_summary = []
    for repo in github_data.get("repos", [])[:15]:
        repos_summary.append({
            "name": repo.get("name", ""),
            "description": repo.get("description", ""),
            "stars": repo.get("stars", 0),
            "language": repo.get("language", ""),
            "topics": repo.get("topics", []),
            "has_readme": repo.get("has_readme", False),
            "readme_snippet": repo.get("readme_content", "")[:300]
        })
    
    # Build analysis prompt
    prompt = f"""You are a senior engineering recruiter at {company} evaluating a candidate for {domain} roles.

Here are their GitHub projects:
{json.dumps(repos_summary, indent=2)}

GitHub Profile Summary:
- Total repositories: {github_data.get('total_repos_fetched', 0)}
- Followers: {github_data.get('followers', 0)}
- Total stars: {github_data.get('total_stars', 0)}
- Top languages: {', '.join([lang for lang, _ in github_data.get('top_languages', [])[:5]])}

Please provide a JSON response with:
1. "quality_score" (0-100): Overall GitHub quality assessment
2. "strongest_projects" (array of 3 project names): Best portfolios pieces
3. "weak_spots" (array of strings): Issues or gaps observed
4. "projects_to_build" (array of 3 objects with "title", "stack", "impact"): Specific projects to build
5. "skills_to_learn" (array of 5 strings): Priority skills ranked by importance
6. "recommendations" (string): Specific actionable advice

Return valid JSON only, no markdown or extra text."""
    
    system = """You are a technical career advisor and recruiting expert. 
    Provide actionable, specific feedback based on portfolio assessment.
    Always respond with valid JSON only - no markdown formatting."""
    
    # Get analysis from Ollama
    response_text = ollama_chat(prompt, system=system, model=model)
    analysis = _extract_json_block(response_text)

    if not analysis:
        analysis = _fallback_github_analysis(github_data, domain, company)

    return {
        "success": True,
        "analysis": analysis,
        "model": model,
        "source": "ollama" if not response_text.startswith("Error:") else "fallback"
    }


def _fallback_roadmap(
    skill_gap: Dict[str, Any],
    github_analysis: Dict[str, Any],
    domain: str,
    company: str,
    resume_data: Dict[str, Any]
) -> Dict[str, Any]:
    missing_skills = skill_gap.get("must_have", {}).get("missing", [])[:5]
    focus_skills = skill_gap.get("good_to_have", {}).get("missing", [])[:5]
    github_quality = _resolve_github_quality(github_analysis)
    experience_years = resume_data.get("experience_years", 0)

    return {
        "title": f"90-day {domain.title()} plan for {company}",
        "summary": f"A focused 12-week plan built from your current skills, GitHub signal, and the {company} target role.",
        "current_context": {
            "experience_years": experience_years,
            "github_quality": github_quality,
            "critical_gaps": missing_skills[:3]
        },
        "phases": [
            {
                "name": "Weeks 1-4",
                "goal": "Fix resume gaps and stabilize core skills",
                "actions": [
                    "Rewrite the resume summary and skills section for the target role.",
                    f"Learn: {', '.join(missing_skills[:3]) if missing_skills else 'core domain fundamentals'}.",
                    "Ship one small project or feature with a public README and screenshots."
                ]
            },
            {
                "name": "Weeks 5-8",
                "goal": "Build one portfolio-worthy project",
                "actions": [
                    f"Build a {domain} project aligned with {company} requirements.",
                    f"Practice deeper skills: {', '.join(focus_skills[:3]) if focus_skills else 'testing, deployment, and design'}.",
                    "Add deployment evidence and a short case study."
                ]
            },
            {
                "name": "Weeks 9-12",
                "goal": "Interview readiness and job search",
                "actions": [
                    "Run mock interviews and review system design basics.",
                    "Tailor the resume for each application using ATS keywords.",
                    "Apply to roles with the highest job match score first."
                ]
            }
        ],
        "weekly_commitment_hours": 12,
        "success_metrics": [
            "ATS score above 80",
            "One production-ready project shipped",
            "Resume keywords aligned to target jobs",
            "Interview stories prepared for key achievements"
        ]
    }


def generate_career_roadmap(
    skill_gap: Dict[str, Any],
    github_analysis: Dict[str, Any],
    domain: str,
    company: str,
    resume_data: Dict[str, Any],
    model: str = DEFAULT_MODEL
) -> str:
    """
    Generate personalized 90-day career roadmap using Ollama.
    
    Args:
        skill_gap: Skill gap analysis result
        github_analysis: GitHub analysis result
        domain: Target domain
        company: Target company
        resume_data: Resume parsing result
        model: Ollama model to use
    
    Returns:
        Generated career roadmap object
    """
    # Prepare context
    missing_skills = skill_gap.get("must_have", {}).get("missing", [])[:5]
    github_quality = _resolve_github_quality(github_analysis)
    experience_years = resume_data.get("experience_years", 0)
    user_skills = ", ".join(resume_data.get("skills", [])[:10])
    
    prompt = f"""You are HirePath AI, a career coach helping someone transition into {domain} at {company}.

Current Situation:
- Current experience: {experience_years} years
- Core skills: {user_skills}
- GitHub quality: {github_quality}/100
- Target: Get hired at {company} as a {domain} engineer
- Timeline: 90 days (3 months) to significantly improve candidacy
- Critical skill gaps: {', '.join(missing_skills[:3]) if missing_skills else 'Minor gaps'}

Create a personalized, actionable 90-day career acceleration plan:

**PHASE 1: Foundation (Days 1-30)**
- Immediate resume fixes
- 2-3 foundational skills to prioritize
- Specific learning resources with time commitment
- Small project to start

**PHASE 2: Building (Days 31-60)**
- One major project to build (specify title, tech stack, key features, why it matters)
- Skills to deepen
- Open source contribution target
- Interview prep start

**PHASE 3: Polish (Days 61-90)**
- Portfolio refinement
- Advanced skill focus
- Mock interview practice
- Final resume optimization
- Job search strategy

For each section, include:
- Concrete milestones (what to complete by day 15, 30, etc.)
- Specific learning resources (courses, articles, projects)
- Time commitment per week
- Success metrics

Be specific, realistic, and motivating. Use exact company/domain knowledge."""
    
    system = """You are an expert career coach specializing in tech hiring.
    Create practical, personalized roadmaps with specific actions and timelines.
    Be concise but comprehensive."""
    
    roadmap_text = ollama_chat(prompt, system=system, model=model)
    parsed = _extract_json_block(roadmap_text)
    if parsed:
        return parsed

    return _fallback_roadmap(skill_gap, github_analysis, domain, company, resume_data)


def _fallback_interview_prep(domain: str, company: str, skill_gap: Dict[str, Any]) -> Dict[str, Any]:
    missing_topics = skill_gap.get("good_to_have", {}).get("missing", [])[:5]
    return {
        "title": f"{domain.title()} interview prep for {company}",
        "technical_topics": [
            f"Review the top missing areas: {', '.join(missing_topics) if missing_topics else 'core domain concepts'}.",
            "Be ready to explain architecture decisions and tradeoffs.",
            "Practice debugging and implementation questions in your primary stack."
        ],
        "system_design": [
            "How would you design a scalable version of your best project?",
            "How do you handle authentication, caching, and background jobs?",
            "What metrics would you track after release?"
        ],
        "behavioral": [
            "Tell me about a time you shipped under pressure.",
            "Describe a conflict in a team project and how you resolved it.",
            "Share a project where you improved performance or quality."
        ],
        "company_research": [
            f"Study {company}'s products, engineering blog, and recent launches.",
            "Map your experience to the company values and domain priorities."
        ],
        "mock_plan": [
            "2 coding sessions per week",
            "1 system design session per week",
            "1 behavioral rehearsal with a timer"
        ],
        "final_week": [
            "Review resume bullets and metrics.",
            "Prepare a 60-second introduction and project walkthrough.",
            "Practice salary and role questions."
        ]
    }


def generate_interview_prep(
    domain: str,
    company: str,
    skill_gap: Dict[str, Any],
    model: str = DEFAULT_MODEL
) -> str:
    """
    Generate interview preparation guide.
    
    Args:
        domain: Target domain
        company: Target company
        skill_gap: Skill gap analysis
        model: Ollama model to use
    
    Returns:
        Interview prep guide
    """
    missing_topics = skill_gap.get("good_to_have", {}).get("missing", [])[:3]
    
    prompt = f"""Create a focused interview preparation guide for a {domain} role at {company}.

Areas of focus: {', '.join(missing_topics) if missing_topics else 'General domain preparation'}

Structure your response with:

1. **Technical Topics to Study** (with resources)
2. **System Design Focus** (key concepts, patterns)
3. **Coding Practice** (specific topics, difficulty level)
4. **Behavioral Questions** (company-specific, prepare 5 stories)
5. **Company Culture Questions** (research areas, good answers)
6. **Mock Interview Strategy** (how to practice)
7. **Final Week Preparation** (timeline and focus)

Be specific with resources, difficulty levels, and time estimates."""
    
    system = "You are an expert interview coach for tech roles. Provide actionable, specific guidance."
    
    guide_text = ollama_chat(prompt, system=system, model=model)
    parsed = _extract_json_block(guide_text)
    if parsed:
        return parsed

    return _fallback_interview_prep(domain, company, skill_gap)


def optimize_bullet_point(
    bullet: str,
    domain: str,
    keywords_to_inject: list,
    model: str = DEFAULT_MODEL
) -> str:
    """
    Use Ollama to optimize a single resume bullet point.
    
    Args:
        bullet: Original bullet point
        domain: Resume domain context
        keywords_to_inject: Keywords to naturally include
        model: Ollama model to use
    
    Returns:
        Optimized bullet point
    """
    keywords_str = ", ".join(keywords_to_inject[:5])
    
    prompt = f"""Rewrite this resume bullet point to be more impactful for a {domain} role:

Original: {bullet}

Requirements:
- Start with a strong action verb
- Include quantifiable metrics if possible
- Naturally incorporate these keywords if relevant: {keywords_str}
- Keep it concise (one line)
- Emphasize impact and outcome

Return only the optimized bullet point, nothing else."""
    
    system = "You are a resume expert optimizing content for ATS and human readers."
    
    optimized = ollama_chat(prompt, system=system, model=model)
    return optimized.strip()


def validate_ollama_model(model_name: str) -> bool:
    """
    Verify if a specific Ollama model is available.
    
    Args:
        model_name: Name of the model to check
    
    Returns:
        True if model is available
    """
    available = list_available_models()
    return any(model_name in m for m in available)


if __name__ == "__main__":
    print("Ollama client module loaded successfully")
    print(f"Ollama base URL: {OLLAMA_BASE_URL}")
    print(f"Default model: {DEFAULT_MODEL}")
    
    # Check connection
    if check_ollama_connection():
        print("✓ Ollama is running")
        models = list_available_models()
        print(f"Available models: {models}")
    else:
        print("✗ Ollama is not running. Start it with: ollama serve")

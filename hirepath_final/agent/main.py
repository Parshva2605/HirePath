"""
FastAPI backend - HirePath main orchestrator
Coordinates resume parsing, GitHub fetching, ATS scoring, and analysis
"""

import os
import tempfile
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import all HirePath modules
from resume_parser import parse_resume
from github_fetcher import fetch_github_data, validate_github_profile
from ats_scorer import calculate_ats_score
from skill_gap import compute_skill_gap, generate_learning_path
from ollama_client import (
    check_ollama_connection,
    analyze_github_projects,
    generate_career_roadmap,
    generate_interview_prep
)
from resume_optimizer import prepare_optimization_payload
from job_matcher import match_jobs, get_top_missing_skills_across_jobs, find_reachable_jobs, get_job_match_summary


# Initialize FastAPI app
app = FastAPI(
    title="HirePath API",
    description="Career acceleration platform combining resume analysis, GitHub evaluation, and job matching",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_FOLDER = Path(__file__).parent.parent / "resume_uploads"
JOB_FOLDER = Path(__file__).parent.parent / "job_folder"
SKILL_GAP_DB = Path(__file__).parent.parent / "skill_gap_db"

UPLOAD_FOLDER.mkdir(exist_ok=True)
JOB_FOLDER.mkdir(exist_ok=True)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ollama_connected": check_ollama_connection()
    }


@app.post("/api/analyze")
async def analyze_profile(
    resume: UploadFile = File(...),
    domain: str = Form(...),
    company: str = Form(...),
    github_url: str = Form(...)
):
    """
    Full pipeline analysis endpoint.
    
    Args:
        resume: Uploaded PDF or DOCX resume
        domain: Target domain (aiml, devops, frontend, backend, etc.)
        company: Target company
        github_url: GitHub profile URL or username
    
    Returns:
        Complete analysis with scores, gaps, roadmap, and job matches
    """
    try:
        # ===== STEP 1: Parse Resume =====
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await resume.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            resume_data = parse_resume(tmp_path)
        finally:
            os.unlink(tmp_path)
        
        # ===== STEP 2: Fetch GitHub Profile =====
        github_data = None
        github_valid = validate_github_profile(github_url)
        
        if github_valid:
            try:
                github_data = fetch_github_data(github_url, fetch_details=False)
            except Exception as e:
                print(f"GitHub fetch error: {str(e)}")
                github_data = None
        
        # ===== STEP 3: Calculate ATS Score =====
        ats_result = calculate_ats_score(resume_data, domain)
        
        # ===== STEP 4: Skill Gap Analysis =====
        user_github_languages = github_data.get("top_languages", []) if github_data else []
        skill_gap = compute_skill_gap(
            user_skills=resume_data.get("skills", []),
            user_github_languages=user_github_languages,
            domain=domain,
            company=company,
            db_path=str(SKILL_GAP_DB)
        )
        
        # ===== STEP 5: GitHub Analysis (via Ollama) =====
        github_analysis = None
        if github_data and check_ollama_connection():
            try:
                github_analysis_result = analyze_github_projects(github_data, domain, company)
                github_analysis = github_analysis_result.get("analysis") if isinstance(github_analysis_result, dict) else github_analysis_result
            except Exception as e:
                print(f"GitHub analysis error: {str(e)}")
        
        # ===== STEP 6: Career Roadmap (via Ollama) =====
        career_roadmap = None
        if check_ollama_connection():
            try:
                career_roadmap = generate_career_roadmap(
                    skill_gap=skill_gap,
                    github_analysis=github_analysis or {},
                    domain=domain,
                    company=company,
                    resume_data=resume_data
                )
            except Exception as e:
                print(f"Roadmap generation error: {str(e)}")
        
        # ===== STEP 7: Resume Optimization Payload =====
        optimization_payload = prepare_optimization_payload(
            resume_data=resume_data,
            ats_score=ats_result,
            skill_gap=skill_gap,
            domain=domain,
            company=company
        )
        
        # ===== STEP 8: Job Matching =====
        matched_jobs = match_jobs(
            user_skills=resume_data.get("skills", []),
            domain=domain,
            job_folder=str(JOB_FOLDER),
            top_n=15
        )
        
        top_missing_skills = get_top_missing_skills_across_jobs(
            user_skills=resume_data.get("skills", []),
            matched_jobs=matched_jobs,
            top_n=10
        ) if matched_jobs else []
        
        reachable_jobs = find_reachable_jobs(
            matched_jobs=matched_jobs,
            learn_skills=skill_gap.get("must_have", {}).get("missing", [])[:5]
        ) if matched_jobs else []
        
        job_summary = get_job_match_summary(matched_jobs)
        
        # ===== STEP 9: Interview Prep =====
        interview_prep = None
        if check_ollama_connection():
            try:
                interview_prep = generate_interview_prep(
                    domain=domain,
                    company=company,
                    skill_gap=skill_gap
                )
            except Exception as e:
                print(f"Interview prep generation error: {str(e)}")
        
        # ===== STEP 10: Learning Path =====
        learning_path = generate_learning_path(skill_gap, timeframe_weeks=12)
        
        # ===== Compile Full Response =====
        github_profile_payload = None
        if github_data:
            github_profile_payload = {
                "username": github_data.get("username", ""),
                "profile_url": github_data.get("profile_url", ""),
                "followers": github_data.get("followers", 0),
                "public_repos": github_data.get("public_repos", 0),
                "top_languages": github_data.get("top_languages", []),
                "repos": [
                    {
                        "name": repo.get("name", ""),
                        "url": repo.get("url", ""),
                        "language": repo.get("language", ""),
                        "topics": repo.get("topics", []),
                        "stars": repo.get("stars", 0),
                        "description": repo.get("description", "")
                    }
                    for repo in github_data.get("repos", [])
                ]
            }

        return {
            "success": True,
            "profile": {
                "domain": domain,
                "company": company,
                "github_url": github_url,
                "resume_filename": resume.filename
            },
            "ats_score": ats_result,
            "skill_gap": skill_gap,
            "github_profile": github_profile_payload,
            "github_analysis": github_analysis,
            "career_roadmap": career_roadmap,
            "learning_path": learning_path,
            "resume_optimization": optimization_payload,
            "job_matches": {
                "total": len(matched_jobs),
                "jobs": matched_jobs,
                "summary": job_summary,
                "top_missing_skills": top_missing_skills,
                "reachable_with_learning": reachable_jobs
            },
            "interview_preparation": interview_prep,
            "next_steps": {
                "resume_optimizer_url": "http://localhost:3000/hirepath/optimize",
                "job_search_tracker": "http://localhost:3000/hirepath/jobs",
                "skill_tracker": "http://localhost:3000/hirepath/skills"
            },
            "ollama_status": {
                "connected": check_ollama_connection(),
                "required_for_ai_features": True
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/api/ats-check")
async def quick_ats_check(resume: UploadFile = File(...), domain: str = Form(...)):
    """Quick ATS score check without full analysis"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await resume.read())
            tmp_path = tmp.name
        
        try:
            resume_data = parse_resume(tmp_path)
            ats_result = calculate_ats_score(resume_data, domain)
            return {"success": True, "ats_score": ats_result}
        finally:
            os.unlink(tmp_path)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/skill-gap")
async def skill_gap_analysis(
    user_skills: str = Form(...),
    domain: str = Form(...),
    company: Optional[str] = Form(None)
):
    """
    Check skill gaps for given skills and domain/company.
    
    Args:
        user_skills: Comma-separated list of skills
        domain: Target domain
        company: Target company (optional)
    """
    try:
        skills_list = [s.strip() for s in user_skills.split(",")]
        
        gap = compute_skill_gap(
            user_skills=skills_list,
            user_github_languages=[],
            domain=domain,
            company=company,
            db_path=str(SKILL_GAP_DB)
        )
        
        return {"success": True, "skill_gap": gap}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/domains")
async def list_domains():
    """List all available domains"""
    domains_path = SKILL_GAP_DB / "domains"
    domains = []
    
    if domains_path.exists():
        for f in domains_path.glob("*.json"):
            domain_name = f.stem
            domains.append(domain_name)
    
    return {"domains": sorted(domains)}


@app.get("/api/companies")
async def list_companies():
    """List all configured companies"""
    companies_path = SKILL_GAP_DB / "companies"
    companies = []
    
    if companies_path.exists():
        for f in companies_path.glob("*.json"):
            company_name = f.stem
            companies.append(company_name)
    
    return {"companies": sorted(companies)}


@app.get("/api/jobs-stats")
async def job_statistics():
    """Return job listing statistics"""
    jobs_list = []
    
    if JOB_FOLDER.exists():
        for f in JOB_FOLDER.glob("**/*.json"):
            try:
                with open(f) as reader:
                    data = json.load(reader)
                    if isinstance(data, list):
                        jobs_list.extend(data)
                    else:
                        jobs_list.append(data)
            except:
                pass
    
    domains = set(job.get("domain", "unknown") for job in jobs_list)
    companies = set(job.get("company", "unknown") for job in jobs_list)
    
    return {
        "total_jobs": len(jobs_list),
        "unique_companies": len(companies),
        "unique_domains": len(domains),
        "domains": list(domains),
        "top_companies": sorted(list(companies))[:10]
    }


@app.get("/api/status")
async def system_status():
    """Check system status and dependencies"""
    return {
        "backend": "running",
        "resume_analyzer": "ready",
        "github_fetcher": "ready",
        "ats_scorer": "ready",
        "skill_gap_analyzer": "ready",
        "job_matcher": "ready",
        "ollama_backend": {
            "connected": check_ollama_connection(),
            "features": ["GitHub analysis", "Career roadmap", "Interview prep"]
        },
        "dependencies": {
            "resume_uploads_folder": UPLOAD_FOLDER.exists(),
            "job_folder": JOB_FOLDER.exists(),
            "skill_gap_db": SKILL_GAP_DB.exists()
        }
    }


@app.post("/api/validate-github")
async def validate_github(github_url: str = Form(...)):
    """Validate if GitHub profile is accessible"""
    try:
        is_valid = validate_github_profile(github_url)
        return {"valid": is_valid, "url": github_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("⭐ HirePath FastAPI Server")
    print("📍 Starting on http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
GitHub Profile Analyzer - Main FastAPI Application
File: app/main.py
"""
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from dotenv import load_dotenv
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import our modules
try:
    from app.github_fetcher import GitHubFetcher
    from app.analyzer import ProfileAnalyzer
    from app.llm_client import OllamaClient
    from app.models import AnalysisRequest, AnalysisResult
    from app.repo_analyzer import RepositoryAnalyzer
    from app.enhanced_analyzer import EnhancedProfileAnalyzer
except ImportError:
    # Fallback to relative imports
    from github_fetcher import GitHubFetcher
    from analyzer import ProfileAnalyzer
    from llm_client import OllamaClient
    from models import AnalysisRequest, AnalysisResult
    from repo_analyzer import RepositoryAnalyzer
    from enhanced_analyzer import EnhancedProfileAnalyzer

# Initialize FastAPI app
app = FastAPI(
    title="GitHub Profile Analyzer",
    description="AI-powered GitHub profile analysis and career recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
github_token = os.getenv("GITHUB_TOKEN")
github_fetcher = GitHubFetcher(token=github_token)
analyzer = ProfileAnalyzer()
llm_client = OllamaClient()
repo_analyzer = RepositoryAnalyzer()
enhanced_analyzer = EnhancedProfileAnalyzer()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ollama_status": llm_client.check_connection()
    })


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_connected = llm_client.check_connection()
    github_rate_limit = github_fetcher.get_rate_limit()
    
    return {
        "status": "healthy",
        "github_api": {
            "authenticated": bool(github_token),
            "rate_limit": github_rate_limit
        },
        "ollama": {
            "connected": ollama_connected,
            "host": llm_client.host,
            "model": llm_client.model
        }
    }


@app.post("/analyze")
async def analyze_profile(
    github_url: str = Form(...),
    target_domain: str = Form(...),
    target_companies: str = Form(...)
):
    """Analyze GitHub profile and return comprehensive results"""
    try:
        # Parse target companies
        companies_list = [c.strip() for c in target_companies.split(",") if c.strip()]
        
        print(f"Analyzing: {github_url}")
        print(f"Domain: {target_domain}")
        print(f"Companies: {companies_list}")
        
        # Step 1: Fetch GitHub data
        print("Fetching GitHub profile data...")
        profile_data = github_fetcher.fetch_profile_data(github_url)
        
        print(f"✅ Fetched {len(profile_data['repositories'])} repositories")
        print(f"📊 API calls used: {profile_data.get('api_calls_used', 'N/A')}")
        print(f"⚡ API calls remaining: {profile_data.get('api_calls_remaining', 'N/A')}")
        
        # Step 2: Analyze each repository in detail
        print("Analyzing repositories...")
        analyzed_repos = []
        for repo in profile_data["repositories"]:
            analyzed_repo = repo_analyzer.analyze_repository(repo)
            analyzed_repos.append(analyzed_repo)
        
        # Get domain distribution and quality summary
        domain_distribution = repo_analyzer.get_domain_distribution(analyzed_repos)
        quality_summary = repo_analyzer.get_quality_summary(analyzed_repos)
        
        # Step 3: Enhanced profile analysis with better scoring
        print("Calculating enhanced rating...")
        enhanced_rating = enhanced_analyzer.calculate_enhanced_rating(
            profile_data,
            analyzed_repos,
            target_domain
        )
        
        # Step 4: Analyze strengths and weaknesses using enhanced scoring
        print("Analyzing profile strengths and weaknesses...")
        strengths, weaknesses = _analyze_strengths_weaknesses(
            profile_data,
            analyzed_repos,
            enhanced_rating,
            target_domain
        )
        
        # Company alignment
        company_alignment = _analyze_company_alignment(
            profile_data,
            analyzed_repos,
            companies_list
        )
        
        # Step 5: Generate AI recommendations based on detailed analysis
        print("Generating AI recommendations...")
        ai_recommendations = llm_client.generate_recommendations(
            profile_data,
            {
                "overall_rating": enhanced_rating["overall_rating"],
                "rating_breakdown": enhanced_rating["breakdown"],
                "strengths": strengths,
                "weaknesses": weaknesses,
                "company_alignment": company_alignment,
                "analyzed_repos": analyzed_repos[:5],  # Top 5 repos for context
                "domain_distribution": domain_distribution,
                "quality_summary": quality_summary
            },
            target_domain,
            companies_list
        )
        
        # Combine results
        # Convert top repos with detailed analysis
        top_repos_detailed = sorted(
            [r for r in analyzed_repos if not r["is_fork"]],
            key=lambda x: x["stars"],
            reverse=True
        )[:10]  # Top 10 repos
        
        result = {
            "success": True,
            "profile_data": {
                "username": profile_data["username"],
                "name": profile_data["name"],
                "bio": profile_data["bio"],
                "location": profile_data["location"],
                "followers": profile_data["followers"],
                "following": profile_data["following"],
                "public_repos": profile_data["public_repos"],
                "total_stars": profile_data["total_stars"],
                "total_forks": profile_data["total_forks"],
                "languages": profile_data["languages"]
            },
            # Enhanced rating (new, improved scoring)
            "overall_rating": enhanced_rating["overall_rating"],
            "rating_breakdown": enhanced_rating["breakdown"],
            
            # API usage tracking
            "api_usage": {
                "calls_used": profile_data.get("api_calls_used", 0),
                "calls_remaining": profile_data.get("api_calls_remaining", 0),
                "total_repos_analyzed": len(analyzed_repos)
            },
            
            # Detailed repository analysis (NEW!)
            "repository_analysis": {
                "top_repositories": top_repos_detailed,
                "domain_distribution": domain_distribution,
                "quality_summary": quality_summary,
                "total_analyzed": len(analyzed_repos),
                "original_repos": len([r for r in analyzed_repos if not r["is_fork"]])
            },
            
            # Strengths and weaknesses
            "strengths": strengths,
            "weaknesses": weaknesses,
            "company_alignment": company_alignment,
            "project_recommendations": ai_recommendations["project_recommendations"],
            "improvement_suggestions": ai_recommendations["improvement_suggestions"]
        }
        
        print("Analysis complete!")
        return JSONResponse(content=result)
        
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Internal server error: {str(e)}"}
        )


def _analyze_strengths_weaknesses(profile_data: Dict, analyzed_repos: List[Dict], 
                                  enhanced_rating: Dict, target_domain: str):
    """Analyze specific strengths and weaknesses based on enhanced rating"""
    strengths = []
    weaknesses = []
    breakdown = enhanced_rating["breakdown"]
    
    # Repository Impact
    if breakdown["repository_impact"] >= 25:
        strengths.append(f"Strong repository portfolio with {profile_data['total_stars']} total stars")
    elif breakdown["repository_impact"] < 15:
        weaknesses.append(f"Low repository impact - consider building more starred projects")
    
    # Community Engagement
    if breakdown["community_engagement"] >= 18:
        strengths.append(f"Excellent community engagement with {profile_data['followers']} followers")
    elif breakdown["community_engagement"] < 12:
        weaknesses.append(f"Limited community presence - engage more with the developer community")
    
    # Tech Stack Alignment
    domain_repos = [r for r in analyzed_repos if target_domain.lower() in r["domain"].lower()]
    if breakdown["tech_stack_alignment"] >= 14:
        strengths.append(f"Well-aligned with {target_domain} - {len(domain_repos)} relevant repositories")
    elif breakdown["tech_stack_alignment"] < 10:
        weaknesses.append(f"Technology stack needs better alignment with {target_domain} - only {len(domain_repos)} relevant repositories found. Build projects specifically using {target_domain} technologies and frameworks")
    
    # Project Quality
    high_quality = [r for r in analyzed_repos if r["quality_stars"] >= 4.0 and not r["is_fork"]]
    if breakdown["project_quality"] >= 11:
        strengths.append(f"High-quality projects - {len(high_quality)} repositories rated 4+ stars")
    elif breakdown["project_quality"] < 8:
        weaknesses.append(f"Project quality needs improvement - add better documentation, topics, and polish to repositories")
    
    # Activity
    if breakdown["activity_consistency"] >= 3.5:
        strengths.append("Consistent development activity and contributions")
    elif breakdown["activity_consistency"] < 2:
        weaknesses.append("Inconsistent activity - maintain regular contributions")
    
    return strengths, weaknesses


def _analyze_company_alignment(profile_data: Dict, analyzed_repos: List[Dict], 
                               target_companies: List[str]):
    """Analyze alignment with target companies"""
    alignment = {}
    
    for company in target_companies:
        score = 50  # Base score
        feedback = []
        
        company_lower = company.lower()
        
        # Check for relevant tech stack
        if company_lower == "microsoft":
            azure_repos = [r for r in analyzed_repos if any(tech in r["domain"].lower() or tech in str(r.get("topics", [])).lower() 
                          for tech in ["azure", "dotnet", ".net", "c#", "typescript"])]
            score += min(len(azure_repos) * 5, 30)
            if azure_repos:
                feedback.append(f"✓ {len(azure_repos)} projects using Microsoft technologies")
            else:
                feedback.append("× Build projects with Azure, .NET, or TypeScript")
        
        elif company_lower == "google":
            google_repos = [r for r in analyzed_repos if any(tech in r["domain"].lower() or tech in str(r.get("topics", [])).lower() 
                           for tech in ["tensorflow", "kubernetes", "golang", "android", "angular", "firebase"])]
            score += min(len(google_repos) * 5, 30)
            if google_repos:
                feedback.append(f"✓ {len(google_repos)} projects using Google technologies")
            else:
                feedback.append("× Build projects with TensorFlow, Kubernetes, or Go")
        
        # Stars and followers bonus
        if profile_data["total_stars"] >= 1000:
            score += 10
            feedback.append("✓ Strong open-source presence")
        
        if profile_data["followers"] >= 200:
            score += 10
            feedback.append("✓ Good community following")
        
        alignment[company] = {
            "score": min(score, 100),
            "feedback": feedback
        }
    
    return alignment


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    
    print("=" * 70)
    print("  GITHUB PROFILE ANALYZER")
    print("=" * 70)
    print(f"\n🚀 Starting server on http://localhost:{port}")
    print(f"\n📊 GitHub API: {'✓ Authenticated' if github_token else '✗ Not authenticated (rate limited)'}")
    print(f"🤖 Ollama: {'✓ Connected' if llm_client.check_connection() else '✗ Not connected'}")
    print("\n" + "=" * 70)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)

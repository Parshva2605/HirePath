"""
GitHub Profile Analyzer - Ollama LLM Integration
File: app/llm_client.py

This module handles communication with the local Ollama LLM for generating
AI-powered project recommendations and improvement suggestions.
"""
import requests
import json
from typing import List, Dict, Optional
import os


class OllamaClient:
    """Client for interacting with local Ollama LLM"""
    
    def __init__(self, host: str = None, model: str = None):
        """Initialize Ollama client"""
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama2")
        self.api_url = f"{self.host}/api/generate"
    
    def check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_recommendations(self, profile_data: Dict, analysis: Dict, 
                                target_domain: str, target_companies: List[str]) -> Dict:
        """Generate project recommendations and improvement suggestions"""
        
        if not self.check_connection():
            print("⚠️ Ollama not connected, using fallback recommendations")
            return self._fallback_recommendations(target_domain)
        
        # Prepare context for LLM
        context = self._prepare_context(profile_data, analysis, target_domain, target_companies)
        
        # Generate recommendations
        try:
            print("🤖 Generating AI recommendations...")
            recommendations = self._generate_projects(context, target_domain)
            improvements = self._generate_improvements(context)
            
            return {
                "project_recommendations": recommendations,
                "improvement_suggestions": improvements
            }
        except Exception as e:
            print(f"❌ LLM generation error: {e}")
            return self._fallback_recommendations(target_domain)
    
    def _prepare_context(self, profile_data: Dict, analysis: Dict, 
                        target_domain: str, target_companies: List[str]) -> str:
        """Prepare context for LLM prompt"""
        languages = ", ".join(profile_data["languages"].keys()) if profile_data["languages"] else "None"
        
        # Get detailed repository analysis if available
        top_repos_info = ""
        if "analyzed_repos" in analysis:
            top_repos_info = "\n\nTop Repositories:"
            for repo in analysis["analyzed_repos"][:5]:
                top_repos_info += f"\n- {repo['name']}: {repo['domain']} ({repo['quality_stars']:.1f}⭐, {repo['stars']} stars)"
        
        # Get domain distribution if available
        domain_info = ""
        if "domain_distribution" in analysis:
            domain_info = "\n\nDomain Distribution:"
            for domain, count in analysis["domain_distribution"].items():
                domain_info += f"\n- {domain}: {count} projects"
        
        # Get quality summary if available
        quality_info = ""
        if "quality_summary" in analysis:
            qs = analysis["quality_summary"]
            quality_info = f"\n\nQuality Metrics:"
            quality_info += f"\n- Average Quality: {qs['average_quality_stars']:.1f}/5.0 stars"
            quality_info += f"\n- High-Quality Projects: {qs['high_quality_repos']}"
            quality_info += f"\n- Quality Rate: {qs['quality_percentage']:.0f}%"
        
        context = f"""GitHub Profile Analysis:
- Username: {profile_data["username"]}
- Primary Languages: {languages}
- Total Repositories: {profile_data["public_repos"]}
- Total Stars: {profile_data["total_stars"]}
- Followers: {profile_data["followers"]}
- Overall Rating: {analysis["overall_rating"]}/100
- Target Domain: {target_domain}
- Target Companies: {", ".join(target_companies) if target_companies else "None"}

Rating Breakdown:
- Repository Impact: {analysis["rating_breakdown"]["repository_impact"]}/35
- Community Engagement: {analysis["rating_breakdown"]["community_engagement"]}/25
- Tech Stack Alignment: {analysis["rating_breakdown"]["tech_stack_alignment"]}/20
- Project Quality: {analysis["rating_breakdown"]["project_quality"]}/15
- Activity Consistency: {analysis["rating_breakdown"]["activity_consistency"]}/5

Strengths:
{chr(10).join(f"- {s}" for s in analysis["strengths"])}

Weaknesses:
{chr(10).join(f"- {w}" for w in analysis["weaknesses"])}
{top_repos_info}
{domain_info}
{quality_info}
"""
        return context
    
    def _generate_projects(self, context: str, target_domain: str) -> List[Dict]:
        """Generate project recommendations using LLM"""
        # Extract values before f-string (can't use backslash in f-string)
        tech_alignment_line = [line for line in context.split('\n') if 'Tech Stack Alignment:' in line]
        tech_score = tech_alignment_line[0].split(':')[1].split('/')[0].strip() if tech_alignment_line else "unknown"
        
        companies_line = [line for line in context.split('\n') if 'Target Companies:' in line]
        companies = companies_line[0].split(':')[1].strip() if companies_line else "unknown"
        
        prompt = f"""{context}

Based on this SPECIFIC GitHub profile analysis, suggest 3 personalized project ideas that:
1. Target the EXACT weaknesses identified (especially tech stack alignment score of {tech_score}/20)
2. Fill gaps in the current domain distribution
3. Use technologies that the target companies ({companies}) actively use
4. Build on existing strengths while addressing weaknesses

IMPORTANT: Be SPECIFIC to THIS profile. Don't give generic advice!
- If weak in {target_domain}, suggest projects that directly demonstrate {target_domain} skills
- If missing certain technologies, recommend projects using those exact technologies
- If low quality score, suggest projects with strong documentation and testing

For each project, provide in this exact JSON format:
[
  {{
    "title": "Project name",
    "description": "2-3 sentence description explaining HOW it addresses their specific gaps",
    "technologies": ["tech1", "tech2", "tech3"],
    "difficulty": "Beginner|Intermediate|Advanced",
    "impact": "SPECIFIC impact on THIS profile's rating (which score it improves)",
    "reasoning": "Why THIS user needs THIS project (reference their specific stats)"
  }}
]

Provide ONLY the JSON array, no other text.
"""
        
        try:
            response = self._call_ollama(prompt)
            projects = self._parse_project_json(response)
            if projects and len(projects) >= 1:
                return projects
        except Exception as e:
            print(f"⚠️ Project generation failed: {e}")
        
        return self._fallback_projects(target_domain)
    
    def _generate_improvements(self, context: str) -> List[str]:
        """Generate improvement suggestions using LLM"""
        prompt = f"""{context}

Based on this analysis, provide 5 specific, actionable improvement suggestions that will:
1. Address the identified weaknesses
2. Increase chances of getting hired at target companies
3. Improve the overall profile rating
4. Be practical and achievable

Provide suggestions as a simple numbered list:
1. First suggestion
2. Second suggestion
(etc.)
"""
        
        try:
            response = self._call_ollama(prompt, max_tokens=800)
            improvements = self._parse_improvements(response)
            if improvements and len(improvements) >= 3:
                return improvements[:5]
        except Exception as e:
            print(f"⚠️ Improvement generation failed: {e}")
        
        return self._fallback_improvements("")
    
    def _call_ollama(self, prompt: str, max_tokens: int = 2000) -> str:
        """Call Ollama API"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(self.api_url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    def _parse_project_json(self, response: str) -> List[Dict]:
        """Parse project recommendations from JSON response"""
        try:
            # Try to find JSON array in response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                projects = json.loads(json_str)
                
                # Validate and format
                formatted = []
                for p in projects[:3]:  # Take top 3
                    if isinstance(p, dict) and "title" in p and "description" in p:
                        # Handle technologies being string or list
                        techs = p.get("technologies", [])
                        if isinstance(techs, str):
                            techs = [t.strip() for t in techs.split(",")]
                        
                        formatted.append({
                            "title": p["title"],
                            "description": p["description"],
                            "technologies": techs if isinstance(techs, list) else [],
                            "difficulty": p.get("difficulty", "Intermediate"),
                            "impact": p.get("impact", "Demonstrates relevant skills"),
                            "reasoning": p.get("reasoning", "Aligns with career goals")
                        })
                
                if formatted:
                    return formatted
        except Exception as e:
            print(f"⚠️ JSON parsing failed: {e}")
        
        return []
    
    def _parse_improvements(self, response: str) -> List[str]:
        """Parse improvement suggestions from response"""
        improvements = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Remove numbering, bullets, etc.
            line = line.lstrip('0123456789.-*• ')
            if len(line) > 15 and not line.startswith('{') and not line.startswith('['):
                improvements.append(line)
        
        return improvements[:5] if improvements else []
    
    def _fallback_projects(self, domain: str) -> List[Dict]:
        """Fallback project recommendations when LLM fails"""
        
        domain_projects = {
            "AI/ML": [
                {
                    "title": "AI-Powered Code Reviewer",
                    "description": "Build an ML model that reviews code quality, suggests improvements, and detects bugs using NLP and static analysis. Include a web interface for uploading code and viewing suggestions.",
                    "technologies": ["Python", "PyTorch", "Transformers", "FastAPI", "Docker"],
                    "difficulty": "Advanced",
                    "impact": "Demonstrates ML engineering skills highly valued at top tech companies",
                    "reasoning": "Combines AI/ML with practical software engineering - shows you can build production ML systems"
                },
                {
                    "title": "Real-time Sentiment Analysis Dashboard",
                    "description": "Create a dashboard that analyzes sentiment from Twitter/Reddit streams using transformer models and visualizes trends in real-time with interactive charts.",
                    "technologies": ["Python", "Streamlit", "Hugging Face", "Redis", "PostgreSQL"],
                    "difficulty": "Intermediate",
                    "impact": "Shows data pipeline and ML deployment skills critical for ML Engineer roles",
                    "reasoning": "Real-world ML application with production components like streaming and databases"
                },
                {
                    "title": "RAG-based Document Q&A System",
                    "description": "Build a conversational AI that answers questions about uploaded documents using Retrieval Augmented Generation with open-source LLMs and vector databases.",
                    "technologies": ["Python", "LangChain", "Ollama", "ChromaDB", "FastAPI"],
                    "difficulty": "Advanced",
                    "impact": "Directly relevant to LLM engineering roles at AI-focused companies",
                    "reasoning": "RAG is a hot technology - demonstrates cutting-edge AI application skills"
                }
            ],
            "DevOps": [
                {
                    "title": "Kubernetes Multi-Cloud Deployment Tool",
                    "description": "Build a CLI tool that automates application deployment across AWS, GCP, and Azure with unified configuration, health checks, and rollback capabilities.",
                    "technologies": ["Go", "Kubernetes", "Terraform", "Docker", "Helm"],
                    "difficulty": "Advanced",
                    "impact": "Showcases cloud-native expertise essential for DevOps Engineer roles",
                    "reasoning": "Solves real multi-cloud challenges that companies face"
                },
                {
                    "title": "Infrastructure Cost Optimizer",
                    "description": "Create a tool that analyzes cloud resource usage across AWS/GCP/Azure and automatically suggests cost optimizations, right-sizing, and unused resource cleanup.",
                    "technologies": ["Python", "AWS SDK", "Prometheus", "Grafana", "PostgreSQL"],
                    "difficulty": "Intermediate",
                    "impact": "Addresses a major pain point for companies - demonstrates business value understanding",
                    "reasoning": "Cost optimization is critical for all cloud-using businesses"
                },
                {
                    "title": "GitOps CI/CD Pipeline Generator",
                    "description": "Build a tool that generates complete CI/CD pipelines following GitOps principles for any tech stack, with automated testing, security scanning, and deployment.",
                    "technologies": ["Python", "ArgoCD", "GitHub Actions", "Jenkins", "Docker"],
                    "difficulty": "Intermediate",
                    "impact": "Demonstrates automation expertise and DevOps best practices",
                    "reasoning": "GitOps is industry standard - shows you understand modern deployment workflows"
                }
            ],
            "Web Development": [
                {
                    "title": "Real-time Collaborative Code Editor",
                    "description": "Build a browser-based code editor with live collaboration, syntax highlighting, real-time cursor tracking, and integrated terminal support.",
                    "technologies": ["TypeScript", "React", "WebSocket", "Monaco Editor", "Node.js"],
                    "difficulty": "Advanced",
                    "impact": "Demonstrates full-stack and real-time systems expertise",
                    "reasoning": "Complex project showcasing WebSockets, state management, and UI/UX skills"
                },
                {
                    "title": "Progressive Web App E-commerce Platform",
                    "description": "Create a production-ready PWA e-commerce template with offline support, push notifications, payment integration, and modern performance optimizations.",
                    "technologies": ["TypeScript", "Next.js", "Service Workers", "Stripe", "Tailwind"],
                    "difficulty": "Intermediate",
                    "impact": "Shows modern web development skills valued at product companies",
                    "reasoning": "PWAs are increasingly important - demonstrates full product development capability"
                },
                {
                    "title": "Component Library with Design System",
                    "description": "Build a comprehensive, accessible React component library with Storybook documentation, automated visual regression testing, and published npm package.",
                    "technologies": ["TypeScript", "React", "Storybook", "Jest", "Chromatic"],
                    "difficulty": "Intermediate",
                    "impact": "Demonstrates component architecture and testing skills crucial at large companies",
                    "reasoning": "Design systems are essential infrastructure at companies like Google and Microsoft"
                }
            ],
            "Backend": [
                {
                    "title": "Distributed Task Queue System",
                    "description": "Build a scalable distributed task queue with priority scheduling, retry logic, dead letter queues, and monitoring dashboard.",
                    "technologies": ["Python", "Redis", "PostgreSQL", "FastAPI", "Docker"],
                    "difficulty": "Advanced",
                    "impact": "Shows understanding of distributed systems crucial for backend roles",
                    "reasoning": "Task queues are fundamental infrastructure at scale-up companies"
                },
                {
                    "title": "API Gateway with Rate Limiting",
                    "description": "Create a high-performance API gateway with authentication, rate limiting, request routing, and real-time analytics.",
                    "technologies": ["Go", "Redis", "PostgreSQL", "JWT", "Prometheus"],
                    "difficulty": "Advanced",
                    "impact": "Demonstrates backend architecture skills valued at infrastructure-heavy companies",
                    "reasoning": "API gateways are critical for microservices - shows system design capability"
                },
                {
                    "title": "Multi-tenant SaaS Boilerplate",
                    "description": "Build a production-ready SaaS boilerplate with multi-tenancy, subscription billing, user management, and admin dashboard.",
                    "technologies": ["Python", "FastAPI", "PostgreSQL", "Stripe", "Redis"],
                    "difficulty": "Intermediate",
                    "impact": "Shows ability to build complete backend systems for SaaS products",
                    "reasoning": "Multi-tenancy is a common requirement - demonstrates product engineering skills"
                }
            ],
            "Data Science": [
                {
                    "title": "Automated ML Pipeline Framework",
                    "description": "Build a framework for automated data preprocessing, feature engineering, model training, and evaluation with experiment tracking.",
                    "technologies": ["Python", "Scikit-learn", "MLflow", "Pandas", "Jupyter"],
                    "difficulty": "Intermediate",
                    "impact": "Shows ML operations skills needed for Data Science roles",
                    "reasoning": "AutoML and MLOps are growing areas - demonstrates practical ML engineering"
                },
                {
                    "title": "Interactive Data Visualization Dashboard",
                    "description": "Create a dashboard for exploring large datasets with interactive visualizations, statistical analysis, and automated insight generation.",
                    "technologies": ["Python", "Plotly", "Dash", "Pandas", "PostgreSQL"],
                    "difficulty": "Intermediate",
                    "impact": "Demonstrates data storytelling skills crucial for Data Scientists",
                    "reasoning": "Visualization and communication are key data science skills"
                },
                {
                    "title": "Predictive Analytics Platform",
                    "description": "Build a platform for time series forecasting with multiple models, automatic model selection, and confidence intervals.",
                    "technologies": ["Python", "Prophet", "ARIMA", "Streamlit", "PostgreSQL"],
                    "difficulty": "Advanced",
                    "impact": "Shows practical forecasting skills used across many industries",
                    "reasoning": "Time series is a common business need - demonstrates applied data science"
                }
            ]
        }
        
        # Return projects for the matched domain
        for key in domain_projects:
            if key.lower() in domain.lower():
                return domain_projects[key]
        
        # Default to AI/ML if no match
        return domain_projects.get("AI/ML", domain_projects["Web Development"])
    
    def _fallback_recommendations(self, target_domain: str) -> Dict:
        """Complete fallback when LLM is unavailable"""
        return {
            "project_recommendations": self._fallback_projects(target_domain),
            "improvement_suggestions": self._fallback_improvements("")
        }
    
    def _fallback_improvements(self, context: str) -> List[str]:
        """Fallback improvement suggestions"""
        return [
            "Add comprehensive README files to all major projects with setup instructions, architecture diagrams, and demo links or screenshots",
            "Contribute to 3-5 popular open-source projects in your target domain to build credibility and network with maintainers",
            "Create a detailed profile bio highlighting your expertise, tech stack, and career goals (include keywords recruiters search for)",
            "Implement CI/CD pipelines for your repositories using GitHub Actions with automated testing, linting, and deployment",
            "Add test coverage (aim for >80%) with coverage badges, and include comprehensive documentation for all public APIs",
            "Write technical blog posts or create video tutorials about your projects to demonstrate communication skills",
            "Create live demos or deployed versions of your projects - recruiters want to see working software, not just code"
        ]

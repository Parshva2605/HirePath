"""
GitHub Profile Analyzer - Profile Rating and Analysis Logic
File: app/analyzer.py

This module contains all the logic for rating GitHub profiles across multiple dimensions.
"""
from typing import Dict, List, Tuple
from collections import Counter
import math


class ProfileAnalyzer:
    """Analyze GitHub profiles and calculate ratings"""
    
    # Domain-specific technologies
    DOMAIN_TECHNOLOGIES = {
        "AI/ML": ["Python", "Jupyter Notebook", "TensorFlow", "PyTorch", "Keras", 
                  "scikit-learn", "pandas", "numpy", "OpenCV", "CUDA"],
        "DevOps": ["Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins", 
                   "Shell", "Python", "Go", "CI/CD", "AWS", "Azure", "GCP"],
        "Web Development": ["JavaScript", "TypeScript", "React", "Vue", "Angular", 
                           "Node.js", "HTML", "CSS", "Next.js", "Express"],
        "Backend": ["Python", "Java", "Go", "Node.js", "C#", "Ruby", "PHP", 
                   "Django", "Flask", "Spring", "FastAPI"],
        "Mobile": ["Swift", "Kotlin", "Java", "Dart", "React Native", "Flutter", 
                  "iOS", "Android"],
        "Data Science": ["Python", "R", "SQL", "Jupyter Notebook", "pandas", 
                        "matplotlib", "seaborn", "Tableau"],
        "Blockchain": ["Solidity", "Rust", "Go", "Web3", "Ethereum", "Smart Contracts"],
        "Game Development": ["C++", "C#", "Unity", "Unreal Engine", "Godot", "Lua"],
        "Cybersecurity": ["Python", "C", "C++", "Assembly", "Bash", "PowerShell", 
                         "Penetration Testing", "Network Security"]
    }
    
    # Company technology preferences
    COMPANY_PREFERENCES = {
        "Microsoft": ["C#", ".NET", "Azure", "TypeScript", "Python", "PowerShell"],
        "Google": ["Go", "Python", "Java", "C++", "Kubernetes", "TensorFlow"],
        "Amazon": ["Java", "Python", "AWS", "Go", "TypeScript"],
        "Meta": ["Python", "React", "PHP", "C++", "PyTorch"],
        "Apple": ["Swift", "Objective-C", "C++", "Metal"],
        "Netflix": ["Java", "Python", "Node.js", "React", "AWS"],
        "Tesla": ["Python", "C++", "ROS", "PyTorch", "CUDA"],
        "OpenAI": ["Python", "PyTorch", "TensorFlow", "Rust", "CUDA"]
    }
    
    def analyze_profile(self, profile_data: Dict, target_domain: str, 
                       target_companies: List[str]) -> Dict:
        """Perform complete profile analysis"""
        
        # Calculate individual rating components
        repo_quality = self._calculate_repository_quality(profile_data)
        tech_alignment = self._calculate_tech_alignment(profile_data, target_domain)
        contribution = self._calculate_contribution_consistency(profile_data)
        documentation = self._calculate_documentation_quality(profile_data)
        domain_relevance = self._calculate_domain_relevance(profile_data, target_domain)
        
        # Weighted overall rating
        overall_rating = (
            repo_quality * 0.25 +
            tech_alignment * 0.25 +
            contribution * 0.15 +
            documentation * 0.15 +
            domain_relevance * 0.20
        )
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(profile_data, {
            "repository_quality": repo_quality,
            "tech_stack_alignment": tech_alignment,
            "contribution_consistency": contribution,
            "documentation_quality": documentation,
            "domain_relevance": domain_relevance
        })
        
        weaknesses = self._identify_weaknesses(profile_data, {
            "repository_quality": repo_quality,
            "tech_stack_alignment": tech_alignment,
            "contribution_consistency": contribution,
            "documentation_quality": documentation,
            "domain_relevance": domain_relevance
        })
        
        # Company alignment analysis
        company_alignment = self._analyze_company_alignment(
            profile_data, target_companies
        )
        
        return {
            "overall_rating": round(overall_rating, 2),
            "rating_breakdown": {
                "repository_quality": round(repo_quality, 2),
                "tech_stack_alignment": round(tech_alignment, 2),
                "contribution_consistency": round(contribution, 2),
                "documentation_quality": round(documentation, 2),
                "domain_relevance": round(domain_relevance, 2)
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "company_alignment": company_alignment
        }
    
    def _calculate_repository_quality(self, profile_data: Dict) -> float:
        """Calculate repository quality score (0-100)"""
        repos = [r for r in profile_data["repositories"] if not r["is_fork"]]
        
        if not repos:
            return 0.0
        
        # Factors: stars, forks, repo count, recent activity
        total_stars = profile_data["total_stars"]
        total_forks = profile_data["total_forks"]
        repo_count = len(repos)
        
        # Log scale for stars/forks to prevent dominance
        star_score = min(math.log10(total_stars + 1) * 15, 35)
        fork_score = min(math.log10(total_forks + 1) * 10, 20)
        repo_count_score = min(repo_count * 2, 25)
        
        # Recent activity bonus (repos updated in last year)
        from datetime import datetime, timedelta
        one_year_ago = datetime.now() - timedelta(days=365)
        recent_repos = sum(1 for r in repos if r["updated_at"].replace(tzinfo=None) > one_year_ago)
        activity_score = min(recent_repos * 3, 20)
        
        return star_score + fork_score + repo_count_score + activity_score
    
    def _calculate_tech_alignment(self, profile_data: Dict, target_domain: str) -> float:
        """Calculate technology stack alignment with target domain (0-100)"""
        if target_domain not in self.DOMAIN_TECHNOLOGIES:
            return 50.0  # Neutral score for unknown domains
        
        required_techs = self.DOMAIN_TECHNOLOGIES[target_domain]
        user_langs = set(profile_data["languages"].keys())
        
        # Check languages in repositories
        repo_techs = set()
        for repo in profile_data["repositories"]:
            if repo["language"]:
                repo_techs.add(repo["language"])
            repo_techs.update(repo["topics"])
        
        all_user_techs = user_langs.union(repo_techs)
        
        # Calculate match percentage
        matches = sum(1 for tech in required_techs if tech in all_user_techs or 
                     any(tech.lower() in t.lower() for t in all_user_techs))
        
        alignment_percentage = (matches / len(required_techs)) * 100
        return min(alignment_percentage, 100)
    
    def _calculate_contribution_consistency(self, profile_data: Dict) -> float:
        """Calculate contribution consistency score (0-100)"""
        repos = profile_data["repositories"]
        
        if not repos:
            return 0.0
        
        # Account age
        from datetime import datetime
        account_age_days = (datetime.now() - profile_data["created_at"].replace(tzinfo=None)).days
        account_years = max(account_age_days / 365, 0.1)
        
        # Repos per year
        repos_per_year = len(repos) / account_years
        consistency_score = min(repos_per_year * 10, 60)
        
        # Follower engagement
        follower_score = min(math.log10(profile_data["followers"] + 1) * 8, 25)
        
        # Public gists bonus
        gist_score = min(profile_data["public_gists"] * 0.5, 15)
        
        return consistency_score + follower_score + gist_score
    
    def _calculate_documentation_quality(self, profile_data: Dict) -> float:
        """Calculate documentation quality score (0-100)"""
        repos = [r for r in profile_data["repositories"] if not r["is_fork"]]
        
        if not repos:
            return 0.0
        
        # README presence
        repos_with_readme = sum(1 for r in repos if r["has_readme"])
        readme_score = (repos_with_readme / len(repos)) * 50
        
        # Description presence
        repos_with_description = sum(1 for r in repos if r["description"])
        description_score = (repos_with_description / len(repos)) * 30
        
        # Topics/tags usage
        repos_with_topics = sum(1 for r in repos if r["topics"])
        topics_score = (repos_with_topics / len(repos)) * 20
        
        return readme_score + description_score + topics_score
    
    def _calculate_domain_relevance(self, profile_data: Dict, target_domain: str) -> float:
        """Calculate how relevant the profile is to the target domain (0-100)"""
        if target_domain not in self.DOMAIN_TECHNOLOGIES:
            return 50.0
        
        domain_keywords = [tech.lower() for tech in self.DOMAIN_TECHNOLOGIES[target_domain]]
        relevance_score = 0
        
        # Check bio
        bio = (profile_data.get("bio") or "").lower()
        if any(keyword in bio for keyword in domain_keywords):
            relevance_score += 20
        
        # Check repository topics and descriptions
        relevant_repos = 0
        for repo in profile_data["repositories"]:
            repo_text = f"{repo.get('description', '')} {' '.join(repo.get('topics', []))}".lower()
            if any(keyword in repo_text for keyword in domain_keywords):
                relevant_repos += 1
        
        if profile_data["repositories"]:
            relevance_score += (relevant_repos / len(profile_data["repositories"])) * 80
        
        return min(relevance_score, 100)
    
    def _identify_strengths(self, profile_data: Dict, scores: Dict) -> List[str]:
        """Identify profile strengths"""
        strengths = []
        
        if scores["repository_quality"] >= 70:
            strengths.append(f"High-quality repository portfolio with {profile_data['total_stars']} total stars")
        
        if scores["tech_stack_alignment"] >= 70:
            strengths.append("Strong alignment with target domain technologies")
        
        if scores["contribution_consistency"] >= 70:
            strengths.append("Consistent contribution pattern and community engagement")
        
        if scores["documentation_quality"] >= 75:
            strengths.append("Excellent documentation practices across repositories")
        
        if profile_data["followers"] > 100:
            strengths.append(f"Strong community presence with {profile_data['followers']} followers")
        
        if profile_data["public_repos"] > 20:
            strengths.append(f"Extensive project portfolio with {profile_data['public_repos']} public repositories")
        
        # Language diversity
        if len(profile_data["languages"]) >= 5:
            strengths.append(f"Diverse technology stack ({len(profile_data['languages'])} languages)")
        
        return strengths if strengths else ["Active GitHub presence"]
    
    def _identify_weaknesses(self, profile_data: Dict, scores: Dict) -> List[str]:
        """Identify profile weaknesses"""
        weaknesses = []
        
        if scores["repository_quality"] < 40:
            weaknesses.append("Limited repository engagement - work on projects that attract stars and forks")
        
        if scores["tech_stack_alignment"] < 40:
            weaknesses.append("Technology stack needs better alignment with target domain - learn relevant technologies")
        
        if scores["documentation_quality"] < 50:
            weaknesses.append("Documentation needs improvement - add READMEs, descriptions, and topics to all repos")
        
        if profile_data["public_repos"] < 5:
            weaknesses.append("Limited portfolio - create more public repositories to showcase your skills")
        
        if not profile_data.get("bio"):
            weaknesses.append("Missing profile bio - add a professional summary highlighting your expertise")
        
        # Check recent activity
        repos = profile_data["repositories"]
        if repos:
            from datetime import datetime, timedelta
            six_months_ago = datetime.now() - timedelta(days=180)
            recent_activity = any(r["updated_at"].replace(tzinfo=None) > six_months_ago for r in repos)
            if not recent_activity:
                weaknesses.append("Low recent activity - update existing projects or start new ones")
        
        # Language diversity
        if len(profile_data["languages"]) < 3:
            weaknesses.append("Limited technology diversity - explore different languages and frameworks")
        
        return weaknesses if weaknesses else ["Continue building and refining your profile"]
    
    def _analyze_company_alignment(self, profile_data: Dict, 
                                   target_companies: List[str]) -> Dict[str, str]:
        """Analyze alignment with target companies"""
        alignment = {}
        user_langs = set(profile_data["languages"].keys())
        
        for company in target_companies:
            if company in self.COMPANY_PREFERENCES:
                preferred_techs = self.COMPANY_PREFERENCES[company]
                matches = sum(1 for tech in preferred_techs if tech in user_langs)
                match_percentage = (matches / len(preferred_techs)) * 100
                
                if match_percentage >= 60:
                    alignment[company] = f"✅ Strong fit ({int(match_percentage)}% tech stack match)"
                elif match_percentage >= 30:
                    alignment[company] = f"⚠️ Moderate fit ({int(match_percentage)}% tech stack match)"
                else:
                    alignment[company] = f"❌ Needs improvement ({int(match_percentage)}% tech stack match)"
            else:
                alignment[company] = "❓ Company tech preferences not in database"
        
        return alignment

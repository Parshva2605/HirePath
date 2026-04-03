"""
Enhanced Repository Analyzer - Per-Repo Analysis with Domain Detection
Provides detailed 5-star quality rating and domain classification for each repository
"""
from typing import Dict, List
import re
from collections import Counter


class RepositoryAnalyzer:
    """Analyze individual repositories for quality and domain"""
    
    # Enhanced domain detection keywords
    DOMAIN_KEYWORDS = {
        "AI/ML": ["machine-learning", "ml", "deep-learning", "neural-network", "tensorflow", 
                  "pytorch", "keras", "scikit-learn", "ai", "artificial-intelligence", 
                  "computer-vision", "nlp", "natural-language", "transformer", "bert", "gpt",
                  "yolo", "cnn", "rnn", "lstm", "gan", "classification", "regression"],
        
        "Data Science": ["data-science", "data-analysis", "pandas", "numpy", "matplotlib",
                        "seaborn", "jupyter", "notebook", "visualization", "analytics",
                        "statistics", "data-mining", "big-data", "tableau"],
        
        "Web Development": ["web", "website", "frontend", "backend", "full-stack", "react",
                           "vue", "angular", "nextjs", "express", "django", "flask", "fastapi",
                           "html", "css", "javascript", "typescript", "node", "web-app"],
        
        "Mobile": ["android", "ios", "mobile", "flutter", "react-native", "swift", "kotlin",
                  "mobile-app", "app-development"],
        
        "DevOps": ["devops", "docker", "kubernetes", "k8s", "ci-cd", "jenkins", "terraform",
                  "ansible", "aws", "azure", "gcp", "cloud", "infrastructure", "deployment",
                  "monitoring", "prometheus", "grafana"],
        
        "Backend": ["api", "rest", "graphql", "microservices", "database", "sql", "nosql",
                   "mongodb", "postgresql", "redis", "server", "backend"],
        
        "Blockchain": ["blockchain", "crypto", "web3", "ethereum", "solidity", "smart-contract",
                      "nft", "defi", "bitcoin"],
        
        "Game Dev": ["game", "unity", "unreal", "godot", "game-development", "gaming"],
        
        "Cybersecurity": ["security", "cybersecurity", "penetration", "vulnerability",
                         "encryption", "hacking", "infosec"],
        
        "Tools/Utilities": ["cli", "tool", "utility", "automation", "script", "helper",
                           "library", "framework", "package"]
    }
    
    def analyze_repository(self, repo: Dict) -> Dict:
        """Analyze a single repository comprehensively"""
        
        # Detect domain
        domain = self._detect_domain(repo)
        
        # Calculate 5-star quality rating
        quality_stars = self._calculate_quality_stars(repo)
        quality_score = self._calculate_detailed_quality(repo)
        
        # Determine impact level
        impact = self._determine_impact(repo)
        
        # Check project maturity
        maturity = self._check_maturity(repo)
        
        return {
            "name": repo["name"],
            "description": repo.get("description", "No description"),
            "language": repo.get("language", "Unknown"),
            "domain": domain,
            "quality_stars": quality_stars,
            "quality_score": quality_score,
            "stars": repo["stars"],
            "forks": repo["forks"],
            "has_readme": repo["has_readme"],
            "topics": repo.get("topics", []),
            "impact": impact,
            "maturity": maturity,
            "is_fork": repo["is_fork"]
        }
    
    def _detect_domain(self, repo: Dict) -> str:
        """Detect repository domain based on topics, description, and language"""
        description = repo.get('description') or ''
        topics = repo.get('topics') or []
        language = repo.get('language') or ''
        
        text = f"{description} {' '.join(topics)} {language}".lower()
        
        domain_scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        
        # Fallback to language-based detection
        language = repo.get("language") or ""
        language = language.lower() if language else ""
        language_domains = {
            "python": "Backend/Scripting",
            "javascript": "Web Development",
            "typescript": "Web Development",
            "java": "Backend",
            "go": "Backend/DevOps",
            "rust": "Systems/Backend",
            "c++": "Systems/Game Dev",
            "c#": "Game Dev/Backend",
            "swift": "Mobile",
            "kotlin": "Mobile",
            "solidity": "Blockchain"
        }
        
        return language_domains.get(language, "General")
    
    def _calculate_quality_stars(self, repo: Dict) -> float:
        """Calculate quality rating (0-5 stars)"""
        score = 0
        
        # Star-based scoring
        stars = repo["stars"]
        if stars >= 1000: score += 2.0
        elif stars >= 100: score += 1.5
        elif stars >= 50: score += 1.0
        elif stars >= 10: score += 0.5
        
        # Fork-based scoring
        forks = repo["forks"]
        if forks >= 200: score += 1.0
        elif forks >= 50: score += 0.75
        elif forks >= 20: score += 0.5
        elif forks >= 5: score += 0.25
        
        # Documentation
        if repo["has_readme"]: score += 0.5
        if repo.get("description"): score += 0.25
        
        # Topics/tags
        if len(repo.get("topics", [])) >= 5: score += 0.5
        elif len(repo.get("topics", [])) >= 3: score += 0.25
        
        # Not a fork bonus
        if not repo["is_fork"]: score += 0.5
        
        return min(score, 5.0)
    
    def _calculate_detailed_quality(self, repo: Dict) -> Dict:
        """Calculate detailed quality metrics"""
        return {
            "popularity": min((repo["stars"] / 10), 100),  # Stars normalized
            "community": min((repo["forks"] / 5), 100),    # Forks normalized
            "documentation": 100 if repo["has_readme"] and repo.get("description") else 50,
            "discoverability": min(len(repo.get("topics", [])) * 20, 100)
        }
    
    def _determine_impact(self, repo: Dict) -> str:
        """Determine project impact level"""
        stars = repo["stars"]
        forks = repo["forks"]
        
        if stars >= 500 or forks >= 100:
            return "🔥 High Impact"
        elif stars >= 100 or forks >= 20:
            return "⭐ Medium Impact"
        elif stars >= 20 or forks >= 5:
            return "📈 Growing"
        else:
            return "🌱 Early Stage"
    
    def _check_maturity(self, repo: Dict) -> str:
        """Check project maturity"""
        has_docs = repo["has_readme"]
        has_description = bool(repo.get("description"))
        has_topics = len(repo.get("topics", [])) > 0
        has_engagement = repo["stars"] > 0 or repo["forks"] > 0
        
        maturity_score = sum([has_docs, has_description, has_topics, has_engagement])
        
        if maturity_score >= 4:
            return "✅ Mature"
        elif maturity_score >= 3:
            return "🔄 Active Development"
        elif maturity_score >= 2:
            return "⚠️ Needs Polish"
        else:
            return "🚧 Work in Progress"
    
    def get_domain_distribution(self, analyzed_repos: List[Dict]) -> Dict:
        """Get distribution of domains across repos"""
        domains = [r["domain"] for r in analyzed_repos if not r["is_fork"]]
        return dict(Counter(domains))
    
    def get_quality_summary(self, analyzed_repos: List[Dict]) -> Dict:
        """Get overall quality summary"""
        non_fork_repos = [r for r in analyzed_repos if not r["is_fork"]]
        
        if not non_fork_repos:
            return {"average_stars": 0, "average_quality": 0, "high_quality_count": 0}
        
        avg_stars = sum(r["quality_stars"] for r in non_fork_repos) / len(non_fork_repos)
        high_quality = sum(1 for r in non_fork_repos if r["quality_stars"] >= 4.0)
        
        return {
            "average_quality_stars": round(avg_stars, 2),
            "high_quality_repos": high_quality,
            "total_original_repos": len(non_fork_repos),
            "quality_percentage": round((high_quality / len(non_fork_repos)) * 100, 1)
        }

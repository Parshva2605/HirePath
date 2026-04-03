"""
GitHub Profile Analyzer - GitHub API Integration
File: app/github_fetcher.py
"""
from github import Github, GithubException
from typing import Dict, List, Optional
import os
from datetime import datetime
from collections import Counter
import re


class GitHubFetcher:
    """Fetch and process GitHub profile data"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with optional token"""
        self.token = token or os.getenv("GITHUB_TOKEN")
        if self.token:
            self.client = Github(self.token)
        else:
            self.client = Github()  # Unauthenticated (60 requests/hour)
        
        # Track API usage
        self.api_calls_start = None
        self.api_calls_end = None
    
    def extract_username(self, github_url: str) -> str:
        """Extract username from GitHub URL or return as-is if already username"""
        # Handle various GitHub URL formats
        patterns = [
            r'github\.com/([^/]+)',
            r'^@?(.+)$'  # Plain username with or without @
        ]
        
        for pattern in patterns:
            match = re.search(pattern, github_url.strip())
            if match:
                return match.group(1)
        
        return github_url.strip()
    
    def fetch_profile_data(self, github_url: str) -> Dict:
        """Fetch comprehensive GitHub profile data"""
        try:
            # Track API usage at start
            rate_limit = self.client.get_rate_limit()
            self.api_calls_start = rate_limit.core.remaining
            
            username = self.extract_username(github_url)
            user = self.client.get_user(username)
            
            # Fetch basic profile info
            profile_info = {
                "username": user.login,
                "name": user.name,
                "bio": user.bio,
                "location": user.location,
                "email": user.email,
                "followers": user.followers,
                "following": user.following,
                "public_repos": user.public_repos,
                "public_gists": user.public_gists,
                "created_at": user.created_at,
            }
            
            # Fetch repositories
            repositories = []
            languages = Counter()
            total_stars = 0
            total_forks = 0
            
            repos = user.get_repos(type="owner", sort="updated")
            
            for repo in repos:
                # Get topics safely (handle API errors)
                try:
                    topics = repo.get_topics()
                except Exception:
                    topics = []  # Fallback to empty list if topics fail
                
                # Skip forked repos for main analysis
                repo_data = {
                    "name": repo.name,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "topics": topics,
                    "is_fork": repo.fork,
                    "created_at": repo.created_at,
                    "updated_at": repo.updated_at,
                    "has_readme": self._check_readme(repo),
                }
                repositories.append(repo_data)
                
                # Accumulate stats (only for non-fork repos)
                if not repo.fork:
                    total_stars += repo.stargazers_count
                    total_forks += repo.forks_count
                    if repo.language:
                        languages[repo.language] += 1
            
            profile_info["repositories"] = repositories
            profile_info["languages"] = dict(languages)
            profile_info["total_stars"] = total_stars
            profile_info["total_forks"] = total_forks
            
            # Track API usage at end
            rate_limit = self.client.get_rate_limit()
            self.api_calls_end = rate_limit.core.remaining
            profile_info["api_calls_used"] = self.api_calls_start - self.api_calls_end if self.api_calls_start else 0
            profile_info["api_calls_remaining"] = self.api_calls_end
            
            return profile_info
            
        except GithubException as e:
            raise ValueError(f"Error fetching GitHub data: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")
    
    def _check_readme(self, repo) -> bool:
        """Check if repository has a README file"""
        try:
            readme_files = ["README.md", "README", "readme.md", "Readme.md"]
            contents = repo.get_contents("")
            
            for content in contents:
                if content.name in readme_files:
                    return True
            return False
        except:
            return False
    
    def get_rate_limit(self) -> Dict:
        """Get current API rate limit status"""
        rate_limit = self.client.get_rate_limit()
        return {
            "core": {
                "remaining": rate_limit.core.remaining,
                "limit": rate_limit.core.limit,
                "reset": rate_limit.core.reset.isoformat() if rate_limit.core.reset else None
            }
        }

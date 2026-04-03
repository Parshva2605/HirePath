"""
GitHub profile fetcher - Fetch public GitHub data via REST API (no auth needed).
"""

import base64
from typing import Dict, Any, List
from urllib.parse import urlparse

import requests


GITHUB_BASE_URL = "https://api.github.com"
TIMEOUT = 10


def extract_github_username(github_url: str) -> str:
    """Extract a GitHub username from a URL or raw username string."""
    candidate = (github_url or "").strip()
    if not candidate:
        return ""

    if "://" not in candidate and "/" not in candidate:
        return candidate

    parsed = urlparse(candidate if candidate.startswith("http") else f"https://{candidate}")
    path_parts = [part for part in parsed.path.split("/") if part]
    if not path_parts:
        return ""

    username = path_parts[0]
    username = username.split("?")[0].split("#")[0].strip()
    return username


def fetch_github_profile(username: str) -> Dict[str, Any]:
    """
    Fetch GitHub user profile information.
    
    Args:
        username: GitHub username
    
    Returns:
        Dictionary with user profile data
    """
    try:
        response = requests.get(f"{GITHUB_BASE_URL}/users/{username}", timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        return {
            "username": data.get("login", username),
            "name": data.get("name", ""),
            "bio": data.get("bio", ""),
            "location": data.get("location", ""),
            "blog": data.get("blog", ""),
            "company": data.get("company", ""),
            "public_repos": data.get("public_repos", 0),
            "followers": data.get("followers", 0),
            "following": data.get("following", 0),
            "created_at": data.get("created_at", ""),
            "updated_at": data.get("updated_at", ""),
            "profile_url": data.get("html_url", "")
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch GitHub profile for {username}: {str(e)}")


def fetch_github_repos(username: str, max_repos: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch all public repositories for a GitHub user.
    
    Args:
        username: GitHub username
        max_repos: Maximum number of repos to fetch (API limit: 100 per page)
    
    Returns:
        List of repository data
    """
    repos = []
    page = 1
    
    while len(repos) < max_repos:
        try:
            response = requests.get(
                f"{GITHUB_BASE_URL}/users/{username}/repos",
                params={
                    "per_page": 100,
                    "sort": "updated",
                    "page": page
                },
                timeout=TIMEOUT
            )
            response.raise_for_status()
            page_data = response.json()
            
            if not page_data:
                break
            
            repos.extend(page_data)
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Warning: Error fetching repos page {page}: {str(e)}")
            break
    
    return repos[:max_repos]


def fetch_readme_content(username: str, repo_name: str, max_chars: int = 2000) -> str:
    """
    Fetch README content for a repository.
    
    Args:
        username: GitHub username
        repo_name: Repository name
        max_chars: Maximum characters to return
    
    Returns:
        README content (first max_chars characters)
    """
    try:
        response = requests.get(
            f"{GITHUB_BASE_URL}/repos/{username}/{repo_name}/readme",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            content_b64 = response.json().get("content", "")
            content = base64.b64decode(content_b64).decode("utf-8")
            return content[:max_chars]
        
    except Exception as e:
        pass  # README not found or error fetching
    
    return ""


def fetch_repo_languages(username: str, repo_name: str) -> Dict[str, int]:
    """
    Fetch programming languages used in a repository.
    
    Args:
        username: GitHub username
        repo_name: Repository name
    
    Returns:
        Dictionary mapping language to byte count
    """
    try:
        response = requests.get(
            f"{GITHUB_BASE_URL}/repos/{username}/{repo_name}/languages",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json() or {}
    except Exception:
        return {}


def process_repository(username: str, repo: Dict, fetch_details: bool = True) -> Dict[str, Any]:
    """
    Process a single repository record into structured format.
    
    Args:
        username: GitHub username (owner)
        repo: Raw repo data from GitHub API
        fetch_details: Whether to fetch README and language details
    
    Returns:
        Processed repository data
    """
    repo_info = {
        "name": repo.get("name", ""),
        "description": repo.get("description", ""),
        "url": repo.get("html_url", ""),
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "language": repo.get("language", ""),
        "topics": repo.get("topics", []),
        "updated_at": repo.get("updated_at", ""),
        "created_at": repo.get("created_at", ""),
        "has_readme": False,
        "readme_content": "",
        "languages": {}
    }
    
    if fetch_details:
        # Fetch README
        readme = fetch_readme_content(username, repo_info["name"])
        if readme:
            repo_info["has_readme"] = True
            repo_info["readme_content"] = readme
        
        # Fetch language breakdown
        repo_info["languages"] = fetch_repo_languages(username, repo_info["name"])
    
    return repo_info


def analyze_language_frequencies(repos: List[Dict]) -> Dict[str, int]:
    """
    Calculate frequency of programming languages across all repos.
    
    Args:
        repos: List of processed repository data
    
    Returns:
        Dictionary mapping language to count
    """
    lang_count = {}
    
    for repo in repos:
        lang = repo.get("language")
        if lang and lang.strip():
            lang_count[lang] = lang_count.get(lang, 0) + 1
    
    return lang_count


def get_top_languages(lang_count: Dict[str, int], top_n: int = 10) -> List[tuple]:
    """
    Get top N languages sorted by frequency.
    
    Args:
        lang_count: Language frequency dictionary
        top_n: Number of top languages to return
    
    Returns:
        List of (language, count) tuples sorted by count
    """
    return sorted(lang_count.items(), key=lambda x: -x[1])[:top_n]


def fetch_github_data(github_url: str, fetch_details: bool = False) -> Dict[str, Any]:
    """
    Main function - fetch complete GitHub profile and repository data.
    
    Args:
        github_url: Full GitHub profile URL or username
        fetch_details: Whether to fetch README and language details for each repo
    
    Returns:
        Complete GitHub profile and repository data
    """
    # Extract username from URL or use directly
    username = extract_github_username(github_url)
    
    if not username:
        raise ValueError("Invalid GitHub URL or username")
    
    # Fetch profile
    profile = fetch_github_profile(username)
    
    # Fetch repositories
    repos_raw = fetch_github_repos(username)
    repos_processed = [process_repository(username, repo, fetch_details) for repo in repos_raw]
    
    # Calculate language frequencies
    lang_count = analyze_language_frequencies(repos_processed)
    top_languages = get_top_languages(lang_count)
    
    # Identify top repos by stars
    top_repos_by_stars = sorted(repos_processed, key=lambda x: -x["stars"])[:5]
    
    return {
        "username": profile["username"],
        "bio": profile.get("bio", ""),
        "location": profile.get("location", ""),
        "company": profile.get("company", ""),
        "profile_url": profile.get("profile_url", ""),
        "public_repos": profile.get("public_repos", 0),
        "followers": profile.get("followers", 0),
        "following": profile.get("following", 0),
        "created_at": profile.get("created_at", ""),
        "repos": repos_processed,
        "top_languages": top_languages,
        "top_repos_by_stars": top_repos_by_stars,
        "total_repos_fetched": len(repos_processed),
        "unique_languages": len(lang_count),
        "total_stars": sum(repo["stars"] for repo in repos_processed)
    }


def validate_github_profile(github_url: str) -> bool:
    """Check if GitHub profile is accessible."""
    try:
        username = extract_github_username(github_url)
        if not username:
            return False
        response = requests.get(f"{GITHUB_BASE_URL}/users/{username}", timeout=TIMEOUT)
        return response.status_code == 200
    except Exception:
        return False


if __name__ == "__main__":
    # Test example
    print("GitHub fetcher module loaded successfully")
    print(f"GitHub API base URL: {GITHUB_BASE_URL}")

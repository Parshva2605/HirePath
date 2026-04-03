"""
Enhanced Profile Analyzer - Improved Rating Algorithm
Properly scores quality profiles (3000+ stars should score 80+)
"""
from typing import Dict, List
import math
from datetime import datetime, timedelta


class EnhancedProfileAnalyzer:
    """Enhanced analyzer with better scoring for quality profiles"""
    
    def calculate_enhanced_rating(self, profile_data: Dict, analyzed_repos: List[Dict], 
                                  target_domain: str) -> Dict:
        """
        Enhanced rating that properly values quality metrics
        A profile with 3165 stars should score 75-85+
        """
        
        # 1. Repository Quality & Impact (35 points)
        repo_score = self._calculate_repository_score_v2(profile_data, analyzed_repos)
        
        # 2. Community Engagement (25 points)
        community_score = self._calculate_community_score(profile_data)
        
        # 3. Tech Stack & Domain Alignment (20 points)
        tech_score = self._calculate_tech_alignment_v2(analyzed_repos, target_domain)
        
        # 4. Project Quality & Maturity (15 points)
        quality_score = self._calculate_quality_score(analyzed_repos)
        
        # 5. Consistency & Activity (5 points)
        activity_score = self._calculate_activity_score(profile_data, analyzed_repos)
        
        overall = repo_score + community_score + tech_score + quality_score + activity_score
        
        return {
            "overall_rating": min(round(overall, 1), 100),
            "breakdown": {
                "repository_impact": round(repo_score, 1),
                "community_engagement": round(community_score, 1),
                "tech_stack_alignment": round(tech_score, 1),
                "project_quality": round(quality_score, 1),
                "activity_consistency": round(activity_score, 1)
            }
        }
    
    def _calculate_repository_score_v2(self, profile_data: Dict, analyzed_repos: List[Dict]) -> float:
        """
        Enhanced repository scoring (0-35 points)
        Better rewards for high star counts
        """
        total_stars = profile_data["total_stars"]
        total_forks = profile_data["total_forks"]
        non_fork_repos = [r for r in analyzed_repos if not r["is_fork"]]
        
        # Star score (0-20 points) - logarithmic scale with better rewards
        if total_stars >= 5000:
            star_score = 20
        elif total_stars >= 2000:
            star_score = 15 + ((total_stars - 2000) / 3000) * 5
        elif total_stars >= 500:
            star_score = 10 + ((total_stars - 500) / 1500) * 5
        elif total_stars >= 100:
            star_score = 5 + ((total_stars - 100) / 400) * 5
        else:
            star_score = min(total_stars / 20, 5)
        
        # Fork score (0-8 points)
        if total_forks >= 1000:
            fork_score = 8
        elif total_forks >= 300:
            fork_score = 5 + ((total_forks - 300) / 700) * 3
        elif total_forks >= 50:
            fork_score = 3 + ((total_forks - 50) / 250) * 2
        else:
            fork_score = min(total_forks / 10, 3)
        
        # Repository count (0-7 points)
        repo_count = len(non_fork_repos)
        if repo_count >= 50:
            count_score = 7
        elif repo_count >= 20:
            count_score = 5 + ((repo_count - 20) / 30) * 2
        elif repo_count >= 10:
            count_score = 3 + ((repo_count - 10) / 10) * 2
        else:
            count_score = min(repo_count * 0.3, 3)
        
        return star_score + fork_score + count_score
    
    def _calculate_community_score(self, profile_data: Dict) -> float:
        """
        Community engagement score (0-25 points)
        Followers, following ratio, overall presence
        """
        followers = profile_data["followers"]
        following = profile_data["following"]
        
        # Follower score (0-15 points)
        if followers >= 500:
            follower_score = 15
        elif followers >= 200:
            follower_score = 12 + ((followers - 200) / 300) * 3
        elif followers >= 50:
            follower_score = 8 + ((followers - 50) / 150) * 4
        elif followers >= 10:
            follower_score = 4 + ((followers - 10) / 40) * 4
        else:
            follower_score = min(followers * 0.4, 4)
        
        # Following/Follower ratio (0-5 points)
        if followers > 0:
            ratio = following / max(followers, 1)
            if ratio <= 0.5:  # More followers than following (influence)
                ratio_score = 5
            elif ratio <= 1.0:
                ratio_score = 4
            elif ratio <= 2.0:
                ratio_score = 3
            else:
                ratio_score = 2
        else:
            ratio_score = 0
        
        # Public gists (0-3 points)
        gist_score = min(profile_data["public_gists"] * 0.3, 3)
        
        # Profile completeness (0-2 points)
        completeness = 0
        if profile_data.get("bio"): completeness += 1
        if profile_data.get("location"): completeness += 0.5
        if profile_data.get("email"): completeness += 0.5
        
        return follower_score + ratio_score + gist_score + completeness
    
    def _calculate_tech_alignment_v2(self, analyzed_repos: List[Dict], target_domain: str) -> float:
        """
        Tech stack alignment score (0-20 points)
        Based on domain distribution and variety
        """
        non_fork_repos = [r for r in analyzed_repos if not r["is_fork"]]
        
        if not non_fork_repos:
            return 0
        
        # Domain relevance (0-12 points)
        target_repos = [r for r in non_fork_repos if r["domain"] == target_domain]
        relevance_ratio = len(target_repos) / len(non_fork_repos)
        
        if relevance_ratio >= 0.5:
            domain_score = 12
        elif relevance_ratio >= 0.3:
            domain_score = 8 + (relevance_ratio - 0.3) * 20
        elif relevance_ratio >= 0.1:
            domain_score = 4 + (relevance_ratio - 0.1) * 20
        else:
            domain_score = relevance_ratio * 40
        
        # Language diversity (0-5 points)
        languages = set(r["language"] for r in non_fork_repos if r["language"] != "Unknown")
        diversity_score = min(len(languages) * 0.7, 5)
        
        # Domain diversity (0-3 points)
        domains = set(r["domain"] for r in non_fork_repos)
        domain_diversity = min(len(domains) * 0.5, 3)
        
        return domain_score + diversity_score + domain_diversity
    
    def _calculate_quality_score(self, analyzed_repos: List[Dict]) -> float:
        """
        Project quality score (0-15 points)
        Based on documentation, topics, and overall polish
        """
        non_fork_repos = [r for r in analyzed_repos if not r["is_fork"]]
        
        if not non_fork_repos:
            return 0
        
        # Documentation score (0-7 points)
        repos_with_readme = sum(1 for r in non_fork_repos if r["has_readme"])
        repos_with_description = sum(1 for r in non_fork_repos if r["description"] != "No description")
        
        doc_ratio = (repos_with_readme + repos_with_description) / (2 * len(non_fork_repos))
        doc_score = doc_ratio * 7
        
        # Topics/discoverability score (0-5 points)
        repos_with_topics = sum(1 for r in non_fork_repos if len(r.get("topics", [])) >= 3)
        topics_ratio = repos_with_topics / len(non_fork_repos)
        topics_score = topics_ratio * 5
        
        # High-quality project count (0-3 points)
        high_quality = sum(1 for r in non_fork_repos if r["quality_stars"] >= 4.0)
        quality_ratio = high_quality / len(non_fork_repos)
        quality_bonus = quality_ratio * 3
        
        return doc_score + topics_score + quality_bonus
    
    def _calculate_activity_score(self, profile_data: Dict, analyzed_repos: List[Dict]) -> float:
        """
        Activity and consistency score (0-5 points)
        """
        # Account age factor
        account_age_days = (datetime.now() - profile_data["created_at"].replace(tzinfo=None)).days
        account_years = max(account_age_days / 365, 0.5)
        
        # Repos per year (0-3 points)
        repos_per_year = len(analyzed_repos) / account_years
        if repos_per_year >= 15:
            activity_score = 3
        elif repos_per_year >= 8:
            activity_score = 2 + ((repos_per_year - 8) / 7)
        elif repos_per_year >= 3:
            activity_score = 1 + ((repos_per_year - 3) / 5)
        else:
            activity_score = repos_per_year / 3
        
        # Recent activity (0-2 points)
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_repos = sum(1 for r in analyzed_repos 
                          if r.get("updated_at") and 
                          r["updated_at"].replace(tzinfo=None) > six_months_ago)
        
        if recent_repos >= 5:
            recent_score = 2
        elif recent_repos >= 2:
            recent_score = 1 + ((recent_repos - 2) / 3)
        else:
            recent_score = recent_repos * 0.5
        
        return activity_score + recent_score

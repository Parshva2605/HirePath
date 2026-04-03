"""
Configuration for Job Matcher Module

All API keys and settings are defined here.
Copy this file and update with your actual values.
"""

# =============================================================================
# API KEYS (Optional - module works without these using free sources)
# =============================================================================

# Adzuna API (Optional - for more job sources)
# Get free API key at: https://developer.adzuna.com/signup
# Free tier: 250 calls/month
ADZUNA_APP_ID = "your_adzuna_app_id_here"
ADZUNA_APP_KEY = "your_adzuna_app_key_here"

# LinkedIn API (Optional - requires LinkedIn Developer account)
# Get API key at: https://www.linkedin.com/developers/
# Note: LinkedIn API has strict rate limits and approval process
LINKEDIN_API_KEY = "your_linkedin_api_key_here"

# Indeed API (Optional - requires Indeed Publisher account)
# Get API key at: https://www.indeed.com/publisher
# Note: Indeed API is being phased out for new users
INDEED_PUBLISHER_ID = "your_indeed_publisher_id_here"


# =============================================================================
# DEFAULT SETTINGS
# =============================================================================

# Default location for job search
DEFAULT_LOCATION = "India"

# Maximum number of jobs to return
MAX_JOBS_RETURNED = 10

# Timeout for API requests (seconds)
REQUEST_TIMEOUT = 10

# Number of jobs to fetch from each source
JOBS_PER_SOURCE = 10

# Minimum match score to include in results (0-99)
MIN_MATCH_SCORE = 0  # Set to 30 to filter out very weak matches


# =============================================================================
# MATCH SCORE THRESHOLDS
# =============================================================================

# These thresholds determine the match labels
STRONG_MATCH_THRESHOLD = 80  # >= 80 = "Strong Match 🟢"
GOOD_MATCH_THRESHOLD = 60    # >= 60 = "Good Match 🟡"
PARTIAL_MATCH_THRESHOLD = 40 # >= 40 = "Partial Match 🟠"
# < 40 = "Weak Match 🔴"


# =============================================================================
# JOB SOURCES
# =============================================================================

# Enable/disable specific job sources
ENABLE_REMOTIVE = True   # Free API, no key required
ENABLE_ADZUNA = False    # Requires API key
ENABLE_LINKEDIN = False  # Requires API key
ENABLE_INDEED = False    # Requires API key
ENABLE_DEMO_JOBS = True  # Always show demo jobs as fallback


# =============================================================================
# INSTRUCTIONS FOR GETTING API KEYS
# =============================================================================

"""
1. ADZUNA (Recommended - Free)
   - Visit: https://developer.adzuna.com/signup
   - Sign up for free account
   - Get app_id and app_key
   - Free tier: 250 API calls per month
   - Covers: India, US, UK, and 15+ other countries

2. REMOTIVE (Already Enabled - No Key Required)
   - Free public API for remote jobs
   - No registration needed
   - Covers: Remote jobs worldwide
   - Already integrated and working

3. LINKEDIN (Advanced - Requires Approval)
   - Visit: https://www.linkedin.com/developers/
   - Apply for API access (approval required)
   - Strict rate limits
   - Best for: Large-scale applications

4. INDEED (Legacy - Not Recommended)
   - Visit: https://www.indeed.com/publisher
   - Note: API being phased out for new users
   - Existing users can still use it
   - Alternative: Use web scraping (not included)

RECOMMENDATION:
- Start with Remotive (already working, no setup needed)
- Add Adzuna if you need more job sources (free tier is generous)
- Demo jobs provide realistic fallback data for testing
"""

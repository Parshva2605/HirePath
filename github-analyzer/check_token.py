"""
GitHub Token Validator and Helper
Checks if your GitHub token is working and helps you get a new one if needed
"""
from github import Github, GithubException
import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("  GITHUB TOKEN VALIDATOR")
print("="*70)
print()

token = os.getenv("GITHUB_TOKEN")

if not token or token == "your_github_token_here":
    print("[ERROR] No GitHub token found in .env file!")
    print()
    print("To fix this:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Give it a name: 'GitHub Profile Analyzer'")
    print("4. Select scopes:")
    print("   ✓ public_repo (or full 'repo' if you want private too)")
    print("   ✓ read:user")
    print("5. Click 'Generate token'")
    print("6. Copy the token (starts with 'ghp_')")
    print("7. Edit .env file and paste it:")
    print("   GITHUB_TOKEN=ghp_your_token_here")
    print()
    exit(1)

print(f"Token found: {token[:10]}...{token[-4:]}")
print()

# Test the token
print("Testing token...")
try:
    g = Github(token)
    user = g.get_user()
    
    print(f"[SUCCESS] Token is valid!")
    print(f"Authenticated as: {user.login}")
    print(f"Name: {user.name}")
    print()
    
    # Check rate limit
    rate_limit = g.get_rate_limit()
    core = rate_limit.core
    
    print("Rate Limit Status:")
    print(f"  Remaining: {core.remaining}/{core.limit}")
    print(f"  Resets at: {core.reset}")
    print()
    
    if core.remaining < 10:
        print("[WARNING] Rate limit is very low!")
        print(f"Only {core.remaining} requests remaining.")
        print(f"Wait until {core.reset} for reset.")
    elif core.remaining < 100:
        print("[INFO] Rate limit is getting low.")
        print(f"{core.remaining} requests remaining.")
    else:
        print("[OK] Plenty of API calls remaining!")
    
    print()
    print("Testing repository access...")
    
    # Try to fetch a public repo
    try:
        repo = g.get_repo("torvalds/linux")
        topics = repo.get_topics()
        print(f"[OK] Can access repository topics: {len(topics)} topics found")
    except GithubException as e:
        print(f"[WARNING] Cannot access topics: {e.status} - {e.data.get('message', 'Unknown error')}")
        print("This might affect some features but the analyzer will still work.")
    
    print()
    print("="*70)
    print("[SUCCESS] Your GitHub token is working!")
    print("="*70)
    print()
    print("You can now use the GitHub Profile Analyzer!")
    print("Run: python run.py")
    
except GithubException as e:
    print(f"[ERROR] GitHub API Error!")
    print(f"Status: {e.status}")
    print(f"Message: {e.data.get('message', 'Unknown error')}")
    print()
    
    if e.status == 401:
        print("Your token is INVALID or EXPIRED!")
        print()
        print("To fix:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Generate a new token")
        print("3. Update .env file with new token")
    elif e.status == 403:
        print("Rate limit exceeded or insufficient permissions!")
        print()
        if "rate limit" in str(e.data.get('message', '')).lower():
            print("You've hit the API rate limit.")
            print("Wait an hour or use a different token.")
        else:
            print("Your token might not have the right scopes.")
            print("Required scopes: public_repo, read:user")
    else:
        print("Unexpected error. Check your internet connection.")
    
    print()
    
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    print()
    print("Make sure:")
    print("1. You have internet connection")
    print("2. Your .env file has GITHUB_TOKEN set")
    print("3. The token is valid")

print()

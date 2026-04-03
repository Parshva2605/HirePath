# 🚀 Quick Setup Guide

This guide will help you set up the GitHub Profile Analyzer on any machine without errors.

## ⚡ Quick Start (3 Steps)

### 1. Install Prerequisites

**Python 3.10+**
- Windows: Download from [python.org](https://www.python.org/downloads/)
- macOS: `brew install python@3.10`
- Linux: `sudo apt install python3.10 python3.10-venv`

**Ollama (Local LLM)**
- Download from [ollama.ai](https://ollama.ai)
- Install and it will auto-start

### 2. Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd github-analyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure & Run

```bash
# Copy environment template
cp .env.example .env  # macOS/Linux
copy .env.example .env  # Windows

# Edit .env and add your GitHub token
# Get token from: https://github.com/settings/tokens

# Pull Ollama model
ollama pull qwen2.5:3b

# Start the server
python run.py
```

Open browser: http://localhost:8000

## 📝 Detailed Setup Instructions

### Step 1: Get GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a name (e.g., "GitHub Analyzer")
4. Select scopes:
   - ✅ `repo` (all repository permissions)
   - ✅ `read:user` (read user profile data)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)

### Step 2: Configure .env File

Edit the `.env` file:

```env
GITHUB_TOKEN=ghp_your_actual_token_here
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_HOST=http://localhost:11434
APP_PORT=8000
```

### Step 3: Install Ollama Model

```bash
# Check Ollama is running
ollama list

# Pull recommended model (fast & accurate)
ollama pull qwen2.5:3b

# OR pull higher quality model (slower)
ollama pull llama3.1:8b
```

### Step 4: Verify Setup

```bash
# Test GitHub token
python check_token.py

# Expected output:
# [SUCCESS] Token is valid!
# Authenticated as: YourUsername
# Remaining: 4999/5000
```

### Step 5: Start Application

```bash
# Make sure venv is activated (you should see (venv) in prompt)
python run.py

# Expected output:
# ======================================================================
#   GITHUB PROFILE ANALYZER
# ======================================================================
# Starting server on http://localhost:8000
# Press CTRL+C to stop
# ======================================================================
# INFO:     Started server process [XXXXX]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 🐛 Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'github'`

**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
# Activate venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: `GitHub API 403 Forbidden`

**Cause:** Invalid or missing GitHub token

**Solution:**
```bash
# Verify token
python check_token.py

# If invalid, generate new token at:
# https://github.com/settings/tokens
# Then update .env file
```

### Issue: `Ollama connection failed`

**Cause:** Ollama not running

**Solution:**
```bash
# Check if Ollama is running
ollama list

# If not running, start it
ollama serve

# Pull a model if needed
ollama pull qwen2.5:3b
```

### Issue: `Port 8000 already in use`

**Cause:** Another process using port 8000

**Solution:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux: Kill process
lsof -ti:8000 | xargs kill -9

# OR change port in .env:
APP_PORT=8001
```

### Issue: `NaN in rating breakdown`

**Cause:** Old code still in memory

**Solution:**
```bash
# Stop server (CTRL+C)
# Start again
python run.py
```

## 🎯 Post-Setup Testing

### Test 1: Homepage Loads
- Open http://localhost:8000
- Should see the analyzer form

### Test 2: Analyze a Profile
- Enter: https://github.com/torvalds
- Domain: Systems/Backend
- Companies: Microsoft, Google
- Click "Analyze Profile"
- Should see results with ratings

### Test 3: Verify Features
- ✅ Overall rating displays (0-100)
- ✅ Rating breakdown shows 5 values
- ✅ API usage section appears
- ✅ Domain distribution displays
- ✅ Top repositories render as cards
- ✅ Each repo has 5-star rating
- ✅ Recommendations are personalized

## 📊 Expected Results

### For a Quality Profile (e.g., 2000+ stars, 500+ followers):
- **Overall Rating:** 75-85/100
- **Repository Impact:** 24-30/35
- **Community Engagement:** 18-23/25
- **Tech Stack Alignment:** 12-18/20 (depends on domain match)
- **Project Quality:** 10-14/15
- **Activity Consistency:** 3-5/5

### API Usage (per analysis):
- ~100-150 API calls for 100 repositories
- ~50-100 API calls for 50 repositories
- ~20-50 API calls for 20 repositories

## 🔄 Updating the Project

```bash
# Pull latest changes
git pull origin main

# Activate venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart server
python run.py
```

## 🌍 Deploying to Another Machine

### Method 1: Git Clone (Recommended)

```bash
# On new machine
git clone <your-repo-url>
cd github-analyzer
python -m venv venv
.\venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
ollama pull qwen2.5:3b
python run.py
```

### Method 2: ZIP Transfer

1. **On source machine:**
   ```bash
   # Remove venv and .env before zipping
   rm -rf venv  # or rmdir /s venv on Windows
   rm .env
   # Zip the project folder
   ```

2. **On target machine:**
   ```bash
   # Unzip and setup
   cd github-analyzer
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env
   ollama pull qwen2.5:3b
   python run.py
   ```

## 📚 Additional Resources

- **GitHub Token Scopes:** https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
- **Ollama Models:** https://ollama.ai/library
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **PyGithub Docs:** https://pygithub.readthedocs.io

## ✅ Setup Checklist

- [ ] Python 3.10+ installed
- [ ] Ollama installed and running
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from `.env.example`
- [ ] GitHub token added to `.env`
- [ ] Ollama model pulled (`ollama pull qwen2.5:3b`)
- [ ] Token validated (`python check_token.py`)
- [ ] Server starts without errors (`python run.py`)
- [ ] Homepage loads at http://localhost:8000
- [ ] Profile analysis works end-to-end

## 🎉 You're Ready!

Once all checklist items are complete, you can analyze any GitHub profile and get personalized recommendations!

**Need help?** Check the main README.md for detailed documentation.

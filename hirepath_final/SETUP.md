# HirePath Setup Guide

Complete, step-by-step setup instructions for HirePath career acceleration system.

## 📋 Prerequisites

- **Windows 10/11** or **Linux/Mac** with Bash
- **Python 3.9+** installed
- **Node.js 16+** (optional, for frontend)
- **Ollama** locally installed
- **4GB+ RAM** (8GB+ recommended)
- **Disk space**: ~2GB for Ollama models

---

## 🔧 Step 1: Install Ollama

### Windows
1. Download from: https://ollama.ai
2. Install using the installer
3. Ollama will start automatically after installation
4. Verify: Open [http://localhost:11434](http://localhost:11434) in browser

### macOS
```bash
# Using Homebrew
brew install ollama

# Or download from https://ollama.ai

# Start Ollama
ollama serve
```

### Linux
```bash
# Download and install
curl https://ollama.ai/install.sh | sh

# Start
ollama serve
```

## 🐍 Step 2: Set Up Python Backend

### 2.1 Prepare Directory
```bash
cd D:\HirePath\hirepath_final

# Verify structure
dir
# Should show: agent, skill_gap_db, job_folder, etc.
```

### 2.2 Create Python Virtual Environment
```bash
cd agent

# Create venv
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2.3 Install Dependencies
```bash
# Make sure venv is activated
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2.4 Verify Installation
```bash
python -c "import fastapi; import pdfplumber; print('✓ Dependencies installed')"
```

## 🤖 Step 3: Configure Ollama Models

### 3.1 Pull Models
In a **new terminal** (keep the original one running):

```bash
# Pull llama3 (recommended for general tasks)
ollama pull llama3

# Pull mistral (faster, lighter)
ollama pull mistral

# Pull deepseek-coder (better for code analysis, optional)
ollama pull deepseek-coder
```

### 3.2 Verify Models
```bash
# List installed models
curl http://localhost:11434/api/tags

# Or via command line
ollama list
```

### 3.3 Test Model
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Say hi in one word"
}'
```

## 🚀 Step 4: Start FastAPI Backend

### 4.1 Run Server
```bash
# From hirepath_final/agent directory
# Make sure Python venv is activated

uvicorn main:app --reload --port 8000
```

### 4.2 Verify Server
Wait for message:
```
Uvicorn running on http://127.0.0.1:8000
```

Then visit: http://localhost:8000/docs

You should see the interactive API documentation.

### 4.3 Check Health Status
```bash
curl http://localhost:8000/api/status
```

Expected response:
```json
{
  "backend": "running",
  "ollama_backend": {"connected": true},
  "dependencies": {"skill_gap_db": true, "job_folder": true}
}
```

---

## 🌐 Step 5: Optional - Setup Frontend (Resume Optimizer)

If you want to use the UI for resume optimization:

### 5.1 Clone resume-lm
```bash
cd D:\HirePath

git clone https://github.com/olyaiy/resume-lm.git

cd resume-lm
```

### 5.2 Install Node Dependencies
```bash
npm install
```

### 5.3 Configure Ollama
Create `.env.local`:
```bash
echo OLLAMA_BASE_URL=http://localhost:11434 > .env.local
```

### 5.4 Start Next.js Server
```bash
npm run dev
```

Visit: http://localhost:3000

---

## 📋 Step 6: Test Full Pipeline

### 6.1 Prepare Test Files
1. Find a sample resume (PDF or DOCX)
2. Get a GitHub profile URL or username
3. Choose a domain (aiml, devops, frontend, backend)

### 6.2 Run Full Analysis
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "resume=@path/to/your/resume.pdf" \
  -F "domain=backend" \
  -F "company=Google" \
  -F "github_url=https://github.com/torvalds"
```

### 6.3 Check Response
You should get:
- ✅ ATS score (0-100)
- ✅ Skill gap analysis
- ✅ GitHub analysis (if Ollama is running)
- ✅ Career roadmap (if Ollama is running)
- ✅ Job matches
- ✅ Interview prep

---

## 🔌 Step 7: Configure Skill Databases

### 7.1 Default Domains
Ready-to-use domain configs:
- `domains/aiml.json` - AI/Machine Learning
- `domains/devops.json` - DevOps/Infrastructure
- `domains/frontend.json` - Frontend Development
- `domains/backend.json` - Backend Development

### 7.2 Add Custom Domain
Create `skill_gap_db/domains/custom_domain.json`:

```json
{
  "required_skills": {
    "must_have": ["Skill1", "Skill2", "Skill3"],
    "good_to_have": ["Skill4", "Skill5"],
    "advanced": ["Skill6", "Skill7"]
  },
  "projects_expected": ["Project 1", "Project 2"],
  "certifications_valued": ["Cert 1", "Cert 2"]
}
```

### 7.3 Add Company Requirements
Create `skill_gap_db/companies/company_name.json`:

```json
{
  "company": "CompanyName",
  "specific_requirements": {
    "backend": {
      "extra_skills": ["Tech1", "Tech2"],
      "bar": "Interview difficulty level",
      "portfolio_bar": "What they want to see"
    }
  },
  "interview_focus": ["DSA", "System Design"],
  "resume_requirements": "What resume should show"
}
```

---

## 📝 Step 8: Add Job Listings

### 8.1 Job File Format
`job_folder/jobs.json`:

```json
[
  {
    "id": "unique_id",
    "title": "Senior Backend Engineer",
    "company": "TechCo",
    "domain": "backend",
    "description": "Job description...",
    "required_skills": ["Python", "Docker", "API Design"],
    "location": "San Francisco",
    "url": "https://example.com/jobs/123"
  }
]
```

### 8.2 Add Your Jobs
1. Create JSON files in `job_folder/`
2. Each file can contain array of jobs
3. Supported formats: `.json` files
4. Subdirectories supported (recursive)

---

## 🧪 Step 9: Testing & Verification

### 9.1 Test Resume Parsing
```bash
python
>>> from agent.resume_parser import parse_resume
>>> data = parse_resume("resume.pdf")
>>> print(data['skills'])
```

### 9.2 Test GitHub Fetcher
```bash
python
>>> from agent.github_fetcher import fetch_github_data
>>> data = fetch_github_data("torvalds")
>>> print(data['public_repos'])
```

### 9.3 Test ATS Scoring
```bash
python
>>> from agent.ats_scorer import calculate_ats_score
>>> score = calculate_ats_score(resume_data, "backend")
>>> print(score['total_score'])
```

### 9.4 Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# List domains
curl http://localhost:8000/api/domains

# List companies
curl http://localhost:8000/api/companies

# Job statistics
curl http://localhost:8000/api/jobs-stats

# System status
curl http://localhost:8000/api/status
```

---

## 🚨 Troubleshooting

### Problem: "Cannot connect to Ollama"
**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve

# Windows users: Check Services or taskbar
```

### Problem: "pdfplumber module not found"
**Solution:**
```bash
# Make sure venv is activated
pip install pdfplumber

# Verify
python -c "import pdfplumber; print('OK')"
```

### Problem: "FileNotFoundError: skill_gap_db"
**Solution:**
```bash
# Verify folder structure from hirepath_final root:
# Should exist:
dir skill_gap_db\domains
dir skill_gap_db\companies

# If missing, create manually with JSON files
```

### Problem: "Port 8000 already in use"
**Solution:**
```bash
# Use different port
uvicorn main:app --reload --port 8001

# Or kill process on port 8000:
# Windows:
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac:
lsof -i :8000
kill -9 <pid>
```

### Problem: "Resume parsing fails"
**Solution:**
```bash
# Check file format (PDF or DOCX only)
# Check file is not corrupted
# Try conversion to PDF first

# For DOCX issues:
pip install --upgrade python-docx

# For PDF issues:
pip install --upgrade pdfplumber
```

### Problem: GitHub API rate limiting
**Solution:**
```bash
# Public API: 60 requests/hour per IP
# Cache results to avoid repeated calls
# Resume-only analysis works without GitHub

# Cache is stored in: github_cache/
```

---

## ⚙️ Configuration Files

### main.py Configuration
```python
# Top of main.py - modify these:
UPLOAD_FOLDER = Path(__file__).parent.parent / "resume_uploads"
JOB_FOLDER = Path(__file__).parent.parent / "job_folder"
SKILL_GAP_DB = Path(__file__).parent.parent / "skill_gap_db"
```

### Ollama Configuration
```python
# In ollama_client.py:
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"
TIMEOUT = 60
```

### API Port
```python
# In main.py:
uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 📊 Performance Tuning

### For Slower Machines
Use faster Ollama model:
```python
# In ollama_client.py
DEFAULT_MODEL = "mistral"  # Instead of llama3
```

### For Large Resume Databases
Implement caching:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def load_job_listings():
    # Cache job listings
    pass
```

### For Production
```bash
# Use Gunicorn instead of Uvicorn
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:8000 agent.main:app
```

---

## 🔐 Security Considerations

### Private Resumes
- Delete resumes after processing: Delete from `resume_uploads/`
- Or disable uploads: Set `UPLOAD_FOLDER = None`

### GitHub Privacy
- Uses public GitHub API only
- Never sends auth tokens
- Respects GitHub privacy settings
- Skips private repositories

### Data Storage
- All data stays local
- No cloud sync by default
- Optional: Configure backups manually

---

## 📈 Monitoring

### Check Logs
```bash
# FastAPI logs show in terminal
# Watch for errors:
ERROR: <error message>

# Ollama logs:
# Check in Ollama system tray or logs folder
```

### Performance Metrics
```bash
# Check API response times in OpenAPI docs:
# http://localhost:8000/docs

# Manual timing:
time curl http://localhost:8000/api/analyze ...
```

### Resource Usage
```bash
# Windows:
tasklist | findstr python
# Check Memory in Task Manager

# Linux/Mac:
ps aux | grep python
top  # Watch resource usage
```

---

## 🔄 Backup & Restore

### Backup Your Data
```bash
# Backup all configuration
robocopy skill_gap_db backup\skill_gap_db /S
robocopy job_folder backup\job_folder /S

# Or zip for safety
tar -czf hirepath_backup.tar.gz skill_gap_db job_folder
```

### Restore
```bash
# Restore from backup
robocopy backup\skill_gap_db skill_gap_db /S

# Or unzip
tar -xzf hirepath_backup.tar.gz
```

---

## 🚀 Production Deployment

### Heroku/Cloud Deployment
```bash
# Add Procfile
echo "web: gunicorn agent.main:app" > Procfile

# Use cloud storage for resume uploads
# Configure environment variables
```

### Docker Deployment
```dockerfile
FROM python:3.11
WORKDIR /app
COPY agent/requirements.txt .
RUN pip install -r requirements.txt
COPY agent /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
```

---

## ✅ Final Verification Checklist

- [ ] Ollama running and models installed
- [ ] Python venv activated with dependencies
- [ ] FastAPI server running on port 8000
- [ ] `/api/status` endpoint returns healthy
- [ ] Resume parsing works (`/api/ats-check`)
- [ ] Skill gap endpoint works (`/api/skill-gap`)
- [ ] Job matching returns results (`/api/jobs-stats`)
- [ ] Ollama analysis works (GitHub analysis endpoint)
- [ ] Frontend (optional) running on port 3000
- [ ] All JSON configs properly formatted

---

## 🎓 Next Steps

1. **Upload your resume** via API
2. **Check ATS score** to see baseline
3. **Review skill gaps** for your domain
4. **Generate roadmap** for 90-day plan
5. **Check job matches** in your field
6. **Start learning** top priority skills
7. **Build portfolio projects** from recommendations
8. **Prepare for interviews** using generated guide

---

## 📞 Getting Help

1. Check `/api/status` for system health
2. Review `.../agent/main.py` comments
3. See README.md for API documentation
4. Check individual module docstrings
5. Verify all JSON configs are valid

---

**Happy career accelerating! 🚀**

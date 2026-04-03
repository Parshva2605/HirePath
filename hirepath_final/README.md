# 🚀 HirePath — Career Acceleration System

**HirePath AI** is a comprehensive, 100% local career acceleration platform that analyzes your resume, GitHub profile, and target domain to provide:

✅ ATS Score & Resume Optimization  
✅ Skill Gap Analysis (Domain + Company specific)  
✅ GitHub Project Quality Assessment  
✅ Personalized 90-Day Career Roadmap  
✅ Interview Preparation Guide  
✅ Job Matching from Local Database  

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Frontend: Next.js (resume-lm based)   │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│   FastAPI Backend (Python)              │
│   ├─ Resume Parser                      │
│   ├─ GitHub Fetcher                     │
│   ├─ ATS Scorer                         │
│   ├─ Skill Gap Analyzer                 │
│   ├─ Job Matcher                        │
│   └─ Ollama Integration                 │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┴────────────────────┐
    │                              │
┌───▼───────────┐    ┌────────────▼──┐
│  Ollama (LLM) │    │  Local Files   │
│  - llama3     │    │ - Resume JSON  │
│  - mistral    │    │ - Job DB       │
│  - deepseek   │    │ - Skill DB     │
└───────────────┘    └────────────────┘
```

## 📋 Quick Start

### 1. Prerequisites
- **Ollama** running locally (`ollama serve`)
- **Python 3.9+**
- **Node.js 16+** (for resume-lm frontend)

### 2. Installation

```bash
# Clone/prepare this repository
cd D:\HirePath\hirepath_final

# Install Python dependencies
cd agent
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start FastAPI backend
uvicorn main:app --reload --port 8000
```

### 3. Start Ollama

```bash
# In a new terminal
ollama serve
# Then in another terminal, pull models:
ollama pull llama3
ollama pull mistral
```

### 4. Optional: Frontend for Resume Optimization

```bash
# Clone resume-lm (one time)
cd D:\HirePath
git clone https://github.com/olyaiy/resume-lm.git
cd resume-lm
npm install

# Create .env.local
echo "OLLAMA_BASE_URL=http://localhost:11434" > .env.local

# Run Next.js dev server
npm run dev
# Visit http://localhost:3000
```

## 🔄 Full Analysis Pipeline

### Input
```json
{
  "resume": "resume.pdf or resume.docx",
  "domain": "aiml | devops | frontend | backend | data_engineering | fullstack",
  "company": "Google | Amazon | Microsoft | Startup | [custom]",
  "github_url": "https://github.com/username"
}
```

### API Call
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "resume=@resume.pdf" \
  -F "domain=aiml" \
  -F "company=Google" \
  -F "github_url=https://github.com/username"
```

### Output
```json
{
  "ats_score": {
    "total_score": 72.5,
    "breakdown": {
      "keyword_match": 75,
      "format": 90,
      "quantification": 60,
      "length": 85,
      "action_verbs": 80
    }
  },
  "skill_gap": {
    "readiness_score": 68,
    "readiness_level": "Good - Minor gaps",
    "must_have_coverage": 85,
    "good_to_have_coverage": 60,
    "advanced_coverage": 40
  },
  "github_analysis": {
    "quality_score": 78,
    "strongest_projects": [...],
    "projects_to_build": [...],
    "skills_to_learn": [...]
  },
  "career_roadmap": "90-day plan with phases...",
  "job_matches": {
    "total": 12,
    "jobs": [...],
    "top_missing_skills": [...]
  },
  "interview_preparation": "Interview prep guide..."
}
```

## 📁 Project Structure

```
hirepath_final/
├── agent/                          # Python backend
│   ├── main.py                    # FastAPI orchestrator
│   ├── resume_parser.py           # PDF/DOCX parsing
│   ├── github_fetcher.py          # GitHub API integration
│   ├── ats_scorer.py              # ATS scoring logic
│   ├── skill_gap.py               # Skill analysis
│   ├── ollama_client.py           # LLM integration
│   ├── resume_optimizer.py        # Resume optimization bridge
│   ├── job_matcher.py             # Job matching engine
│   ├── requirements.txt           # Python dependencies
│   └── __init__.py
│
├── skill_gap_db/                  # Configuration databases
│   ├── domains/
│   │   ├── aiml.json             # AI/ML skill requirements
│   │   ├── devops.json           # DevOps requirements
│   │   ├── frontend.json         # Frontend requirements
│   │   ├── backend.json          # Backend requirements
│   │   └── ...
│   └── companies/
│       ├── google.json           # Google-specific requirements
│       ├── amazon.json           # Amazon requirements
│       ├── microsoft.json        # Microsoft requirements
│       ├── startup.json          # Startup requirements
│       └── ...
│
├── job_folder/                    # Job listings database
│   └── sample_jobs.json          # Example job listings
│
├── resume_uploads/               # User uploaded resumes
│
└── github_cache/                 # Cached GitHub data (optional)
```

## 🎯 Use Cases

### 1. Quick ATS Check
```bash
curl -X POST http://localhost:8000/api/ats-check \
  -F "resume=@resume.pdf" \
  -F "domain=backend"
```

### 2. Skill Gap Check
```bash
curl -X POST http://localhost:8000/api/skill-gap \
  -F "user_skills=Python,Docker,FastAPI" \
  -F "domain=devops" \
  -F "company=Amazon"
```

### 3. List Available Domains
```bash
curl http://localhost:8000/api/domains
```

### 4. System Status
```bash
curl http://localhost:8000/api/status
```

## 🧠 Key Features

### ATS Scoring (0-100)
- **Keyword Match (40%)** - Domain-specific terminology
- **Format (20%)** - Required sections, readability
- **Quantification (20%)** - Metrics and numbers in bullets
- **Length (10%)** - Optimal word count (400-700)
- **Action Verbs (10%)** - Strong bullet starters

### Skill Gap Analysis
- **Must-Have Skills** - Critical for the role
- **Good-to-Have Skills** - Competitive advantage
- **Advanced Skills** - Future growth
- **Readiness Scoring** - Overall preparation (0-100)

### GitHub Analysis (via Ollama)
- Project quality assessment
- Strongest portfolio pieces identification
- Portfolio gaps detection
- Specific project recommendations
- Skill learning priorities

### Career Roadmap (90-day)
- **Phase 1: Foundations** (Days 1-30)
  - Immediate resume fixes
  - Foundational skill learning
  - Quick wins
  
- **Phase 2: Building** (Days 31-60)
  - Major project development
  - Skill deepening
  - Open source contributions
  
- **Phase 3: Polish** (Days 61-90)
  - Portfolio refinement
  - Advanced skills
  - Interview preparation
  - Job search strategy

### Interview Preparation
- Domain-specific technical topics
- System design focus areas
- Behavioral question preparation
- Company culture fit
- Mock interview strategy

### Job Matching
- Skills-based matching (60% weight)
- Domain relevance (40% weight)
- Missing skills across matched jobs
- Reachable jobs with new skills
- Job market summary statistics

## 🤖 Ollama Configuration

### Available Models
```bash
ollama pull llama3          # Best for general tasks
ollama pull mistral         # Faster, lighter
ollama pull deepseek-coder  # Better for code analysis
```

### Environment Variables
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### Model Selection
- **General Analysis**: `llama3`
- **Fast Processing**: `mistral`
- **Code Analysis**: `deepseek-coder`

## 📊 Skill Database Format

### Domain Configuration (domains/aiml.json)
```json
{
  "required_skills": {
    "must_have": ["Python", "Machine Learning", "..."],
    "good_to_have": ["MLOps", "Docker", "..."],
    "advanced": ["CUDA", "JAX", "..."]
  },
  "projects_expected": ["ML project...", "..."],
  "certifications_valued": ["AWS ML", "..."]
}
```

### Company Configuration (companies/google.json)
```json
{
  "company": "Google",
  "specific_requirements": {
    "aiml": {
      "extra_skills": ["JAX", "Vertex AI"],
      "bar": "Strong CS fundamentals...",
      "portfolio_bar": "Published papers OR top Kaggle"
    }
  },
  "interview_focus": ["DSA", "System Design", "..."]
}
```

## 🔐 Security Notes

- ✅ **100% Local Processing** - No data sent to external services
- ✅ **GitHub REST API** - Public endpoints only, no auth token needed
- ✅ **Resume Privacy** - Resumes stored locally only
- ✅ **LLM Local** - Ollama runs on your machine

## 🛠️ Troubleshooting

### Ollama Connection Error
```
Error: Cannot connect to Ollama
Solution: 
  1. Start Ollama: ollama serve
  2. Check http://localhost:11434/api/tags
```

### Resume Parsing Error
```
Error: pdfplumber not installed
Solution: pip install pdfplumber python-docx
```

### Spacy Model Missing
```
Error: SpacyError
Solution: python -m spacy download en_core_web_sm
```

### GitHub Profile Not Found
```
Error: Invalid GitHub URL
Solution: Use full URL or username only
  Valid: https://github.com/username OR username
```

## 📈 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Resume Parsing | <1s | PDF/DOCX |
| GitHub Fetch | 5-10s | 100 repos max |
| ATS Scoring | <1s | Local calculation |
| Skill Gap | <1s | JSON lookup + scoring |
| GitHub Analysis | 20-60s | Ollama LLM call |
| Career Roadmap | 30-90s | Ollama LLM call |
| Job Matching | <2s | Local database |
| Full Pipeline | 1-3 min | All steps combined |

## 🚦 API Endpoints

### Core Analysis
- `POST /api/analyze` - Full pipeline analysis
- `POST /api/ats-check` - Quick ATS score
- `POST /api/skill-gap` - Skill gap analysis

### Lookup
- `GET /api/domains` - List domains
- `GET /api/companies` - List companies
- `GET /api/jobs-stats` - Job database stats

### Validation
- `POST /api/validate-github` - Check GitHub URL
- `GET /api/status` - System status check
- `GET /api/health` - Health check

## 📝 Example Resume Content

Good ATS Score Indicators:
- ✅ Clear sections: Summary, Experience, Skills, Education
- ✅ Bullet points starting with action verbs
- ✅ Quantified metrics: "increased by 40%", "reduced by 2 hours"
- ✅ Domain keywords naturally integrated
- ✅ 400-700 words for 1 page resume
- ✅ standard fonts, no images/tables

Bad ATS Score Indicators:
- ❌ No clear sections
- ❌ Generic descriptions without metrics
- ❌ Tables, columns, or fancy formatting
- ❌ Weak verbs: "did", "helped", "worked on"
- ❌ Too short (<300 words) or too long (>1000 words)
- ❌ Unusual fonts or PDF formatting

## 🔄 Integration Examples

### Python Script Integration
```python
from agent import parse_resume, calculate_ats_score

resume_data = parse_resume("resume.pdf")
ats_score = calculate_ats_score(resume_data, "backend")
print(f"ATS Score: {ats_score['total_score']}")
```

### Direct API Usage
```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    files={"resume": open("resume.pdf", "rb")},
    data={
        "domain": "backend",
        "company": "Google",
        "github_url": "https://github.com/username"
    }
)

print(response.json())
```

## 🎓 Learning Resources

Based on your skill gaps, HirePath recommends:

- **Machine Learning**: Fast.ai, DeepLearning.AI, Coursera
- **DevOps**: Linux Academy, KodeKloud, Udemy
- **Frontend**: freeCodeCamp, React docs, Web Dev courses
- **Backend**: Design Gurus, System Design Interview, LeetCode
- **General**: CS fundamentals, algorithms, system design

## 📞 Support & Contribution

- Issues: GitHub Issues
- Documentation: See SETUP.md
- Contributing: Pull requests welcome
- Questions: Use Discussions tab

## 📄 License

MIT License - Open source, use freely

## 🌟 Roadmap (Phase 2+)

- [ ] Course recommendations engine
- [ ] Real-time job market analytics
- [ ] Interview video feedback
- [ ] Portfolio website generator
- [ ] LinkedIn optimization
- [ ] Salary negotiation guides
- [ ] Company culture assessment
- [ ] Networking strategy

---

**Built with ❤️ for career acceleration**  
*Your AI career coach, running 100% local*

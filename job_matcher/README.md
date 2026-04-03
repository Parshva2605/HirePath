# Job Matcher Module

A standalone, reusable module that fetches real job listings and ranks them by match score against a candidate's resume skills.

## What This Does

This module:
- Fetches job listings from multiple sources (Remotive API, demo data)
- Extracts technical skills from job descriptions
- Calculates match scores (0-99) based on skill overlap
- Returns ranked list of jobs with detailed match information
- Works out-of-the-box with no API keys required (uses free sources)

Perfect for:
- Resume analysis tools
- Job recommendation systems
- Career guidance platforms
- Recruitment automation

---

## Setup (5 minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

That's it! Only requires `requests` library.

### Step 2: Copy Module to Your Project

```bash
# Copy the entire folder
cp -r job_matcher_standalone/ /path/to/your/project/
```

### Step 3: Test It Works

```bash
python example_usage.py
```

You should see job listings with match scores!

---

## API Keys Required

### ✅ No Keys Needed to Start

The module works immediately using:
- **Remotive API** (free, public, no registration)
- **Demo Jobs** (realistic fallback data)

### 🔑 Optional: Add More Job Sources

#### Adzuna (Recommended)
- **Where to get**: https://developer.adzuna.com/signup
- **Cost**: FREE (250 calls/month)
- **Coverage**: India, US, UK, 15+ countries
- **Setup time**: 2 minutes

1. Sign up at link above
2. Get `app_id` and `app_key`
3. Add to `config.py`:
   ```python
   ADZUNA_APP_ID = "your_app_id"
   ADZUNA_APP_KEY = "your_app_key"
   ENABLE_ADZUNA = True
   ```

#### LinkedIn (Advanced)
- **Where to get**: https://www.linkedin.com/developers/
- **Cost**: FREE (with limits)
- **Coverage**: Global
- **Setup time**: Requires approval (1-2 weeks)
- **Note**: Strict rate limits, best for large-scale apps

#### Indeed (Not Recommended)
- **Status**: API being phased out for new users
- **Alternative**: Use web scraping (not included in this module)

---

## Function Reference

### `fetch_and_rank_jobs()`

Main function to fetch and rank jobs.

```python
from job_matcher import fetch_and_rank_jobs

jobs = fetch_and_rank_jobs(
    resume_text="Full resume text here...",
    resume_skills=["Python", "Docker", "AWS"],
    target_role="Software Engineer",
    location="India",
    goal_type="job"
)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `resume_text` | str | Yes | - | Full resume text (used for additional matching) |
| `resume_skills` | List[str] | Yes | - | List of candidate's skills |
| `target_role` | str | Yes | - | Job role to search for |
| `location` | str | No | "India" | Location preference |
| `goal_type` | str | No | "job" | One of: "job", "internship", "promotion" |

#### Returns

List of job dictionaries (max 10), sorted by match score descending.

---

## Return Format

Each job object contains:

```json
{
  "title": "Senior Software Engineer",
  "company": "TechCorp Solutions",
  "location": "Bangalore, India",
  "url": "https://company.com/careers/job123",
  "match_score": 75,
  "match_label": "Good Match 🟡",
  "match_explanation": "Strong match — you have 6 of 8 required skills",
  "salary": "₹15,00,000 - ₹25,00,000 per annum",
  "posted_date": "2 days ago",
  "platform": "Remotive",
  "description_snippet": "We are seeking a talented Senior Software Engineer to join our dynamic team..."
}
```

### Field Descriptions

- **title**: Job title
- **company**: Company name
- **location**: Job location (city, country, or "Remote")
- **url**: Direct application URL
- **match_score**: Integer 0-99 indicating match percentage
- **match_label**: Human-readable label with emoji
  - 🟢 Strong Match (≥80%)
  - 🟡 Good Match (≥60%)
  - 🟠 Partial Match (≥40%)
  - 🔴 Weak Match (<40%)
- **match_explanation**: One-line explanation of the match
- **salary**: Salary range or "Not disclosed"
- **posted_date**: When job was posted
- **platform**: Source platform (e.g., "Remotive", "Demo")
- **description_snippet**: First 150 characters of job description

---

## Match Score Calculation

The match score (0-99) is calculated using this algorithm:

### Step 1: Extract Skills from Job
- Parse job title and description
- Match against database of 200+ tech skills
- Use word boundary matching to avoid partial matches

### Step 2: Count Skill Overlap
```
matched_skills = count of resume_skills found in job_text
total_skills = total number of resume_skills
```

### Step 3: Calculate Percentage
```
match_score = (matched_skills / total_skills) * 100
```

### Step 4: Cap at 99
```
match_score = min(match_score, 99)
```
We cap at 99 to avoid showing "perfect" 100% matches.

### Example

**Resume Skills**: `["Python", "Docker", "AWS", "Kubernetes", "FastAPI"]` (5 skills)

**Job Description**: Contains "Python", "Docker", and "AWS"

**Calculation**:
- Matched: 3 skills
- Total: 5 skills
- Score: (3/5) * 100 = 60%
- Label: "Good Match 🟡"

---

## Integration into New Project

### FastAPI Example

```python
from fastapi import FastAPI
from job_matcher import fetch_and_rank_jobs

app = FastAPI()

@app.post("/api/match-jobs")
def match_jobs(resume_text: str, skills: list, role: str):
    jobs = fetch_and_rank_jobs(resume_text, skills, role)
    return {"jobs": jobs}
```

### Flask Example

```python
from flask import Flask, request, jsonify
from job_matcher import fetch_and_rank_jobs

app = Flask(__name__)

@app.route('/api/match-jobs', methods=['POST'])
def match_jobs():
    data = request.json
    jobs = fetch_and_rank_jobs(
        resume_text=data['resume_text'],
        resume_skills=data['skills'],
        target_role=data['role']
    )
    return jsonify(jobs)
```

### Django Example

```python
from django.http import JsonResponse
from job_matcher import fetch_and_rank_jobs

def match_jobs(request):
    data = json.loads(request.body)
    jobs = fetch_and_rank_jobs(
        resume_text=data['resume_text'],
        resume_skills=data['skills'],
        target_role=data['role']
    )
    return JsonResponse({'jobs': jobs})
```

---

## Troubleshooting

### Issue: No jobs returned

**Cause**: API timeout or network issue

**Solution**:
1. Check internet connection
2. Increase timeout in `config.py`:
   ```python
   REQUEST_TIMEOUT = 30  # Increase from 10 to 30 seconds
   ```
3. Demo jobs should still appear as fallback

### Issue: All match scores are 0

**Cause**: Resume skills don't match job descriptions

**Solution**:
1. Ensure `resume_skills` contains actual technical skills
2. Use common skill names (e.g., "JavaScript" not "JS")
3. Check skills database in `job_matcher.py` - add missing skills if needed

### Issue: Import error

**Cause**: Module not in Python path

**Solution**:
```python
import sys
sys.path.append('/path/to/job_matcher_standalone')
from job_matcher import fetch_and_rank_jobs
```

### Issue: Requests timeout

**Cause**: Slow network or API down

**Solution**:
1. Module automatically falls back to demo jobs
2. Adjust timeout in `config.py`
3. Disable slow sources:
   ```python
   ENABLE_REMOTIVE = False  # If Remotive is slow
   ```

### Issue: Want more jobs

**Cause**: Default limit is 10 jobs

**Solution**:
Modify `config.py`:
```python
MAX_JOBS_RETURNED = 20  # Increase from 10 to 20
```

---

## For AI Assistants / Teammates

### Plain English Explanation

**What this module does:**
1. Takes a candidate's resume and skills
2. Fetches job listings from the internet
3. Compares candidate's skills with job requirements
4. Gives each job a score (0-99) showing how good the match is
5. Returns top 10 jobs sorted by best match first

**Files in this module:**

- `job_matcher.py` - Main code, does all the work
- `config.py` - Settings and API keys (all optional)
- `requirements.txt` - Just needs `requests` library
- `example_usage.py` - Shows 6 different ways to use it
- `README.md` - This file, explains everything
- `ARCHITECTURE.md` - Technical details for developers

**How to use it:**
```python
from job_matcher import fetch_and_rank_jobs

jobs = fetch_and_rank_jobs(
    resume_text="I'm a Python developer...",
    resume_skills=["Python", "Django", "PostgreSQL"],
    target_role="Backend Developer"
)

for job in jobs:
    print(f"{job['title']} - {job['match_score']}% match")
```

**Key features:**
- Works immediately, no setup needed
- No API keys required (uses free sources)
- Returns realistic job data
- Match scores are accurate and explainable
- Easy to integrate into any Python project

**When to use this:**
- Building a resume analyzer
- Creating a job recommendation system
- Helping candidates find relevant jobs
- Automating recruitment workflows

**Limitations:**
- Returns max 10 jobs per search
- Match score is based only on skill overlap (not experience, location, etc.)
- Free sources have limited job coverage
- No real-time job updates (depends on API freshness)

---

## License

This module is part of the HirePath project and can be freely copied and used in any project.

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review `example_usage.py` for working examples
3. Read `ARCHITECTURE.md` for technical details
4. Modify `config.py` to adjust behavior

---

**Last Updated**: 2024
**Version**: 1.0.0
**Tested With**: Python 3.8+

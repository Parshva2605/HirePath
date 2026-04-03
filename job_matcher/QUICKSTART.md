# Quick Start Guide

Get the job matcher running in 2 minutes!

## Step 1: Install (30 seconds)

```bash
pip install requests
```

That's it! Only one dependency.

## Step 2: Test (30 seconds)

```bash
cd job_matcher_standalone
python example_usage.py
```

You should see job listings with match scores!

## Step 3: Use in Your Code (1 minute)

```python
from job_matcher import fetch_and_rank_jobs

# Your candidate's data
resume_skills = ["Python", "Docker", "AWS", "Kubernetes"]
resume_text = "DevOps engineer with 2 years experience..."

# Fetch and rank jobs
jobs = fetch_and_rank_jobs(
    resume_text=resume_text,
    resume_skills=resume_skills,
    target_role="DevOps Engineer",
    location="India",
    goal_type="job"
)

# Display results
for job in jobs:
    print(f"{job['title']} at {job['company']}")
    print(f"Match: {job['match_score']}% - {job['match_label']}")
    print(f"Apply: {job['url']}\n")
```

## That's It!

You now have a working job matcher.

### Next Steps

- Read [README.md](README.md) for full documentation
- Check [example_usage.py](example_usage.py) for more examples
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how it works
- Modify [config.py](config.py) to customize behavior

### Common Use Cases

**1. Add to FastAPI**
```python
from fastapi import FastAPI
from job_matcher import fetch_and_rank_jobs

app = FastAPI()

@app.post("/match-jobs")
def match_jobs(resume_text: str, skills: list, role: str):
    return fetch_and_rank_jobs(resume_text, skills, role)
```

**2. Filter High Matches Only**
```python
jobs = fetch_and_rank_jobs(...)
strong_matches = [j for j in jobs if j['match_score'] >= 70]
```

**3. Get Remote Jobs Only**
```python
jobs = fetch_and_rank_jobs(...)
remote_jobs = [j for j in jobs if 'remote' in j['location'].lower()]
```

### Troubleshooting

**No jobs returned?**
- Check internet connection
- Demo jobs should still appear as fallback

**All match scores are 0?**
- Ensure resume_skills contains actual tech skills
- Use common names: "JavaScript" not "JS"

**Import error?**
```python
import sys
sys.path.append('/path/to/job_matcher_standalone')
from job_matcher import fetch_and_rank_jobs
```

### Need Help?

1. Check [README.md](README.md) - Comprehensive documentation
2. Run [example_usage.py](example_usage.py) - 6 working examples
3. Read [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details

---

**Ready to integrate?** Copy the entire `job_matcher_standalone/` folder to your project and start using it!

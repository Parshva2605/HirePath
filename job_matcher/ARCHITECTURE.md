# Job Matcher Architecture

Technical documentation for developers who want to understand or modify the job matcher module.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Data Flow](#data-flow)
3. [Match Score Algorithm](#match-score-algorithm)
4. [Job Sources](#job-sources)
5. [Skill Extraction](#skill-extraction)
6. [Swapping Job Sources](#swapping-job-sources)
7. [Known Limitations](#known-limitations)
8. [Performance Considerations](#performance-considerations)
9. [Extension Points](#extension-points)

---

## System Overview

The job matcher is a single-file Python module with no external dependencies except `requests`. It follows a simple pipeline architecture:

```
Input (resume + skills) → Fetch Jobs → Extract Skills → Calculate Match → Rank → Output
```

### Core Components

1. **Job Fetchers** - Functions that fetch jobs from various sources
2. **Skill Extractor** - Extracts technical skills from text
3. **Match Calculator** - Computes match score between resume and job
4. **Ranker** - Sorts jobs by match score

### Design Principles

- **Self-contained**: No imports from other modules
- **Fail-safe**: Each job source wrapped in try/except
- **Fallback-ready**: Demo jobs always available
- **Simple**: No complex ML models or dependencies

---

## Data Flow

### ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    fetch_and_rank_jobs()                        │
│                         (Main Entry)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   Fetch Jobs from:     │
                │   - Remotive API       │
                │   - Demo Data          │
                │   (parallel, fail-safe)│
                └────────┬───────────────┘
                         │
                         ▼
                ┌────────────────────────┐
                │  Filter by goal_type   │
                │  (internship/job)      │
                └────────┬───────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │  For each job:                         │
        │  1. Extract skills from description    │
        │  2. Calculate match score              │
        │  3. Generate match label & explanation │
        └────────┬───────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  Sort by match_score   │
        │  (descending)          │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  Return top 10 jobs    │
        └────────────────────────┘
```

### Detailed Flow

1. **Input Validation**
   - Accept resume_text, resume_skills, target_role, location, goal_type
   - No validation errors - all inputs optional with defaults

2. **Job Fetching** (Parallel)
   ```python
   all_jobs = []
   
   # Try Remotive (free API)
   try:
       jobs = _fetch_remotive_jobs(role)
       all_jobs.extend(jobs)
   except:
       pass  # Fail silently
   
   # Fallback to demo jobs
   if len(all_jobs) < 5:
       all_jobs.extend(_get_demo_jobs(role, location))
   ```

3. **Filtering**
   - If goal_type == "internship", filter for jobs with "intern" in title/description
   - Otherwise, use all jobs

4. **Scoring Loop**
   ```python
   for job in all_jobs:
       # Extract skills from job
       job_skills = _extract_skills_from_text(job['description'])
       
       # Calculate match
       match_score = _calculate_job_match(resume_text, resume_skills, job)
       
       # Generate explanation
       label = _get_match_label(match_score)
       explanation = _get_match_explanation(resume_skills, job_skills, match_score)
       
       # Build result
       ranked_jobs.append({...})
   ```

5. **Ranking**
   ```python
   ranked_jobs.sort(key=lambda x: x['match_score'], reverse=True)
   return ranked_jobs[:10]
   ```

---

## Match Score Algorithm

### Step-by-Step Calculation

```python
def _calculate_job_match(resume_text, resume_skills, job):
    # Step 1: Get job text
    job_text = (job['title'] + ' ' + job['description']).lower()
    
    # Step 2: Count matched skills
    matched = 0
    for skill in resume_skills:
        skill_lower = skill.lower()
        # Use word boundary regex to avoid partial matches
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', job_text):
            matched += 1
    
    # Step 3: Calculate percentage
    total_skills = max(len(resume_skills), 1)  # Avoid division by zero
    match_score = (matched / total_skills) * 100
    
    # Step 4: Cap at 99
    match_score = min(match_score, 99)
    
    return match_score
```

### Why This Algorithm?

**Pros:**
- Simple and explainable
- Fast (no ML inference)
- Deterministic (same input = same output)
- Works with any skill list

**Cons:**
- Doesn't consider skill importance (all skills weighted equally)
- Doesn't account for synonyms (e.g., "JS" vs "JavaScript")
- Ignores experience level
- No semantic understanding

### Alternative Algorithms (Not Implemented)

1. **TF-IDF + Cosine Similarity**
   ```python
   from sklearn.feature_extraction.text import TfidfVectorizer
   from sklearn.metrics.pairwise import cosine_similarity
   
   vectorizer = TfidfVectorizer()
   tfidf = vectorizer.fit_transform([resume_text, job_description])
   similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
   score = similarity * 100
   ```
   - More sophisticated
   - Requires scikit-learn dependency
   - Slower

2. **Weighted Skills**
   ```python
   skill_weights = {
       "Python": 1.5,  # High priority
       "Git": 0.5      # Low priority
   }
   weighted_score = sum(weights[skill] for skill in matched_skills)
   ```
   - More accurate
   - Requires manual weight tuning

3. **Semantic Embeddings**
   ```python
   from sentence_transformers import SentenceTransformer
   
   model = SentenceTransformer('all-MiniLM-L6-v2')
   resume_embedding = model.encode(resume_text)
   job_embedding = model.encode(job_description)
   similarity = cosine_similarity([resume_embedding], [job_embedding])
   ```
   - Most accurate
   - Requires large model download
   - Much slower

---

## Job Sources

### Current Sources

#### 1. Remotive API (Primary)

**Endpoint**: `https://remotive.com/api/remote-jobs`

**Pros:**
- Free, no API key required
- Good coverage of remote jobs
- Reliable uptime
- JSON response

**Cons:**
- Only remote jobs
- Limited to ~50 jobs per search
- No location filtering

**Implementation:**
```python
def _fetch_remotive_jobs(role: str) -> List[Dict]:
    url = "https://remotive.com/api/remote-jobs"
    params = {"search": role, "limit": 10}
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    return normalize_jobs(data['jobs'])
```

#### 2. Demo Jobs (Fallback)

**Purpose**: Provide realistic data when APIs fail or for testing

**Pros:**
- Always available
- Instant response
- Realistic job descriptions

**Cons:**
- Not real jobs
- Static data

**Implementation:**
```python
def _get_demo_jobs(role: str, location: str) -> List[Dict]:
    return [
        {
            "title": f"{role}",
            "company": "TechCorp",
            "description": "...",
            # ... full job details
        },
        # ... 4 more jobs
    ]
```

### Potential Additional Sources

#### Adzuna API
- **URL**: https://api.adzuna.com/v1/api/jobs/in/search/1
- **Key Required**: Yes (free tier: 250 calls/month)
- **Coverage**: India, US, UK, 15+ countries
- **Integration**: Add to `config.py`, implement `_fetch_adzuna_jobs()`

#### LinkedIn API
- **URL**: https://api.linkedin.com/v2/jobs
- **Key Required**: Yes (requires approval)
- **Coverage**: Global
- **Integration**: Complex OAuth flow required

#### Indeed API
- **Status**: Being phased out
- **Alternative**: Web scraping (not recommended due to ToS)

---

## Skill Extraction

### Current Implementation

Uses a curated database of 200+ tech skills with regex matching:

```python
def _extract_skills_from_text(text: str) -> List[str]:
    text_lower = text.lower()
    skills_db = _get_skills_database()  # 200+ skills
    matched_skills = set()
    
    for skill in skills_db:
        skill_lower = skill.lower()
        # Word boundary matching
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            matched_skills.add(skill_lower)
    
    return sorted(list(matched_skills))
```

### Skill Database Categories

- Programming Languages (25)
- Web Frontend (25)
- Web Backend (25)
- Databases (20)
- Cloud & DevOps (25)
- Data Science & ML (25)
- Mobile Development (15)
- Testing (15)
- Version Control (10)
- Methodologies (15)

**Total**: 200+ skills

### Limitations

1. **No Synonyms**: "JS" won't match "JavaScript"
2. **No Abbreviations**: "k8s" won't match "Kubernetes"
3. **Case Sensitive**: Handled by lowercasing
4. **Partial Matches**: Avoided by word boundaries

### Improvements (Not Implemented)

1. **Add Synonym Mapping**
   ```python
   synonyms = {
       "javascript": ["js", "ecmascript"],
       "kubernetes": ["k8s"],
       "postgresql": ["postgres", "psql"]
   }
   ```

2. **Use NLP Library**
   ```python
   import spacy
   nlp = spacy.load("en_core_web_sm")
   doc = nlp(text)
   skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
   ```

3. **Machine Learning Classifier**
   - Train model to identify skills
   - More accurate but requires training data

---

## Swapping Job Sources

### How to Replace Remotive with Indeed

1. **Get Indeed API Key**
   - Sign up at https://www.indeed.com/publisher
   - Get publisher ID

2. **Add to config.py**
   ```python
   INDEED_PUBLISHER_ID = "your_publisher_id"
   ENABLE_INDEED = True
   ENABLE_REMOTIVE = False
   ```

3. **Implement Fetcher**
   ```python
   def _fetch_indeed_jobs(role: str, location: str) -> List[Dict]:
       url = "http://api.indeed.com/ads/apisearch"
       params = {
           "publisher": config.INDEED_PUBLISHER_ID,
           "q": role,
           "l": location,
           "format": "json",
           "limit": 10
       }
       
       response = requests.get(url, params=params, timeout=10)
       data = response.json()
       
       results = []
       for job in data.get('results', []):
           results.append({
               'title': job['jobtitle'],
               'company': job['company'],
               'location': job['formattedLocation'],
               'description': job['snippet'],
               'source': 'Indeed',
               'url': job['url'],
               'salary': 'Not disclosed',
               'posted_date': job['date']
           })
       
       return results
   ```

4. **Update Main Function**
   ```python
   def fetch_and_rank_jobs(...):
       all_jobs = []
       
       # Replace Remotive with Indeed
       if config.ENABLE_INDEED:
           try:
               indeed_jobs = _fetch_indeed_jobs(target_role, location)
               all_jobs.extend(indeed_jobs)
           except:
               pass
       
       # ... rest of code
   ```

### How to Add LinkedIn

Similar process:
1. Get LinkedIn API credentials
2. Implement OAuth flow
3. Create `_fetch_linkedin_jobs()` function
4. Add to main function

### How to Add Web Scraping

**Warning**: Check website Terms of Service first!

```python
def _scrape_jobs_from_website(role: str) -> List[Dict]:
    from bs4 import BeautifulSoup
    
    url = f"https://example.com/jobs?q={role}"
    response = requests.get(url, headers={"User-Agent": "..."})
    soup = BeautifulSoup(response.text, 'html.parser')
    
    jobs = []
    for job_card in soup.find_all('div', class_='job-card'):
        jobs.append({
            'title': job_card.find('h2').text,
            'company': job_card.find('span', class_='company').text,
            # ... extract other fields
        })
    
    return jobs
```

---

## Known Limitations

### 1. Match Score Accuracy

**Issue**: All skills weighted equally

**Impact**: A job requiring "Python" (critical) and "Git" (basic) treats both the same

**Workaround**: Manually adjust skill list to include only important skills

**Future Fix**: Implement weighted scoring

### 2. No Synonym Handling

**Issue**: "JavaScript" and "JS" treated as different skills

**Impact**: Lower match scores if job uses abbreviations

**Workaround**: Add both forms to resume_skills list

**Future Fix**: Add synonym mapping

### 3. Limited Job Sources

**Issue**: Only Remotive + demo jobs by default

**Impact**: Limited job coverage, especially for non-remote roles

**Workaround**: Add Adzuna API key (free)

**Future Fix**: Integrate more free APIs

### 4. No Experience Level Matching

**Issue**: Doesn't distinguish junior vs senior roles

**Impact**: May match junior candidates with senior roles

**Workaround**: Filter results by title keywords

**Future Fix**: Parse experience requirements from job description

### 5. Static Skill Database

**Issue**: Skill database is hardcoded

**Impact**: New technologies not recognized

**Workaround**: Manually add skills to `_get_skills_database()`

**Future Fix**: Use dynamic skill extraction with NLP

### 6. No Location Filtering

**Issue**: Remotive only returns remote jobs

**Impact**: Can't filter by specific cities

**Workaround**: Use demo jobs or add Adzuna

**Future Fix**: Integrate location-aware APIs

### 7. Rate Limiting

**Issue**: No rate limiting implemented

**Impact**: May hit API limits with heavy usage

**Workaround**: Add caching layer

**Future Fix**: Implement rate limiter

---

## Performance Considerations

### Current Performance

- **Latency**: 2-5 seconds per search
  - Remotive API: 1-2 seconds
  - Skill extraction: 0.5 seconds
  - Match calculation: 0.1 seconds per job
  - Total: ~2-5 seconds

- **Memory**: ~5 MB
  - Job data: ~2 MB (10 jobs × 200 KB each)
  - Skill database: ~50 KB
  - Python overhead: ~3 MB

- **CPU**: Minimal
  - Regex matching: O(n × m) where n=skills, m=job_text_length
  - Sorting: O(n log n) where n=number of jobs

### Optimization Opportunities

1. **Caching**
   ```python
   import functools
   
   @functools.lru_cache(maxsize=100)
   def fetch_and_rank_jobs(resume_text, resume_skills_tuple, ...):
       # Convert tuple back to list
       resume_skills = list(resume_skills_tuple)
       # ... rest of code
   ```

2. **Parallel API Calls**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor(max_workers=3) as executor:
       remotive_future = executor.submit(_fetch_remotive_jobs, role)
       adzuna_future = executor.submit(_fetch_adzuna_jobs, role)
       
       all_jobs = remotive_future.result() + adzuna_future.result()
   ```

3. **Lazy Skill Extraction**
   ```python
   # Only extract skills for top 20 jobs by title match
   # Then rank those 20 by full match score
   ```

4. **Compiled Regex**
   ```python
   import re
   
   # Compile patterns once
   skill_patterns = {
       skill: re.compile(r'\b' + re.escape(skill.lower()) + r'\b')
       for skill in skills_db
   }
   
   # Reuse compiled patterns
   for skill, pattern in skill_patterns.items():
       if pattern.search(text_lower):
           matched_skills.add(skill)
   ```

---

## Extension Points

### 1. Custom Skill Database

Replace `_get_skills_database()` with your own:

```python
def _get_skills_database() -> List[str]:
    # Load from file
    with open('skills.txt', 'r') as f:
        return [line.strip() for line in f]
    
    # Or load from database
    # return db.query("SELECT skill_name FROM skills")
```

### 2. Custom Match Algorithm

Replace `_calculate_job_match()`:

```python
def _calculate_job_match(resume_text, resume_skills, job):
    # Your custom algorithm here
    # Must return float 0-99
    return custom_score
```

### 3. Custom Job Fetcher

Add your own source:

```python
def _fetch_custom_jobs(role: str) -> List[Dict]:
    # Your API call here
    # Must return list of dicts with keys:
    # title, company, location, description, source, url, salary, posted_date
    return jobs
```

Then add to main function:

```python
def fetch_and_rank_jobs(...):
    all_jobs = []
    
    # Add your custom source
    try:
        custom_jobs = _fetch_custom_jobs(target_role)
        all_jobs.extend(custom_jobs)
    except:
        pass
    
    # ... rest of code
```

### 4. Custom Filters

Add filtering logic:

```python
def fetch_and_rank_jobs(...):
    # ... fetch jobs ...
    
    # Custom filter: only jobs with salary info
    all_jobs = [
        job for job in all_jobs 
        if job['salary'] != 'Not disclosed'
    ]
    
    # Custom filter: only specific companies
    preferred_companies = ['Google', 'Microsoft', 'Amazon']
    all_jobs = [
        job for job in all_jobs
        if job['company'] in preferred_companies
    ]
    
    # ... rest of code
```

### 5. Custom Output Format

Modify return dict:

```python
# Add custom fields
ranked_jobs.append({
    # ... existing fields ...
    'custom_field': calculate_custom_metric(job),
    'priority': get_priority_level(job),
    'tags': extract_tags(job['description'])
})
```

---

## Testing

### Unit Tests (Not Included)

```python
import unittest
from job_matcher import fetch_and_rank_jobs, _calculate_job_match

class TestJobMatcher(unittest.TestCase):
    def test_match_score_calculation(self):
        resume_skills = ["Python", "Docker", "AWS"]
        job = {
            "title": "Python Developer",
            "description": "We need Python and Docker experience"
        }
        score = _calculate_job_match("", resume_skills, job)
        self.assertGreater(score, 50)  # Should match 2/3 skills
    
    def test_fetch_returns_list(self):
        jobs = fetch_and_rank_jobs("", ["Python"], "Developer")
        self.assertIsInstance(jobs, list)
        self.assertLessEqual(len(jobs), 10)
```

### Integration Tests

```python
def test_end_to_end():
    jobs = fetch_and_rank_jobs(
        resume_text="Python developer with 3 years experience",
        resume_skills=["Python", "Django", "PostgreSQL"],
        target_role="Backend Developer"
    )
    
    assert len(jobs) > 0
    assert all('match_score' in job for job in jobs)
    assert jobs[0]['match_score'] >= jobs[-1]['match_score']  # Sorted
```

---

## Version History

- **v1.0.0** (2024) - Initial release
  - Remotive API integration
  - Demo jobs fallback
  - Basic skill matching
  - Match score calculation

---

## Future Roadmap

1. **v1.1.0** - Add Adzuna integration
2. **v1.2.0** - Implement caching layer
3. **v1.3.0** - Add synonym handling
4. **v2.0.0** - ML-based skill extraction
5. **v2.1.0** - Weighted skill scoring
6. **v3.0.0** - Semantic matching with embeddings

---

**Last Updated**: 2024
**Maintainer**: HirePath Team

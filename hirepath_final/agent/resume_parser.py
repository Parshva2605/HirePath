"""
Resume parsing module - Extract text and structured data from PDF/DOCX resumes.
"""

import re
from pathlib import Path
from typing import Dict, Any

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from docx import Document
except ImportError:
    Document = None


# Master skill lexicon for NLP keyword matching
SKILL_KEYWORDS = {
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "Kotlin",
    "React", "Vue", "Angular", "Next.js", "Svelte", "Redux", "Tailwind", "Material-UI",
    "Node.js", "Express", "Django", "FastAPI", "Flask", "Spring", "Spring Boot", "ASP.NET",
    "GraphQL", "REST API", "gRPC", "WebSocket",
    "Docker", "Kubernetes", "Helm", "Terraform", "Ansible",
    "AWS", "Azure", "GCP", "Google Cloud",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "DynamoDB",
    "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Scikit-learn", "Keras",
    "NLP", "Computer Vision", "Transformers", "BERT", "GPT",
    "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly",
    "Git", "GitHub", "GitLab", "Bitbucket",
    "CI/CD", "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI",
    "Linux", "Unix", "Windows", "macOS",
    "Agile", "Scrum", "Jira", "Confluence",
    "SQL", "NoSQL", "Spark", "Hadoop", "Airflow", "dbt",
    "Microservices", "Distributed Systems", "System Design",
    "Testing", "Jest", "Pytest", "Unit Tests", "Integration Tests",
    "DevOps", "MLOps", "Cloud Architecture",
    "Kubernetes", "Docker Compose", "AWS Lambda", "Cloud Functions",
    "API Gateway", "Load Balancing", "Caching", "Message Queues",
    "RabbitMQ", "Kafka", "Apache Kafka", "AWS SNS", "AWS SQS",
    "Monitoring", "Prometheus", "Grafana", "DataDog", "New Relic",
    "Logging", "ELK Stack", "Splunk", "CloudWatch",
    "JAX", "Vertex AI", "SageMaker",
    "RLHF", "RAG", "Retrieval-Augmented Generation",
    "Distributed Training", "Model Training", "Feature Engineering",
    "Data Pipeline", "ETL", "Data Engineering",
    "Accessibility", "WCAG", "SEO",
    "Performance Optimization", "Caching", "Database Optimization",
    "Security", "OAuth", "JWT", "SSL/TLS",
    "Technical Writing", "Documentation", "Communication"
}

SECTION_KEYWORDS = {
    "experience": ["experience", "professional", "work", "employment", "career"],
    "education": ["education", "degree", "university", "college", "school", "academic"],
    "skills": ["skills", "technical", "competencies", "expertise", "tools"],
    "projects": ["projects", "portfolio", "publications", "work samples", "accomplishments"],
    "certifications": ["certifications", "certificates", "licenses", "credentials"]
}

ACTION_VERBS = [
    "built", "designed", "developed", "led", "optimized", "reduced",
    "increased", "deployed", "implemented", "architected", "automated",
    "created", "engineered", "launched", "scaled", "improved",
    "enhanced", "accelerated", "streamlined", "invented", "pioneered"
]


def parse_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    if not pdfplumber:
        raise ImportError("pdfplumber not installed. Install with: pip install pdfplumber")
    
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def parse_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    if not Document:
        raise ImportError("python-docx not installed. Install with: pip install python-docx")
    
    doc = Document(file_path)
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return text


def extract_email(text: str) -> str:
    """Find email address in text."""
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Find phone number in text."""
    # US phone number patterns
    patterns = [
        r'\+1[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
        r'\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return ""


def extract_years_of_experience(text: str) -> int:
    """Estimate years of experience from text."""
    matches = re.findall(r'(\d+)\s+years?', text, re.IGNORECASE)
    if matches:
        return max(int(m) for m in matches)
    
    # Fallback: count number of job entries (rough estimate)
    job_indicators = len(re.findall(r'(job|position|role|worked|employed)', text, re.IGNORECASE))
    return max(0, job_indicators // 2)


def extract_education_level(text: str) -> str:
    """Extract education level (BS, MS, PhD, etc.)."""
    text_lower = text.lower()
    
    degrees = ["phd", "ph.d.", "doctorate", "master's", "masters", "m.s.", "ms", "m.a.",
               "bachelor's", "bachelors", "b.s.", "bs", "b.a.", "ba", "associate", "diploma"]
    
    for degree in degrees:
        if degree in text_lower:
            return degree.upper()
    
    return "Not specified"


def extract_skills(text: str) -> list:
    """Extract skills from text using keyword matching."""
    text_lower = text.lower()
    found_skills = []
    
    for skill in SKILL_KEYWORDS:
        skill_lower = skill.lower()
        # Whole word matching with word boundaries
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return list(set(found_skills))


def detect_sections(text: str) -> Dict[str, str]:
    """Detect resume sections."""
    sections = {}
    text_lower = text.lower()
    
    for section_name, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                sections[section_name] = keyword
                break
    
    return sections


def extract_job_titles(text: str) -> list:
    """Extract job titles from experience section."""
    # Common job title patterns
    job_patterns = [
        r'(\b(?:Senior|Junior|Lead|Principal|Staff|Intern|Graduate|Entry[- ]?Level)?\s+(?:Software|Data|Product|DevOps|Cloud|Security|ML|AI)\s+(?:Engineer|Developer|Architect|Scientist|Analyst|Manager)(?:\s+(?:I{1,3}|IV|V))?\b)',
        r'((?:Engineering|Data) Manager|Tech Lead|Founding Engineer|CTO|VP of Engineering)',
        r'(Front[- ]?end Developer|Backend Developer|Full[- ]?stack Developer|Web Developer)',
        r'(Machine Learning(?:\s+Engineer)?|Data Scientist|AI (?:Engineer|Researcher))',
        r'(DevOps Engineer|SRE|Cloud (?:Engineer|Architect)|Infrastructure Engineer)',
    ]
    
    titles = []
    for pattern in job_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        titles.extend(matches)
    
    return list(set(t.strip() for t in titles if t))


def extract_quantification_score(text: str) -> float:
    """Calculate percentage of lines with quantifiable metrics."""
    lines = text.split('\n')
    lines_with_numbers = sum(1 for line in lines if re.search(r'\d+', line))
    
    if not lines:
        return 0.0
    
    return round((lines_with_numbers / len(lines)) * 100, 1)


def extract_action_verb_count(text: str) -> int:
    """Count action verbs in resume."""
    text_lower = text.lower()
    verb_count = 0
    
    for verb in ACTION_VERBS:
        verb_count += len(re.findall(r'\b' + re.escape(verb) + r'\b', text_lower))
    
    return verb_count


def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Main parsing function - reads resume and extracts structured data.
    
    Args:
        file_path: Path to resume file (PDF or DOCX)
    
    Returns:
        Dictionary with parsed resume data
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")
    
    # Parse based on file extension
    if file_path.suffix.lower() == '.pdf':
        raw_text = parse_pdf(str(file_path))
    elif file_path.suffix.lower() in ['.docx', '.doc']:
        raw_text = parse_docx(str(file_path))
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    # Extract structured data
    skills = extract_skills(raw_text)
    experience_years = extract_years_of_experience(raw_text)
    education = extract_education_level(raw_text)
    job_titles = extract_job_titles(raw_text)
    sections = detect_sections(raw_text)
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)
    word_count = len(raw_text.split())
    quant_score = extract_quantification_score(raw_text)
    action_verb_count = extract_action_verb_count(raw_text)
    
    return {
        "raw_text": raw_text,
        "skills": skills,
        "experience_years": experience_years,
        "education": education,
        "job_titles": job_titles,
        "sections": sections,
        "email": email,
        "phone": phone,
        "word_count": word_count,
        "quantification_score": quant_score,
        "action_verb_count": action_verb_count,
        "file_path": str(file_path)
    }


if __name__ == "__main__":
    # Test example
    print("Resume parser module loaded successfully")
    print(f"Master skill lexicon: {len(SKILL_KEYWORDS)} skills")
    print(f"Action verbs tracked: {len(ACTION_VERBS)}")

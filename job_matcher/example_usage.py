"""
Example Usage of Job Matcher Module

This demonstrates how to use the job matcher in your application.
Run this file directly to see it in action: python example_usage.py
"""

from job_matcher import fetch_and_rank_jobs


def example_1_basic_usage():
    """Basic example with minimal parameters."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 80)
    
    # Define candidate's skills
    resume_skills = ["Python", "Docker", "AWS", "Kubernetes", "FastAPI"]
    
    # Resume text (can be full resume or summary)
    resume_text = """
    DevOps Engineer with 2 years of experience in cloud infrastructure.
    Skilled in Python, Docker, Kubernetes, AWS, and CI/CD pipelines.
    Built scalable microservices using FastAPI and deployed on AWS EKS.
    """
    
    # Fetch and rank jobs
    jobs = fetch_and_rank_jobs(
        resume_text=resume_text,
        resume_skills=resume_skills,
        target_role="DevOps Engineer",
        location="India",
        goal_type="job"
    )
    
    # Display results
    print(f"\nFound {len(jobs)} matching jobs:\n")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['title']} at {job['company']}")
        print(f"   {job['match_label']} ({job['match_score']}%)")
        print(f"   {job['match_explanation']}")
        print(f"   Location: {job['location']}")
        print(f"   Salary: {job['salary']}")
        print(f"   Apply: {job['url']}")
        print()


def example_2_software_engineer():
    """Example for Software Engineer role."""
    print("=" * 80)
    print("EXAMPLE 2: Software Engineer")
    print("=" * 80)
    
    resume_skills = [
        "JavaScript", "React", "Node.js", "TypeScript", 
        "MongoDB", "Express.js", "Git", "REST API"
    ]
    
    resume_text = """
    Full Stack Developer with 3 years of experience building web applications.
    Expert in React, Node.js, and MongoDB. Built 10+ production applications.
    Strong understanding of REST APIs, microservices, and cloud deployment.
    """
    
    jobs = fetch_and_rank_jobs(
        resume_text=resume_text,
        resume_skills=resume_skills,
        target_role="Software Engineer",
        location="Bangalore",
        goal_type="job"
    )
    
    print(f"\nTop 3 matches:\n")
    for job in jobs[:3]:
        print(f"✓ {job['title']} at {job['company']}")
        print(f"  Match: {job['match_score']}% | {job['location']}")
        print(f"  {job['description_snippet']}...")
        print()


def example_3_internship():
    """Example for finding internships."""
    print("=" * 80)
    print("EXAMPLE 3: Internship Search")
    print("=" * 80)
    
    resume_skills = ["Python", "Java", "Git", "HTML", "CSS"]
    
    resume_text = """
    Computer Science student seeking internship opportunities.
    Completed coursework in Data Structures, Algorithms, and Web Development.
    Built several academic projects using Python and Java.
    """
    
    jobs = fetch_and_rank_jobs(
        resume_text=resume_text,
        resume_skills=resume_skills,
        target_role="Software Engineer",
        location="India",
        goal_type="internship"  # Filter for internships
    )
    
    print(f"\nFound {len(jobs)} internship opportunities:\n")
    for job in jobs:
        if 'intern' in job['title'].lower():
            print(f"🎓 {job['title']} at {job['company']}")
            print(f"   Match: {job['match_score']}%")
            print()


def example_4_data_scientist():
    """Example for Data Scientist role."""
    print("=" * 80)
    print("EXAMPLE 4: Data Scientist")
    print("=" * 80)
    
    resume_skills = [
        "Python", "TensorFlow", "PyTorch", "Pandas", "NumPy",
        "Scikit-learn", "SQL", "Jupyter", "Machine Learning"
    ]
    
    resume_text = """
    Data Scientist with 4 years of experience in ML and AI.
    Built predictive models using TensorFlow and PyTorch.
    Expert in data analysis with Pandas and NumPy.
    Published research papers on deep learning applications.
    """
    
    jobs = fetch_and_rank_jobs(
        resume_text=resume_text,
        resume_skills=resume_skills,
        target_role="Data Scientist",
        location="Remote",
        goal_type="job"
    )
    
    print(f"\nTop matches with detailed info:\n")
    for job in jobs[:5]:
        print(f"📊 {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Platform: {job['platform']}")
        print(f"   Match: {job['match_label']}")
        print(f"   Posted: {job['posted_date']}")
        print(f"   URL: {job['url']}")
        print()


def example_5_json_output():
    """Example showing JSON output format."""
    print("=" * 80)
    print("EXAMPLE 5: JSON Output Format")
    print("=" * 80)
    
    import json
    
    resume_skills = ["Go", "Kubernetes", "Docker", "Microservices"]
    resume_text = "Backend engineer with Go and Kubernetes experience."
    
    jobs = fetch_and_rank_jobs(
        resume_text=resume_text,
        resume_skills=resume_skills,
        target_role="Backend Engineer",
        location="India",
        goal_type="job"
    )
    
    # Get first job as JSON
    if jobs:
        print("\nFirst job as JSON:")
        print(json.dumps(jobs[0], indent=2))


def example_6_filtering():
    """Example showing how to filter results."""
    print("=" * 80)
    print("EXAMPLE 6: Filtering Results")
    print("=" * 80)
    
    resume_skills = ["Python", "Django", "PostgreSQL", "Redis"]
    resume_text = "Python developer with Django and PostgreSQL experience."
    
    jobs = fetch_and_rank_jobs(
        resume_text=resume_text,
        resume_skills=resume_skills,
        target_role="Python Developer",
        location="India",
        goal_type="job"
    )
    
    # Filter for high match scores only
    strong_matches = [job for job in jobs if job['match_score'] >= 60]
    
    print(f"\nTotal jobs: {len(jobs)}")
    print(f"Strong matches (≥60%): {len(strong_matches)}\n")
    
    for job in strong_matches:
        print(f"✓ {job['title']} - {job['match_score']}%")
    
    # Filter by location
    remote_jobs = [job for job in jobs if 'remote' in job['location'].lower()]
    print(f"\nRemote jobs: {len(remote_jobs)}")


if __name__ == "__main__":
    # Run all examples
    example_1_basic_usage()
    print("\n" + "=" * 80 + "\n")
    
    example_2_software_engineer()
    print("\n" + "=" * 80 + "\n")
    
    example_3_internship()
    print("\n" + "=" * 80 + "\n")
    
    example_4_data_scientist()
    print("\n" + "=" * 80 + "\n")
    
    example_5_json_output()
    print("\n" + "=" * 80 + "\n")
    
    example_6_filtering()
    
    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)

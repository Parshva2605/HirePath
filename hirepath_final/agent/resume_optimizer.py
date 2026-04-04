"""
Resume optimizer - Bridge between HirePath and resume-lm for ATS optimization.
"""

import json
from typing import Dict, Any, List
from pathlib import Path
import re


AI_PHRASE_REPLACEMENTS = {
    "utilized": "used",
    "leveraged": "used",
    "orchestrated": "coordinated",
    "spearheaded": "led",
    "synergy": "collaboration",
    "robust": "reliable",
    "cutting-edge": "modern",
    "world-class": "high-quality",
}


def _clean_text(value: str) -> str:
    text = (value or "").strip()
    for bad, replacement in AI_PHRASE_REPLACEMENTS.items():
        text = re.sub(rf"\b{re.escape(bad)}\b", replacement, text, flags=re.IGNORECASE)
    text = text.replace("--", ", ").replace("---", ", ").replace("\u2014", ", ")
    return re.sub(r"\s+", " ", text).strip()


def _extract_resume_bullets(raw_text: str, limit: int = 8) -> List[str]:
    lines = [line.strip() for line in (raw_text or "").splitlines() if line.strip()]
    bullets = []
    for line in lines:
        if line.startswith(("-", "*", "•")):
            cleaned = _clean_text(line.lstrip("-*• "))
            if cleaned:
                bullets.append(cleaned)
    return bullets[:limit]


def _inject_keywords_in_bullet(bullet: str, keywords: List[str]) -> str:
    if not bullet:
        return bullet

    lower = bullet.lower()
    already = [kw for kw in keywords if kw.lower() in lower]
    if already:
        return bullet

    to_add = [kw for kw in keywords if kw][:2]
    if not to_add:
        return bullet

    if re.search(r"\d", bullet):
        return f"{bullet} using {', '.join(to_add)}"
    return f"{bullet}, focused on {', '.join(to_add)}"


def _build_targeted_edits(original_bullets: List[str], keywords: List[str], verbs: List[str]) -> List[Dict[str, str]]:
    edits: List[Dict[str, str]] = []
    action = verbs[0] if verbs else "Improved"
    for original in original_bullets[:5]:
        rewritten = _inject_keywords_in_bullet(original, keywords)
        if rewritten and not re.match(r"^[A-Za-z]+", rewritten):
            rewritten = f"{action} {rewritten[0].lower() + rewritten[1:] if len(rewritten) > 1 else rewritten.lower()}"
        rewritten = _clean_text(rewritten)
        edits.append({
            "before": original,
            "after": rewritten,
            "reason": "Increased keyword alignment while preserving original claim"
        })
    return edits


def _top_skills(skills: List[str], limit: int = 12) -> List[str]:
    seen = set()
    result = []
    for skill in skills:
        s = _clean_text(skill)
        if not s:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(s)
        if len(result) >= limit:
            break
    return result


def _build_ats_resume_markdown(preview: Dict[str, Any], contact_line: str = "") -> str:
    lines = []
    lines.append(preview.get("headline", "Candidate Resume"))
    if contact_line:
        lines.append(contact_line)
    lines.append("")
    lines.append("PROFESSIONAL SUMMARY")
    lines.append(preview.get("summary", ""))
    lines.append("")
    lines.append("TECHNICAL SKILLS")
    lines.append("Core: " + " | ".join(preview.get("technical_skills", [])))
    lines.append("Tools: " + " | ".join(preview.get("tool_skills", [])))
    lines.append("")
    lines.append("EXPERIENCE HIGHLIGHTS")
    for bullet in preview.get("experience_points", [])[:6]:
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("PROJECT HIGHLIGHTS")
    for project in preview.get("project_points", [])[:4]:
        lines.append(f"- {project}")
    lines.append("")
    lines.append("ATS KEYWORDS")
    lines.append(" | ".join(preview.get("ats_keywords", [])))
    lines.append("")
    lines.append("EDUCATION")
    lines.append(preview.get("education_line", ""))
    return "\n".join(lines).strip()


def prepare_optimization_payload(
    resume_data: Dict[str, Any],
    ats_score: Dict[str, Any],
    skill_gap: Dict[str, Any],
    domain: str,
    company: str = None
) -> Dict[str, Any]:
    """
    Prepare structured data for resume-lm optimization.
    
    Args:
        resume_data: Parsed resume data
        ats_score: ATS scoring result
        skill_gap: Skill gap analysis result
        domain: Target domain
        company: Target company
    
    Returns:
        Payload to send to resume-lm
    """
    missing_keywords = ats_score.get("keyword_analysis", {}).get("missing", [])[:10]
    must_have_skills = skill_gap.get("must_have", {}).get("missing", [])[:5]
    missing_verbs = ats_score.get("action_verbs_analysis", {}).get("missing_verbs", [])
    
    summary = resume_data.get("raw_text", "").split("\n")[:6]
    headline = resume_data.get("job_titles", [domain.title()])[0] if resume_data.get("job_titles") else domain.title()
    core_skills = _top_skills(resume_data.get("skills", []), 12)
    resume_bullets = _extract_resume_bullets(resume_data.get("raw_text", ""), 10)
    improved_bullets = [_inject_keywords_in_bullet(bullet, missing_keywords[:5]) for bullet in (resume_bullets or [])]
    if not improved_bullets:
        improved_bullets = [
            f"Built and improved {domain} workflows using {', '.join(core_skills[:3]) if core_skills else 'core tools'}, increasing delivery speed and quality.",
            f"Optimized project outcomes by applying {', '.join(missing_keywords[:3]) if missing_keywords else 'ATS-aligned keywords'} and measurable impact.",
            f"Collaborated across product and engineering to ship {company or 'target'}-ready solutions with clear documentation."
        ]

    optimized_summary = {
        "headline": f"{headline} targeting {company or domain.title()} roles",
        "summary": (
            f"{domain.title()} professional with {resume_data.get('experience_years', 0)} years of experience, "
            f"focused on building measurable impact with {', '.join(core_skills[:4]) if core_skills else 'relevant technical skills'}."
        ),
        "keywords": missing_keywords[:8],
        "skills_to_highlight": must_have_skills[:8],
        "action_verbs": missing_verbs[:5] if missing_verbs else ["built", "optimized", "designed", "shipped", "automated"],
        "technical_skills": core_skills[:10],
        "tool_skills": _top_skills(missing_keywords + must_have_skills, 8),
        "ats_keywords": _top_skills(missing_keywords + must_have_skills, 10),
        "experience_points": [_clean_text(item) for item in improved_bullets[:6]],
        "project_points": [
            f"{domain.title()} project with production-style README, metrics, and deployment",
            f"{company or domain.title()}-aligned case study highlighting business impact",
            "Portfolio refinement with clear problem statement, approach, and outcomes"
        ],
        "education_line": resume_data.get("education", "Not specified"),
        "targeted_edits": _build_targeted_edits(resume_bullets, missing_keywords[:5], missing_verbs[:3]),
        "ats_score_target": min(98, max(80, int(ats_score.get("total_score", 0) + 12)))
    }

    optimization_instructions = f"""
# Resume Optimization Instructions for {domain}

## Priority 1: Keyword Optimization
- Add these domain-specific keywords naturally throughout the resume: {', '.join(missing_keywords[:5])}
- Keywords should appear in Experience and Skills sections
- Integrate keywords in context, don't just list them

## Priority 2: Action Verbs
- Replace weak verbs with strong action verbs: {', '.join(missing_verbs[:3])}
- Every bullet point should start with an action verb
- Use past tense for completed projects, present for ongoing

## Priority 3: Quantification
- Add metrics to at least 60% of bullet points
- Use percentages, numbers, or time references
- Show impact: "reduced latency from X to Y" not just "optimized performance"

## Priority 4: Skills Section
- Ensure these skills are prominently listed: {', '.join(must_have_skills[:8])}
- Organize by proficiency level (Expert, Proficient, Learning)
- Match job descriptions emphasis

## Priority 5: Format & Structure
- Keep to 1 page if experience < 3 years, 2 pages if 3-7 years
- Use standard sections: Summary, Experience, Skills, Education, Projects
- Consistent formatting, proper spacing
- No tables or complex formatting (ATS-hostile)

## Company-Specific Optimization
- Target company is: {company or 'Not specified'}
- Research company values and incorporate alignment examples
- Highlight relevant domain experience

## Final Checklist
- Remove grammatical errors and typos
- Ensure consistent date formatting
- Remove personal pronouns (I, me, my)
- Check for ATS compatibility (no images, no fancy fonts)
"""
    
    return {
        "resume": {
            "raw_text": resume_data.get("raw_text", ""),
            "skills": resume_data.get("skills", []),
            "experience_years": resume_data.get("experience_years", 0),
            "education": resume_data.get("education", ""),
            "job_titles": resume_data.get("job_titles", []),
            "word_count": resume_data.get("word_count", 0)
        },
        "ats_analysis": {
            "current_score": ats_score.get("total_score", 0),
            "keyword_match_score": ats_score.get("breakdown", {}).get("keyword_match", 0),
            "format_score": ats_score.get("breakdown", {}).get("format", 0),
            "quantification_score": ats_score.get("breakdown", {}).get("quantification", 0),
            "action_verbs_score": ats_score.get("breakdown", {}).get("action_verbs", 0),
            "top_recommendations": ats_score.get("recommendations", {}).get("quick_wins", [])
        },
        "inject_keywords": missing_keywords,
        "add_skills": must_have_skills,
        "add_action_verbs": missing_verbs[:3],
        "target_domain": domain,
        "target_company": company,
        "optimized_resume_preview": {
            "headline": optimized_summary["headline"],
            "summary": optimized_summary["summary"],
            "keywords": optimized_summary["keywords"],
            "skills_to_highlight": optimized_summary["skills_to_highlight"],
            "action_verbs": optimized_summary["action_verbs"],
            "technical_skills": optimized_summary["technical_skills"],
            "tool_skills": optimized_summary["tool_skills"],
            "ats_keywords": optimized_summary["ats_keywords"],
            "sample_bullets": optimized_summary["experience_points"],
            "experience_points": optimized_summary["experience_points"],
            "project_points": optimized_summary["project_points"],
            "education_line": optimized_summary["education_line"],
            "targeted_edits": optimized_summary["targeted_edits"],
            "ats_score_target": optimized_summary["ats_score_target"],
            "raw_resume_lines": summary,
            "ats_template_markdown": _build_ats_resume_markdown(optimized_summary)
        },
        "optimization_instructions": optimization_instructions,
        "skill_gap_analysis": {
            "missing_must_have": skill_gap.get("must_have", {}).get("missing", []),
            "missing_good_to_have": skill_gap.get("good_to_have", {}).get("missing", [])[:3],
            "readiness_level": skill_gap.get("readiness_level", "Not assessed")
        }
    }


def create_hiepath_preload_data(payload: Dict[str, Any]) -> str:
    """
    Convert optimization payload to localStorage JSON string for resume-lm.
    
    Args:
        payload: Optimization payload
    
    Returns:
        JSON string for localStorage
    """
    preload_data = {
        "resume_content": payload.get("resume", {}),
        "optimization_hints": {
            "keywords_to_add": payload.get("inject_keywords", []),
            "skills_to_highlight": payload.get("add_skills", []),
            "verbs_to_use": payload.get("add_action_verbs", []),
            "domain": payload.get("target_domain", ""),
            "company": payload.get("target_company", "")
        },
        "ats_baseline": payload.get("ats_analysis", {})
    }
    
    return json.dumps(preload_data)


def generate_resume_editing_checklist(
    ats_score: Dict[str, Any],
    skill_gap: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate prioritized checklist for resume editing.
    
    Args:
        ats_score: ATS scoring result
        skill_gap: Skill gap analysis
    
    Returns:
        List of editing tasks with priorities
    """
    checklist = []
    
    # High priority: Low scoring areas
    breakdown = ats_score.get("breakdown", {})
    if breakdown.get("keyword_match", 100) < 60:
        checklist.append({
            "task": "Add domain-specific keywords",
            "priority": "HIGH",
            "keywords": ats_score.get("keyword_analysis", {}).get("missing", [])[:5],
            "time_estimate": "15 minutes",
            "impact": "40% of ATS score"
        })
    
    if breakdown.get("quantification", 100) < 50:
        checklist.append({
            "task": "Add metrics to bullet points",
            "priority": "HIGH",
            "example": "Reduced API latency by 40% (from 500ms to 300ms)",
            "time_estimate": "20 minutes",
            "impact": "20% of ATS score"
        })
    
    if breakdown.get("action_verbs", 100) < 50:
        checklist.append({
            "task": "Replace weak verbs with action verbs",
            "priority": "MEDIUM",
            "verbs_to_use": ["built", "designed", "optimized", "led", "automated"],
            "time_estimate": "10 minutes",
            "impact": "10% of ATS score"
        })
    
    # Add skill-based tasks
    missing_must = skill_gap.get("must_have", {}).get("missing", [])
    if missing_must:
        checklist.append({
            "task": "Highlight required skills",
            "priority": "HIGH",
            "skills": missing_must[:3],
            "time_estimate": "5 minutes",
            "impact": "Readiness improvement"
        })
    
    # Format issues
    if len(ats_score.get("missing_sections", [])) > 0:
        checklist.append({
            "task": "Add missing sections",
            "priority": "MEDIUM",
            "sections": ats_score.get("missing_sections", []),
            "time_estimate": "10 minutes",
            "impact": "20% of ATS score"
        })
    
    # Word count
    word_count = ats_score.get("word_count", 0)
    if word_count < 400 or word_count > 800:
        checklist.append({
            "task": "Adjust resume length",
            "priority": "LOW",
            "current": f"{word_count} words",
            "target": "400-700 words",
            "time_estimate": "15 minutes",
            "impact": "10% of ATS score"
        })
    
    return checklist


def estimate_ats_improvement(
    before_ats: Dict[str, Any],
    after_ats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Estimate ATS score improvement after optimization.
    
    Args:
        before_ats: ATS score before optimization
        after_ats: ATS score after optimization
    
    Returns:
        Improvement analysis
    """
    before_score = before_ats.get("total_score", 0)
    after_score = after_ats.get("total_score", 0)
    improvement = after_score - before_score
    improvement_percent = ((after_score - before_score) / before_score * 100) if before_score > 0 else 0
    
    return {
        "before": before_score,
        "after": after_score,
        "absolute_improvement": round(improvement, 1),
        "percentage_improvement": round(improvement_percent, 1),
        "breakdown_changes": {
            key: {
                "before": before_ats.get("breakdown", {}).get(key, 0),
                "after": after_ats.get("breakdown", {}).get(key, 0),
                "change": round(after_ats.get("breakdown", {}).get(key, 0) - before_ats.get("breakdown", {}).get(key, 0), 1)
            }
            for key in before_ats.get("breakdown", {}).keys()
        },
        "new_readiness_level": "Improved" if improvement > 5 else "Similar"
    }


def save_optimization_report(
    payload: Dict[str, Any],
    output_path: str
) -> bool:
    """
    Save optimization payload to JSON file for reference.
    
    Args:
        payload: Optimization payload
        output_path: File path to save to
    
    Returns:
        True if successful
    """
    try:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(payload, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving report: {str(e)}")
        return False


def generate_resume_lm_url_params(
    domain: str,
    company: str,
    gist_id: str = None
) -> str:
    """
    Generate URL parameters for resume-lm application.
    
    Args:
        domain: Target domain
        company: Target company
        gist_id: Optional GitHub Gist ID with pre-filled resume
    
    Returns:
        URL query string
    """
    params = [
        f"domain={domain}",
        f"company={company.replace(' ', '+')}"
    ]
    
    if gist_id:
        params.append(f"gist={gist_id}")
    
    return "&".join(params)


if __name__ == "__main__":
    print("Resume optimizer module loaded successfully")

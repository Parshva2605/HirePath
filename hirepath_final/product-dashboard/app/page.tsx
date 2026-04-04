"use client";

import { useEffect, useMemo, useRef, useState, type ChangeEvent } from 'react';
import { FaLinkedin, FaGithub } from 'react-icons/fa6';
import { buildLinkedInApplyLink, getSkillResourceBundle } from '../lib/resources';
import { getDomainProfile } from '../lib/domain-data';
import type { AnalysisResponse, JobMatch } from '../lib/types';

const API_BASE = process.env.NEXT_PUBLIC_HIREPATH_API ?? 'http://localhost:8000';

async function fetchWithTimeout(input: RequestInfo | URL, init?: RequestInit, timeoutMs = 15000) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(input, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

function scoreTone(score: number) {
  if (score >= 80) return 'good';
  if (score >= 60) return 'warn';
  return 'bad';
}

function scoreLabel(score: number) {
  if (score >= 80) return 'strong';
  if (score >= 60) return 'moderate';
  return 'low';
}

function clampScore(value: number) {
  return Math.max(0, Math.min(100, value));
}

function estimateOptimizedScore(result: AnalysisResponse) {
  const current = result.ats_score?.total_score ?? 0;
  const missingKeywords = result.resume_optimization?.inject_keywords?.length ?? 0;
  const missingSkills = result.resume_optimization?.skill_gap_analysis?.missing_must_have?.length ?? 0;
  const missingVerbs = result.resume_optimization?.add_action_verbs?.length ?? 0;
  const boost = Math.min(25, 8 + missingKeywords * 1.5 + missingSkills * 1.8 + missingVerbs * 1.2);
  return clampScore(current + boost);
}

function linkedinUrlForJob(job: JobMatch, domain?: string) {
  return buildLinkedInApplyLink(job.title, job.company, domain);
}

function asArray(value: unknown): string[] {
  if (Array.isArray(value)) return value.filter((item): item is string => typeof item === 'string');
  return [];
}

function asString(value: unknown): string {
  if (typeof value === 'string') return value;
  if (value == null) return '';
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function projectLabel(project: unknown) {
  if (typeof project === 'string') return project;
  if (project && typeof project === 'object') {
    const typed = project as { title?: string; stack?: string; impact?: string };
    return typed.title ?? typed.stack ?? typed.impact ?? 'Project idea';
  }
  return 'Project idea';
}

function repoCoreSkills(repo: { language?: string; topics?: string[]; description?: string }) {
  const fromTopics = (repo.topics ?? []).slice(0, 3);
  const fromLanguage = repo.language ? [repo.language] : [];
  const combined = Array.from(new Set([...fromLanguage, ...fromTopics]));
  if (combined.length) return combined.join(' • ');

  if (repo.description) {
    const words = repo.description
      .split(/[^a-zA-Z0-9+#.]+/)
      .map((word) => word.trim())
      .filter((word) => word.length > 2)
      .slice(0, 3);
    if (words.length) return words.join(' • ');
  }

  return 'Core skills not detected';
}

function normalizeSkillLabel(skill: string) {
  return skill.trim().replace(/\s+/g, ' ');
}

function formatStopwatch(totalSeconds: number) {
  const mins = Math.floor(totalSeconds / 60);
  const secs = totalSeconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function buildLearningSkills(skills: string[]) {
  const seen = new Set<string>();
  const cleaned: string[] = [];

  for (const raw of skills) {
    if (!raw) continue;
    const normalized = normalizeSkillLabel(raw);
    if (!normalized) continue;

    const key = normalized.toLowerCase();
    if (seen.has(key)) continue;

    seen.add(key);
    cleaned.push(normalized);
  }

  return cleaned;
}

type AtsResumeDraft = {
  title: string;
  targetRole: string;
  summary: string;
  technicalSkills: string[];
  toolSkills: string[];
  atsKeywords: string[];
  experienceBullets: string[];
  projectHighlights: string[];
  educationLine: string;
  onePageRules: string[];
};

type CandidateProfile = {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
};

type UploadAnimationStatus = 'idle' | 'loading' | 'success' | 'saved';

function dedupeLimit(values: string[], limit: number) {
  const seen = new Set<string>();
  const result: string[] = [];
  for (const value of values) {
    const cleaned = normalizeSkillLabel(value || '');
    if (!cleaned) continue;
    const key = cleaned.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(cleaned);
    if (result.length >= limit) break;
  }
  return result;
}

function buildAtsResumeDraft(
  result: AnalysisResponse,
  selectedDomain: string,
  selectedCompany: string,
  fallbackProjectIdeas: unknown[]
): AtsResumeDraft {
  const optimized = result.resume_optimization?.optimized_resume_preview;
  const title = optimized?.headline || `${selectedDomain.toUpperCase()} Engineer`;
  const targetRole = `${selectedDomain.toUpperCase()} Engineer - Target: ${selectedCompany}`;
  const summary = optimized?.summary || `Results-driven engineer targeting ${selectedCompany} ${selectedDomain} roles with ATS-aligned resume structure and quantified impact.`;

  const technicalSkills = dedupeLimit([
    ...(optimized?.technical_skills ?? []),
    ...(result.resume_optimization?.resume?.skills ?? []),
    ...(result.resume_optimization?.add_skills ?? []),
    ...(result.job_matches?.jobs?.flatMap((job) => job.matched_skills ?? []).slice(0, 12) ?? [])
  ], 10);

  const toolSkills = dedupeLimit([
    ...(optimized?.tool_skills ?? []),
    ...(result.resume_optimization?.inject_keywords ?? []),
    ...(result.github_profile?.top_languages?.map(([lang]) => lang) ?? []),
    ...(result.job_matches?.top_missing_skills?.map((item) => item.skill) ?? [])
  ], 8);

  const atsKeywords = dedupeLimit([
    ...(optimized?.ats_keywords ?? []),
    ...(result.resume_optimization?.inject_keywords ?? []),
    ...(result.skill_gap?.must_have?.missing ?? []),
    ...(result.skill_gap?.good_to_have?.missing ?? [])
  ], 10);

  const experienceBullets = dedupeLimit([
    ...(optimized?.experience_points ?? []),
    ...(optimized?.sample_bullets ?? []),
    ...(result.ats_score?.recommendations?.quick_wins ?? []).map((item) => `Improved resume quality by applying: ${item}`)
  ], 6);

  const projectHighlights = dedupeLimit(
    [
      ...(optimized?.project_points ?? []),
      ...fallbackProjectIdeas.map((idea) => projectLabel(idea))
    ],
    4
  );

  const educationLine = optimized?.education_line || result.resume_optimization?.resume?.education || 'Add degree and institute details';

  return {
    title,
    targetRole,
    summary,
    technicalSkills,
    toolSkills,
    atsKeywords,
    experienceBullets,
    projectHighlights,
    educationLine,
    onePageRules: [
      'Keep total length to one page with concise bullets',
      'Use strong action verbs and quantify outcomes in each experience section',
      'Include ATS keywords naturally in Summary, Skills, and Experience',
      'Use standard headings: Summary, Skills, Experience, Projects, Education',
      'Avoid tables, icons, images, and multi-column layouts'
    ]
  };
}

function escapeHtml(text: string) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildAtsResumeHtml(draft: AtsResumeDraft, profile: CandidateProfile) {
  const contact = [profile.email, profile.phone, profile.location, profile.linkedin].filter(Boolean).map(escapeHtml).join(' | ');
  const techSkills = draft.technicalSkills.map(escapeHtml).join(' | ');
  const toolSkills = draft.toolSkills.map(escapeHtml).join(' | ');
  const keywords = draft.atsKeywords.map(escapeHtml).join(' | ');
  const experience = draft.experienceBullets.map((bullet) => `<li>${escapeHtml(bullet)}</li>`).join('');
  const projects = draft.projectHighlights.map((project) => `<li>${escapeHtml(project)}</li>`).join('');

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>ATS Resume</title>
  <style>
    body { font-family: Arial, Helvetica, sans-serif; color: #111; margin: 0; padding: 0; background: #fff; }
    .page { width: 210mm; min-height: 297mm; margin: 0 auto; padding: 14mm; box-sizing: border-box; }
    h1 { margin: 0; font-size: 20px; letter-spacing: 0.2px; }
    .contact { margin-top: 4px; font-size: 11px; color: #333; }
    .target { margin-top: 8px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
    .section { margin-top: 10px; }
    .section h2 { margin: 0 0 4px; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid #111; padding-bottom: 2px; }
    p { margin: 0; font-size: 11px; line-height: 1.35; }
    ul { margin: 4px 0 0 16px; padding: 0; }
    li { margin: 0 0 3px; font-size: 11px; line-height: 1.3; }
    .row { margin-top: 2px; font-size: 11px; line-height: 1.3; }
    @page { size: A4; margin: 10mm; }
  </style>
</head>
<body>
  <div class="page">
    <h1>${escapeHtml(profile.fullName || 'Candidate Name')}</h1>
    <div class="contact">${contact || 'Add contact details'}</div>
    <div class="target">${escapeHtml(draft.targetRole)}</div>

    <div class="section">
      <h2>Professional Summary</h2>
      <p>${escapeHtml(draft.summary)}</p>
    </div>

    <div class="section">
      <h2>Technical Skills</h2>
      <div class="row"><strong>Core:</strong> ${techSkills}</div>
      <div class="row"><strong>Tools:</strong> ${toolSkills}</div>
    </div>

    <div class="section">
      <h2>Experience Highlights</h2>
      <ul>${experience}</ul>
    </div>

    <div class="section">
      <h2>Projects</h2>
      <ul>${projects}</ul>
    </div>

    <div class="section">
      <h2>ATS Keywords</h2>
      <p>${keywords}</p>
    </div>

    <div class="section">
      <h2>Education</h2>
      <p>${escapeHtml(draft.educationLine)}</p>
    </div>
  </div>
</body>
</html>`;
}

function downloadAtsResumePdf(draft: AtsResumeDraft, profile: CandidateProfile) {
  const previewWindow = window.open('', '_blank', 'noopener,noreferrer,width=1000,height=1200');
  if (!previewWindow) return;

  previewWindow.document.open();
  previewWindow.document.write(buildAtsResumeHtml(draft, profile));
  previewWindow.document.close();
  previewWindow.focus();
  setTimeout(() => {
    previewWindow.print();
  }, 350);
}

export default function Page() {
  const [resume, setResume] = useState<File | null>(null);
  const [domain, setDomain] = useState('frontend');
  const [company, setCompany] = useState('Google');
  const [githubUrl, setGithubUrl] = useState('');
  const [status, setStatus] = useState<string>('Checking backend status...');
  const [backendOnline, setBackendOnline] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [resumeUploadStatus, setResumeUploadStatus] = useState<UploadAnimationStatus>('idle');
  const [analysisSeconds, setAnalysisSeconds] = useState(0);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [linkedin, setLinkedin] = useState('');
  const resumeInputRef = useRef<HTMLInputElement | null>(null);
  const cursorFollowerRef = useRef<HTMLDivElement | null>(null);

  const domainProfile = useMemo(() => getDomainProfile(domain), [domain]);
  const atsScore = analysis?.ats_score?.total_score ?? 0;
  const optimizedScore = analysis ? estimateOptimizedScore(analysis) : 0;
  const readinessScore = analysis?.skill_gap?.readiness_score ?? 0;
  const githubQuality = analysis?.github_analysis?.quality_score ?? 0;
  const avgJobScore = analysis?.job_matches?.summary?.average_match_score ?? 0;
  const topJob = analysis?.job_matches?.jobs?.[0];
  const jobs = analysis?.job_matches?.jobs ?? [];
  const mustHaveMissing = analysis?.resume_optimization?.skill_gap_analysis?.missing_must_have ?? analysis?.skill_gap?.must_have?.missing ?? [];
  const goodToHaveMissing = analysis?.skill_gap?.good_to_have?.missing ?? analysis?.resume_optimization?.skill_gap_analysis?.missing_good_to_have ?? [];
  const injectKeywords = analysis?.resume_optimization?.inject_keywords ?? analysis?.ats_score?.keyword_analysis?.missing ?? [];
  const actionVerbs = analysis?.resume_optimization?.add_action_verbs ?? [];
  const projectIdeas = analysis?.github_analysis?.projects_to_build?.length ? analysis.github_analysis.projects_to_build : domainProfile.projectIdeas;
  const learningSkills = buildLearningSkills([
    ...mustHaveMissing,
    ...goodToHaveMissing,
    ...(analysis?.github_analysis?.skills_to_learn ?? [])
  ]).slice(0, 8);
  const githubRepos = analysis?.github_profile?.repos ?? [];
  const atsResumeDraft = analysis
    ? buildAtsResumeDraft(analysis, domain, company, projectIdeas)
    : null;
  const stopwatchValue = formatStopwatch(Math.max(0, analysisSeconds));
  const showStopwatch = loading || (!!analysis && analysisSeconds > 0);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/status`);
        if (!response.ok) throw new Error('Status check failed');
        const data = await response.json();
        setBackendOnline(true);
        setStatus(data.ollama_backend?.connected ? 'Backend online - Ollama connected' : 'Backend online - Ollama offline');
      } catch {
        setBackendOnline(false);
        setStatus('Backend unreachable');
      }
    };

    void fetchStatus();
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const prefersCoarse = window.matchMedia('(pointer: coarse)').matches;
    if (prefersCoarse) return;

    const follower = cursorFollowerRef.current;
    if (!follower) return;

    let x = window.innerWidth / 2;
    let y = window.innerHeight / 2;
    let targetX = x;
    let targetY = y;
    let raf = 0;

    const draw = () => {
      x += (targetX - x) * 0.2;
      y += (targetY - y) * 0.2;
      follower.style.transform = `translate3d(${x - 6}px, ${y - 6}px, 0)`;
      raf = window.requestAnimationFrame(draw);
    };

    const onMouseMove = (event: MouseEvent) => {
      targetX = event.clientX;
      targetY = event.clientY;
      follower.style.opacity = '1';
    };

    const onMouseLeave = () => {
      follower.style.opacity = '0';
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseenter', onMouseMove);
    window.addEventListener('mouseleave', onMouseLeave);
    raf = window.requestAnimationFrame(draw);

    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseenter', onMouseMove);
      window.removeEventListener('mouseleave', onMouseLeave);
      window.cancelAnimationFrame(raf);
    };
  }, []);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | undefined;

    if (loading) {
      setAnalysisSeconds(0);
      interval = setInterval(() => {
        setAnalysisSeconds((prev) => prev + 1);
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [loading]);

  useEffect(() => {
    if (!resume) {
      setResumeUploadStatus('idle');
      return;
    }

    setResumeUploadStatus('loading');

    const successTimer = setTimeout(() => setResumeUploadStatus('success'), 1200);
    const savedTimer = setTimeout(() => setResumeUploadStatus('saved'), 2000);
    const resetTimer = setTimeout(() => setResumeUploadStatus('idle'), 4200);

    return () => {
      clearTimeout(successTimer);
      clearTimeout(savedTimer);
      clearTimeout(resetTimer);
    };
  }, [resume]);

  function handleResumeChange(event: ChangeEvent<HTMLInputElement>) {
    setResume(event.target.files?.[0] ?? null);
  }

  async function runHirePath() {
    setError('');
    setLoading(true);
    setAnalysis(null);

    try {
      if (!resume) {
        throw new Error('Upload a resume file first.');
      }

      // Fail fast with a clear message when backend is unreachable.
      const statusResponse = await fetchWithTimeout(`${API_BASE}/api/status`, undefined, 8000);
      if (!statusResponse.ok) {
        throw new Error(`Backend is not ready at ${API_BASE}. Start FastAPI server and try again.`);
      }

      const formData = new FormData();
      formData.append('resume', resume);
      formData.append('domain', domain);
      formData.append('company', company);
      formData.append('github_url', githubUrl);

      const response = await fetchWithTimeout(`${API_BASE}/api/analyze`, {
        method: 'POST',
        body: formData
      }, 90000);

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload?.detail || 'Analysis failed');
      }

      setAnalysis(payload);
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : 'Unknown error';
      if (message.includes('Failed to fetch') || message.includes('NetworkError') || message.includes('aborted')) {
        setError(`Cannot connect to backend at ${API_BASE}. Ensure backend is running on port 8000 and refresh once.`);
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  }

  const predictedBadge = scoreTone(optimizedScore);
  const atsBadge = scoreTone(atsScore);
  const readinessBadge = scoreTone(readinessScore);
  const githubBadge = scoreTone(githubQuality);
  const jobBadge = scoreTone(avgJobScore);

  return (
    <main className="app-shell">
      <div ref={cursorFollowerRef} className="cursor-follower-dot" aria-hidden="true" />
      <section className="hero">
        <div className="hero-panel">
          <div className="kicker">HirePath product dashboard</div>
          <h1>One dashboard for resume, GitHub, skills, and jobs.</h1>
          <p>
            Upload your resume, add your GitHub URL, target company, and domain. HirePath scans ATS fit first,
            then rewrites the resume strategy, exposes skill gaps, scores GitHub quality, recommends courses and projects,
            and ranks the jobs you can realistically apply for.
          </p>

          <div className="hero-stats">
            <div className="stat">
              <div className="stat-label">Backend</div>
              <div className="stat-value">{backendOnline ? 'LIVE' : 'OFFLINE'}</div>
              <div className="stat-note">{status}</div>
            </div>
            <div className="stat">
              <div className="stat-label">Target domain</div>
              <div className="stat-value">{domainProfile.label}</div>
              <div className="stat-note">{domainProfile.summary}</div>
            </div>
            <div className="stat">
              <div className="stat-label">ATS target</div>
              <div className="stat-value">{analysis ? `${Math.round(optimizedScore)}%` : '80%+'}</div>
              <div className="stat-note">Projected after optimization</div>
            </div>
            <div className="stat">
              <div className="stat-label">Job match path</div>
              <div className="stat-value">{analysis?.job_matches?.total ?? 0}</div>
              <div className="stat-note">Shortlisted roles from local database</div>
            </div>
          </div>
        </div>

        <aside className="side-panel">
          <div className="panel workflow-panel">
            <div className="section-title">
              <h3>Workflow</h3>
              <span>single pass analysis</span>
            </div>
            <div className="stack">
              <div className="mini-pill">1. ATS first</div>
              <div className="mini-pill">2. Optimize resume</div>
              <div className="mini-pill">3. Reveal skill gaps</div>
              <div className="mini-pill">4. Review GitHub quality</div>
              <div className="mini-pill">5. Rank jobs and apply links</div>
            </div>
            <div className="workflow-live-area">
              {showStopwatch ? (
                <div className="workflow-stopwatch" aria-live="polite">
                  <span className="workflow-prefix">Analysis timer</span>
                  <div className="workflow-speedline">
                    <span className="workflow-number workflow-timer">{stopwatchValue}</span>
                  </div>
                </div>
              ) : (
                <div className="workflow-emphasis" aria-label="All things in just 90 sec">
                  <span className="workflow-prefix">All things in just</span>
                  <div className="workflow-speedline">
                    <span className="workflow-number">90</span>
                    <span className="workflow-unit">sec</span>
                  </div>
                </div>
              )}
              <div className="workflow-powered">Powered by Team Shield</div>
            </div>
          </div>
          <div className="panel source-data-panel">
            <div className="section-title">
              <h3>Source data</h3>
              <span>courses + projects</span>
            </div>
            <p>
              Course recommendations are curated from trusted learning sources and matched to your missing skills.
              Project suggestions are generated from domain requirements and your analysis results.
            </p>
            <div className="source-platform-row">
              <p className="source-help-line"><strong>With the help of trusted platforms</strong></p>
              <div className="source-button-group" aria-label="Source platforms">
                <button className="source-icon-button" type="button" aria-label="Team Shield logo">
                  <img className="source-icon source-logo-image" src="/logo-64.png" alt="Team Shield" />
                </button>
                <button className="source-icon-button" type="button" aria-label="Continue with LinkedIn">
                  <FaLinkedin className="source-icon source-icon-theme" />
                </button>
                <button className="source-icon-button" type="button" aria-label="Continue with GitHub">
                  <FaGithub className="source-icon source-icon-theme" />
                </button>
              </div>
            </div>
          </div>
        </aside>
      </section>

      <section className="panel">
        <div className="section-title">
          <h2>Input</h2>
          <span>upload resume, then analyze once</span>
        </div>
        <div className="form-grid">
          <div className="field">
            <label htmlFor="resume">Resume</label>
            <div className="resume-picker" aria-live="polite">
              <input
                ref={resumeInputRef}
                id="resume"
                className="resume-hidden-input"
                type="file"
                accept=".pdf,.docx"
                onChange={handleResumeChange}
              />
              <button
                type="button"
                className="resume-picker-button"
                onClick={() => resumeInputRef.current?.click()}
              >
                Choose File
              </button>
              <div className={`resume-picker-name ${resumeUploadStatus}`} title={resume?.name ?? 'No file chosen'}>
                {resumeUploadStatus === 'loading' ? (
                  <>
                    <span className="resume-upload-spinner" aria-hidden="true" />
                    <span>Saving...</span>
                  </>
                ) : resumeUploadStatus === 'success' || resumeUploadStatus === 'saved' ? (
                  <>
                    <span className="resume-upload-check" aria-hidden="true">✓</span>
                    <span>Saved</span>
                  </>
                ) : (
                  <span>{resume?.name ?? 'No file chosen'}</span>
                )}
              </div>
            </div>
          </div>
          <div className="field">
            <label htmlFor="github">GitHub URL</label>
            <input
              id="github"
              value={githubUrl}
              onChange={(event) => setGithubUrl(event.target.value)}
              placeholder="https://github.com/username"
            />
          </div>
          <div className="field">
            <label htmlFor="company">Target company</label>
            <input id="company" value={company} onChange={(event) => setCompany(event.target.value)} placeholder="Google" />
          </div>
          <div className="field">
            <label htmlFor="domain">Domain</label>
            <select id="domain" value={domain} onChange={(event) => setDomain(event.target.value)}>
              <option value="frontend">Frontend</option>
              <option value="backend">Backend</option>
              <option value="fullstack">Full stack</option>
              <option value="aiml">AI / ML</option>
              <option value="devops">DevOps</option>
            </select>
          </div>
          <div className="field" style={{ alignSelf: 'end' }}>
            <button className="primary-button run-hirepath-button" type="button" onClick={runHirePath} disabled={loading}>
              {loading ? 'Analyzing...' : 'Run HirePath'}
            </button>
          </div>
        </div>

        {error ? <div className="error-box">{error}</div> : null}
        {!analysis && !loading ? <div className="empty-state">Upload a resume and click Run HirePath to generate the dashboard.</div> : null}
      </section>

      {loading ? <div className="loading">Processing ATS score, resume optimization, skill gaps, GitHub quality, and job matches...</div> : null}

      {analysis ? (
        <div className="section-stack">
          <section className="dashboard-grid">
            <div className="panel">
              <div className="section-title">
                <h2>Analytics</h2>
                <span>scoreboard</span>
              </div>
              <div className="kpi-grid">
                <div className="metric-card">
                  <div className="metric-label">ATS score</div>
                  <div className="metric-value">{Math.round(atsScore)}%</div>
                  <div className="progress"><div style={{ width: `${atsScore}%` }} /></div>
                  <div className="metric-subtext">Current resume fit: <span className={`badge ${atsBadge}`}>{scoreLabel(atsScore)}</span></div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Optimized score</div>
                  <div className="metric-value">{Math.round(optimizedScore)}%</div>
                  <div className="progress"><div style={{ width: `${optimizedScore}%` }} /></div>
                  <div className="metric-subtext">Projected after rewrite: <span className={`badge ${predictedBadge}`}>{scoreLabel(optimizedScore)}</span></div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Skill readiness</div>
                  <div className="metric-value">{Math.round(readinessScore)}%</div>
                  <div className="progress"><div style={{ width: `${readinessScore}%` }} /></div>
                  <div className="metric-subtext">{analysis.skill_gap?.readiness_level ?? 'Unknown'}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">GitHub quality</div>
                  <div className="metric-value">{Math.round(githubQuality)}%</div>
                  <div className="progress"><div style={{ width: `${githubQuality}%` }} /></div>
                  <div className="metric-subtext">Repo quality signal: <span className={`badge ${githubBadge}`}>{scoreLabel(githubQuality)}</span></div>
                </div>
              </div>
            </div>

            <div className="panel">
              <div className="section-title">
                <h2>Job market</h2>
                <span>{analysis.job_matches?.total ?? 0} roles</span>
              </div>
              <div className="stack">
                <div className="metric-card">
                  <div className="metric-label">Average match</div>
                  <div className="metric-value">{Math.round(avgJobScore)}%</div>
                  <div className="progress"><div style={{ width: `${avgJobScore}%` }} /></div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Top role</div>
                  <div className="metric-value" style={{ fontSize: '18px' }}>{topJob?.title ?? 'No match yet'}</div>
                  <div className="metric-subtext">{topJob ? `${topJob.company} • ${topJob.location ?? 'Remote'}` : 'Add stronger skills to unlock roles'}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Job match signal</div>
                  <div className="metric-subtext">
                    <span className={`badge ${jobBadge}`}>{scoreLabel(avgJobScore)}</span> {analysis.job_matches?.summary?.jobs_over_70 ?? 0} jobs above 70%
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="grid-2">
            <div className="panel">
              <div className="section-title">
                <h2>Resume optimization</h2>
                <span>ATS-friendly rewrite path</span>
              </div>
              <p>
                HirePath first checks ATS fit. If the score is low, use the checklist below to make the resume more ATS-friendly,
                then re-run the same dashboard for a better projected score.
              </p>
              <div className="pill-row" style={{ marginBottom: 16 }}>
                {injectKeywords.slice(0, 6).map((keyword) => (
                  <span className="pill" key={keyword}>{keyword}</span>
                ))}
              </div>
              <div className="grid-2">
                <div className="info-card">
                  <h4>Keywords to inject</h4>
                  <p>{injectKeywords.length ? injectKeywords.slice(0, 8).join(', ') : 'No missing keyword data returned.'}</p>
                </div>
                <div className="info-card">
                  <h4>Action verbs</h4>
                  <p>{actionVerbs.length ? actionVerbs.slice(0, 6).join(', ') : 'No action-verbs list returned.'}</p>
                </div>
                <div className="info-card">
                  <h4>Optimized resume preview</h4>
                  <p>{analysis.resume_optimization?.optimized_resume_preview?.headline ?? 'No optimized headline returned.'}</p>
                  <p>{analysis.resume_optimization?.optimized_resume_preview?.summary ?? 'No optimized summary returned.'}</p>
                  <p><strong>Sample bullets:</strong> {analysis.resume_optimization?.optimized_resume_preview?.sample_bullets?.slice(0, 2).join(' | ') ?? 'No sample bullets returned.'}</p>
                </div>
              </div>
              <div className="section-stack">
                <div className="info-card">
                  <h4>Optimization instructions</h4>
                  <pre className="code-block">{analysis.resume_optimization?.optimization_instructions ?? 'No optimization instructions returned.'}</pre>
                </div>
                <div className="info-card">
                  <h4>Checklist</h4>
                  <ul className="checklist">
                    <li>Move required keywords into Experience and Skills sections naturally.</li>
                    <li>Replace weak verbs with strong action verbs and add metrics.</li>
                    <li>Keep the layout simple: no tables, no images, no fancy formatting.</li>
                    <li>Prioritize missing must-have skills before submitting applications.</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="panel">
              <div className="section-title">
                <h2>Skill gaps</h2>
                <span>courses + focus</span>
              </div>
              <div className="stack">
                <div className="info-card">
                  <h4>Must-have gaps</h4>
                  <div className="tag-row">
                    {mustHaveMissing.length ? mustHaveMissing.slice(0, 8).map((skill) => {
                      const bundle = getSkillResourceBundle(skill);
                      const course = bundle.exact;
                      return (
                        <span className="tag" key={skill}>
                          <span>{skill}</span>
                          {course ? <strong>{course.title}</strong> : null}
                          <a href={bundle.youtube?.url} target="_blank" rel="noreferrer">YouTube</a>
                          <a href={bundle.web?.url} target="_blank" rel="noreferrer">Web</a>
                        </span>
                      );
                    }) : <span className="mini-pill">No must-have gaps returned.</span>}
                  </div>
                </div>
                <div className="info-card">
                  <h4>Good-to-have gaps</h4>
                  <div className="tag-row">
                    {goodToHaveMissing.length ? goodToHaveMissing.slice(0, 8).map((skill) => {
                      const bundle = getSkillResourceBundle(skill);
                      const course = bundle.exact;
                      return (
                        <span className="tag" key={skill}>
                          <span>{skill}</span>
                          {course ? <strong>{course.title}</strong> : null}
                          <a href={bundle.youtube?.url} target="_blank" rel="noreferrer">YouTube</a>
                          <a href={bundle.web?.url} target="_blank" rel="noreferrer">Web</a>
                        </span>
                      );
                    }) : <span className="mini-pill">No good-to-have gaps returned.</span>}
                  </div>
                </div>
                <div className="info-card">
                  <h4>Skills to focus on next</h4>
                  <div className="pill-row">
                    {learningSkills.length ? learningSkills.map((skill) => (
                      <span className="pill" key={skill}>{skill}</span>
                    )) : <span className="mini-pill">No focus skills returned.</span>}
                  </div>
                </div>
                <div className="info-card">
                  <h4>Domain courses</h4>
                  <div className="columns-2">
                    {learningSkills.map((skill) => {
                      const bundle = getSkillResourceBundle(skill);
                      return (
                        <div className="list-card" key={`${skill}-${bundle.exact?.title ?? 'search'}`}>
                          <h4>{skill}</h4>
                          {bundle.exact ? (
                            <>
                              <p>{bundle.exact.title}</p>
                              <p>{bundle.exact.platform}</p>
                              <p><a href={bundle.exact.url} target="_blank" rel="noreferrer">Open course</a></p>
                            </>
                          ) : null}
                          <p><a href={bundle.youtube?.url} target="_blank" rel="noreferrer">YouTube search</a></p>
                          <p><a href={bundle.web?.url} target="_blank" rel="noreferrer">Free web search</a></p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </section>



          <section className="panel">
            <div className="section-title">
              <h2>GitHub, Roadmap, Interview</h2>
              <span>horizontal insight cards</span>
            </div>

            <div className="grid-3">
              <article className="job-card">
                <div className="section-title" style={{ marginBottom: 8 }}>
                  <h3>GitHub quality</h3>
                  <span>{Math.round(githubQuality)}%</span>
                </div>
                <p>{githubRepos.length} repositories analyzed</p>
                <div className="progress" style={{ margin: '12px 0 10px' }}>
                  <div style={{ width: `${githubQuality}%` }} />
                </div>
                <p><strong>Strongest:</strong> {(analysis.github_analysis?.strongest_projects ?? []).slice(0, 3).join(', ') || 'No project strengths returned.'}</p>
                <p><strong>Build next:</strong> {projectIdeas.slice(0, 3).map((idea) => projectLabel(idea)).join(' • ')}</p>
              </article>

              <article className="job-card">
                <div className="section-title" style={{ marginBottom: 8 }}>
                  <h3>Career roadmap</h3>
                  <span>90 days</span>
                </div>
                {analysis.career_roadmap && typeof analysis.career_roadmap === 'object' ? (
                  <>
                    <p>{analysis.career_roadmap.title ?? 'Career roadmap'}</p>
                    <p>{analysis.career_roadmap.summary ?? ''}</p>
                    <p>{analysis.career_roadmap.current_context ? `GitHub: ${analysis.career_roadmap.current_context.github_quality ?? 0}% • Experience: ${analysis.career_roadmap.current_context.experience_years ?? 0} years` : ''}</p>
                    <ul className="checklist" style={{ marginTop: 10 }}>
                      {(analysis.career_roadmap.phases ?? []).slice(0, 3).map((phase) => (
                        <li key={phase.name ?? phase.goal ?? 'phase'}>{phase.name ?? 'Phase'}: {phase.goal ?? 'Focus'}</li>
                      ))}
                    </ul>
                  </>
                ) : (
                  <p>{asString(analysis.career_roadmap ?? 'No roadmap returned yet.')}</p>
                )}
              </article>

              <article className="job-card">
                <div className="section-title" style={{ marginBottom: 8 }}>
                  <h3>Interview prep</h3>
                  <span>focus areas</span>
                </div>
                {analysis.interview_preparation && typeof analysis.interview_preparation === 'object' ? (
                  <>
                    <p>{analysis.interview_preparation.title ?? 'Interview prep'}</p>
                    <p><strong>Technical:</strong> {(analysis.interview_preparation.technical_topics ?? []).slice(0, 2).join(' • ') || 'N/A'}</p>
                    <p><strong>System design:</strong> {(analysis.interview_preparation.system_design ?? []).slice(0, 2).join(' • ') || 'N/A'}</p>
                    <p><strong>Behavioral:</strong> {(analysis.interview_preparation.behavioral ?? []).slice(0, 2).join(' • ') || 'N/A'}</p>
                  </>
                ) : (
                  <p>{asString(analysis.interview_preparation ?? 'No interview prep returned yet.')}</p>
                )}
              </article>
            </div>

            <div className="grid-3" style={{ marginTop: 14 }}>
              <article className="job-card" style={{ gridColumn: '1 / -1' }}>
                <div className="section-title" style={{ marginBottom: 8 }}>
                  <h3>Learning path</h3>
                  <span>phases</span>
                </div>
                {analysis.learning_path && typeof analysis.learning_path === 'object' && 'phases' in analysis.learning_path ? (
                  <div className="grid-3">
                    {(analysis.learning_path as { phases?: Array<{ name?: string; focus?: string; skills?: Array<{ skill?: string }> }> }).phases?.map((phase) => (
                      <div className="list-card" key={phase.name ?? phase.focus ?? 'learning-phase'}>
                        <h4>{phase.name ?? 'Phase'}</h4>
                        <p>{phase.focus ?? ''}</p>
                        <div className="tag-row">
                          {(phase.skills ?? []).map((skill) => (
                            <span className="mini-pill" key={skill.skill ?? 'skill'}>{skill.skill ?? 'Skill'}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>{asString(analysis.learning_path ?? 'No learning path returned yet.')}</p>
                )}
              </article>

              <article className="job-card" style={{ gridColumn: '1 / -1' }}>
                <div className="section-title" style={{ marginBottom: 8 }}>
                  <h3>All repositories with core skills</h3>
                  <span>{githubRepos.length} repos</span>
                </div>
                {githubRepos.length ? (
                  <div className="grid-3">
                    {githubRepos.map((repo) => (
                      <div className="list-card" key={`${repo.name}-${repo.url}`}>
                        <h4>{repo.name ?? 'Repository'}</h4>
                        <p><strong>Core skills:</strong> {repoCoreSkills(repo)}</p>
                        {repo.description ? <p>{repo.description}</p> : null}
                        <p>
                          {repo.stars != null ? <span><strong>Stars:</strong> {repo.stars}</span> : null}
                          {repo.url ? <span> • <a href={repo.url} target="_blank" rel="noreferrer">Open repo</a></span> : null}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <span className="mini-pill">No repository details returned. Check the GitHub URL and rerun analysis.</span>
                )}
              </article>
            </div>
          </section>

          <section className="panel">
            <div className="section-title">
              <h2>Job matches</h2>
              <span>LinkedIn apply links</span>
            </div>
            <div className="grid-3">
              {jobs.length ? jobs.map((job) => (
                <article className="job-card" key={`${job.company}-${job.title}`}>
                  <div className="section-title" style={{ marginBottom: 8 }}>
                    <h3>{job.title}</h3>
                    <span>{Math.round(job.match_score)}%</span>
                  </div>
                  <p>{job.company} • {job.location ?? 'Remote'}</p>
                  <div className="progress" style={{ margin: '12px 0 10px' }}>
                    <div style={{ width: `${job.match_score}%` }} />
                  </div>
                  <p><strong>Matched:</strong> {job.matched_skills.slice(0, 5).join(', ') || 'None'}</p>
                  <p><strong>Missing:</strong> {job.missing_skills.slice(0, 5).join(', ') || 'None'}</p>
                  <div className="toolbar" style={{ marginTop: 12 }}>
                    <a className="primary-button" href={linkedinUrlForJob(job, domain)} target="_blank" rel="noreferrer">Apply on LinkedIn</a>
                    {job.url ? <a className="secondary-button" href={job.url} target="_blank" rel="noreferrer">Original listing</a> : null}
                  </div>
                </article>
              )) : <div className="empty-state">No job matches returned yet.</div>}
            </div>
          </section>

          <section className="grid-2">
            <div className="panel">
              <div className="section-title">
                <h2>Company and domain focus</h2>
                <span>{company}</span>
              </div>
              <div className="stack">
                <div className="info-card">
                  <h4>What to focus on now</h4>
                  <div className="pill-row">
                    {domainProfile.focusSkills.map((skill) => (
                      <span className="pill" key={skill}>{skill}</span>
                    ))}
                  </div>
                </div>
                <div className="info-card">
                  <h4>Projects employers expect</h4>
                  <div className="tag-row">
                    {domainProfile.projectIdeas.map((idea) => (
                      <span className="tag" key={idea}>{idea}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div className="panel">
              <div className="section-title">
                <h2>Short summary</h2>
                <span>resume + github + jobs</span>
              </div>
              <div className="stack">
                <div className="info-card">
                  <h4>Top line</h4>
                  <p>
                    {analysis.job_matches?.summary?.jobs_over_70 ?? 0} jobs are above 70%, {analysis.job_matches?.summary?.jobs_over_50 ?? 0} above 50%, and the projected ATS path is {Math.round(optimizedScore)}%.
                  </p>
                </div>
                <div className="info-card">
                  <h4>Apply strategy</h4>
                  <ul className="checklist">
                    <li>Use the optimized resume checklist before applying.</li>
                    <li>Prioritize jobs with the highest match score and lowest missing skills.</li>
                    <li>Open the course links for the top missing skills first.</li>
                    <li>Build one project from the domain roadmap before the next application batch.</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>
        </div>
      ) : null}
    </main>
  );
}

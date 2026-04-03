"use client";

import { useEffect, useMemo, useState } from 'react';
import { buildLinkedInApplyLink, getSkillResourceBundle } from '../lib/resources';
import { getDomainProfile } from '../lib/domain-data';
import type { AnalysisResponse, JobMatch } from '../lib/types';

const API_BASE = process.env.NEXT_PUBLIC_HIREPATH_API ?? 'http://localhost:8000';

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
  const learningSkills = Array.from(
    new Set([
      ...mustHaveMissing,
      ...goodToHaveMissing,
      ...(analysis?.github_analysis?.skills_to_learn ?? [])
    ])
  ).slice(0, 8);
  const githubRepos = analysis?.github_profile?.repos ?? [];

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

  async function runHirePath() {
    setError('');
    setLoading(true);
    setAnalysis(null);

    try {
      if (!resume) {
        throw new Error('Upload a resume file first.');
      }

      const formData = new FormData();
      formData.append('resume', resume);
      formData.append('domain', domain);
      formData.append('company', company);
      formData.append('github_url', githubUrl);

      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        body: formData
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload?.detail || 'Analysis failed');
      }

      setAnalysis(payload);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unknown error');
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
          <div className="panel">
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
          </div>
          <div className="panel">
            <div className="section-title">
              <h3>Source data</h3>
              <span>courses + projects</span>
            </div>
            <p>
              Course links are sourced from the local skill library derived from <strong>200_skills_finder.html</strong>.
              Project suggestions come from the domain skill databases and backend analysis output.
            </p>
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
            <input id="resume" type="file" accept=".pdf,.docx" onChange={(event) => setResume(event.target.files?.[0] ?? null)} />
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
            <button className="primary-button" type="button" onClick={runHirePath} disabled={loading}>
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

          <section className="grid-2">
            <div className="panel">
              <div className="section-title">
                <h2>GitHub quality</h2>
                <span>{githubRepos.length} repositories</span>
              </div>
              <p>
                The backend scores GitHub quality and identifies the projects you should build next. That gives you a portfolio map,
                not just a repo count.
              </p>
              <div className="grid-2" style={{ marginTop: 14 }}>
                <div className="info-card">
                  <h4>Strongest projects</h4>
                  <div className="tag-row">
                    {analysis.github_analysis?.strongest_projects?.length ? analysis.github_analysis.strongest_projects.map((item) => (
                      <span className="tag" key={item}>{item}</span>
                    )) : <span className="mini-pill">No project strengths returned.</span>}
                  </div>
                </div>
                <div className="info-card">
                  <h4>What to build next</h4>
                  <div className="tag-row">
                    {projectIdeas.map((idea) => (
                      <span className="tag" key={projectLabel(idea)}>{projectLabel(idea)}</span>
                    ))}
                  </div>
                </div>
                <div className="info-card" style={{ gridColumn: '1 / -1' }}>
                  <h4>All repositories with core skills</h4>
                  {githubRepos.length ? (
                    <div className="columns-2">
                      {githubRepos.map((repo) => (
                        <div className="list-card" key={`${repo.name}-${repo.url}`}>
                          <h4>{repo.name ?? 'Repository'}</h4>
                          <p><strong>Core skills:</strong> {repoCoreSkills(repo)}</p>
                          <p>{repo.description || 'No description available.'}</p>
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
                </div>
              </div>
            </div>

            <div className="panel">
              <div className="section-title">
                <h2>Roadmap and interview prep</h2>
                <span>next 90 days</span>
              </div>
              <div className="stack">
                <div className="info-card">
                  <h4>Career roadmap</h4>
                  {analysis.career_roadmap && typeof analysis.career_roadmap === 'object' ? (
                    <div className="stack">
                      <p>{analysis.career_roadmap.title ?? 'Career roadmap'}</p>
                      <p>{analysis.career_roadmap.summary ?? ''}</p>
                      <p>{analysis.career_roadmap.current_context ? `GitHub quality: ${analysis.career_roadmap.current_context.github_quality ?? 0}% • Experience: ${analysis.career_roadmap.current_context.experience_years ?? 0} years` : ''}</p>
                      <div className="columns-2">
                        {analysis.career_roadmap.phases?.map((phase) => (
                          <div className="list-card" key={phase.name ?? phase.goal ?? 'phase'}>
                            <h4>{phase.name ?? 'Phase'}</h4>
                            <p>{phase.goal ?? ''}</p>
                            <ul className="checklist">
                              {(phase.actions ?? []).map((action) => <li key={action}>{action}</li>)}
                            </ul>
                          </div>
                        ))}
                      </div>
                      <p><strong>Weekly commitment:</strong> {analysis.career_roadmap.weekly_commitment_hours ?? 0} hours</p>
                      <p><strong>Success metrics:</strong> {(analysis.career_roadmap.success_metrics ?? []).join(' • ')}</p>
                    </div>
                  ) : (
                    <p>{asString(analysis.career_roadmap ?? 'No roadmap returned yet.')}</p>
                  )}
                </div>
                <div className="info-card">
                  <h4>Interview prep</h4>
                  {analysis.interview_preparation && typeof analysis.interview_preparation === 'object' ? (
                    <div className="stack">
                      <p>{analysis.interview_preparation.title ?? 'Interview prep'}</p>
                      <div className="grid-2">
                        <div className="list-card">
                          <h4>Technical topics</h4>
                          <ul className="checklist">
                            {(analysis.interview_preparation.technical_topics ?? []).map((item) => <li key={item}>{item}</li>)}
                          </ul>
                        </div>
                        <div className="list-card">
                          <h4>System design</h4>
                          <ul className="checklist">
                            {(analysis.interview_preparation.system_design ?? []).map((item) => <li key={item}>{item}</li>)}
                          </ul>
                        </div>
                        <div className="list-card">
                          <h4>Behavioral</h4>
                          <ul className="checklist">
                            {(analysis.interview_preparation.behavioral ?? []).map((item) => <li key={item}>{item}</li>)}
                          </ul>
                        </div>
                        <div className="list-card">
                          <h4>Final week</h4>
                          <ul className="checklist">
                            {(analysis.interview_preparation.final_week ?? []).map((item) => <li key={item}>{item}</li>)}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <p>{asString(analysis.interview_preparation ?? 'No interview prep returned yet.')}</p>
                  )}
                </div>
                <div className="info-card">
                  <h4>Learning path</h4>
                  {analysis.learning_path && typeof analysis.learning_path === 'object' && 'phases' in analysis.learning_path ? (
                    <div className="columns-2">
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
                </div>
              </div>
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

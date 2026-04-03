export type DomainKey = 'aiml' | 'devops' | 'frontend' | 'backend' | 'fullstack';

export type CourseResource = {
  skill: string;
  title: string;
  platform: string;
  url: string;
  tags?: string[];
};

export type SkillResourceBundle = {
  exact?: CourseResource;
  youtube?: CourseResource;
  web?: CourseResource;
};

export type DomainProfile = {
  label: string;
  summary: string;
  projectIdeas: string[];
  focusSkills: string[];
  interviewTopics: string[];
};

export type JobMatch = {
  title: string;
  company: string;
  domain: string;
  location?: string;
  url?: string;
  match_score: number;
  skill_overlap: number;
  domain_match: number;
  matched_skills: string[];
  missing_skills: string[];
};

export type AnalysisResponse = {
  success?: boolean;
  profile?: {
    domain?: string;
    company?: string;
    github_url?: string;
    resume_filename?: string;
  };
  ats_score?: {
    total_score?: number;
    breakdown?: {
      keyword_match?: number;
      format?: number;
      quantification?: number;
      length?: number;
      action_verbs?: number;
    };
    keyword_analysis?: {
      missing?: string[];
    };
    recommendations?: {
      quick_wins?: string[];
    };
    missing_sections?: string[];
    word_count?: number;
  };
  skill_gap?: {
    readiness_score?: number;
    readiness_level?: string;
    must_have?: {
      coverage?: number;
      missing?: string[];
      have?: string[];
    };
    good_to_have?: {
      coverage?: number;
      missing?: string[];
      have?: string[];
    };
    advanced?: {
      coverage?: number;
      missing?: string[];
      have?: string[];
    };
  };
  github_profile?: {
    username?: string;
    profile_url?: string;
    followers?: number;
    public_repos?: number;
    top_languages?: Array<[string, number]>;
    repos?: Array<{
      name?: string;
      url?: string;
      language?: string;
      topics?: string[];
      stars?: number;
      description?: string;
    }>;
  } | null;
  github_analysis?: {
    quality_score?: number;
    strongest_projects?: string[];
    projects_to_build?: Array<{ title?: string; stack?: string; impact?: string } | string>;
    skills_to_learn?: string[];
    weak_spots?: string[];
    recommendations?: string;
  } | null;
  career_roadmap?: {
    title?: string;
    summary?: string;
    current_context?: {
      experience_years?: number;
      github_quality?: number;
      critical_gaps?: string[];
    };
    phases?: Array<{
      name?: string;
      goal?: string;
      actions?: string[];
    }>;
    weekly_commitment_hours?: number;
    success_metrics?: string[];
  } | string | null;
  learning_path?: unknown;
  resume_optimization?: {
    resume?: {
      raw_text?: string;
      skills?: string[];
      experience_years?: number;
      education?: string;
      job_titles?: string[];
      word_count?: number;
    };
    optimized_resume_preview?: {
      headline?: string;
      summary?: string;
      keywords?: string[];
      skills_to_highlight?: string[];
      action_verbs?: string[];
      sample_bullets?: string[];
      raw_resume_lines?: string[];
    };
    ats_analysis?: {
      current_score?: number;
      keyword_match_score?: number;
      format_score?: number;
      quantification_score?: number;
      action_verbs_score?: number;
      top_recommendations?: string[];
    };
    inject_keywords?: string[];
    add_skills?: string[];
    add_action_verbs?: string[];
    optimization_instructions?: string;
    skill_gap_analysis?: {
      missing_must_have?: string[];
      missing_good_to_have?: string[];
      readiness_level?: string;
    };
  };
  job_matches?: {
    total?: number;
    jobs?: JobMatch[];
    summary?: {
      total_jobs?: number;
      average_match_score?: number;
      best_match?: number;
      jobs_over_70?: number;
      jobs_over_50?: number;
      jobs_over_30?: number;
    };
    top_missing_skills?: Array<{ skill: string; frequency: number; appears_in: string }>;
    reachable_with_learning?: Array<{
      job: string;
      company: string;
      current_score: number;
      current_missing_skills: number;
      new_missing_skills: number;
      improvement_percent: number;
      url?: string;
    }>;
  };
  interview_preparation?: {
    title?: string;
    technical_topics?: string[];
    system_design?: string[];
    behavioral?: string[];
    company_research?: string[];
    mock_plan?: string[];
    final_week?: string[];
  } | string | null;
  next_steps?: Record<string, string>;
  ollama_status?: {
    connected?: boolean;
    required_for_ai_features?: boolean;
  };
};

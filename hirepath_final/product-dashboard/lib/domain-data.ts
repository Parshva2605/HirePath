import type { DomainKey, DomainProfile } from './types';

export const DOMAIN_PROFILES: Record<DomainKey, DomainProfile> = {
  frontend: {
    label: 'Frontend',
    summary: 'React and Next.js product engineering with strong UI execution.',
    projectIdeas: [
      'Responsive multi-page dashboard with analytics',
      'Interactive resume optimizer UI with live ATS scoring',
      'Accessible component library with tests and Storybook',
      'Full-stack job tracker with filters and saved searches'
    ],
    focusSkills: ['React', 'TypeScript', 'Next.js', 'Accessibility', 'Performance', 'Testing'],
    interviewTopics: ['Hooks', 'state management', 'performance optimization', 'accessibility', 'API integration']
  },
  backend: {
    label: 'Backend',
    summary: 'API design, data modeling, reliability, and service architecture.',
    projectIdeas: [
      'REST API with auth, pagination, and filtering',
      'Resume processing service with queue-based workers',
      'Job recommendation API with cached scoring',
      'Observability-first microservice with metrics and logs'
    ],
    focusSkills: ['FastAPI', 'PostgreSQL', 'Docker', 'System Design', 'Authentication', 'Caching'],
    interviewTopics: ['HTTP semantics', 'database design', 'scalability', 'caching', 'transactions']
  },
  devops: {
    label: 'DevOps',
    summary: 'Automation, delivery pipelines, infrastructure, and system reliability.',
    projectIdeas: [
      'Dockerized application with CI/CD pipeline',
      'Kubernetes deployment with health checks and autoscaling',
      'Infrastructure as code setup with Terraform',
      'Monitoring and alerting stack with dashboards'
    ],
    focusSkills: ['Docker', 'Kubernetes', 'Terraform', 'CI/CD', 'Linux', 'Monitoring'],
    interviewTopics: ['deployments', 'networking', 'observability', 'incident response', 'automation']
  },
  aiml: {
    label: 'AI/ML',
    summary: 'Applied machine learning, deployment, and portfolio-driven experimentation.',
    projectIdeas: [
      'End-to-end ML project with deployment',
      'NLP classification or summarization app',
      'Computer vision model demo with explanation',
      'RAG project with a clean evaluation story'
    ],
    focusSkills: ['Python', 'Machine Learning', 'PyTorch', 'TensorFlow', 'NLP', 'MLOps'],
    interviewTopics: ['model metrics', 'bias/variance', 'transformers', 'feature engineering', 'deployment']
  },
  fullstack: {
    label: 'Full Stack',
    summary: 'Product-style engineering across frontend, backend, and deployment layers.',
    projectIdeas: [
      'Full-stack job search dashboard with saved profiles',
      'ATS resume optimizer with resume and job comparison',
      'Project portfolio with analytics and admin views',
      'Realtime dashboard with notifications and activity feed'
    ],
    focusSkills: ['React', 'Next.js', 'FastAPI', 'Database Design', 'Docker', 'System Design'],
    interviewTopics: ['API boundaries', 'state management', 'schema design', 'performance', 'product thinking']
  }
};

export function getDomainProfile(domain: string | undefined | null): DomainProfile {
  const key = (domain || 'fullstack').toLowerCase() as DomainKey;
  return DOMAIN_PROFILES[key] ?? DOMAIN_PROFILES.fullstack;
}

import type { CourseResource, SkillResourceBundle } from './types';

export const COURSE_RESOURCES: CourseResource[] = [
  { skill: 'React', title: 'React.js', platform: 'YouTube - Codevolution', url: 'https://www.youtube.com/@Codevolution', tags: ['frontend'] },
  { skill: 'Next.js', title: 'Next.js 14', platform: 'YouTube - Vercel', url: 'https://www.youtube.com/@VercelHQ', tags: ['frontend'] },
  { skill: 'TypeScript', title: 'TypeScript', platform: 'YouTube - Matt Pocock', url: 'https://www.youtube.com/@mattpocockuk', tags: ['frontend'] },
  { skill: 'JavaScript', title: 'JavaScript Basics', platform: 'The Odin Project', url: 'https://www.theodinproject.com', tags: ['frontend'] },
  { skill: 'HTML', title: 'Responsive Web Design', platform: 'freeCodeCamp', url: 'https://www.freecodecamp.org/learn', tags: ['frontend'] },
  { skill: 'CSS', title: 'Responsive Web Design', platform: 'freeCodeCamp', url: 'https://www.freecodecamp.org/learn', tags: ['frontend'] },
  { skill: 'REST APIs', title: 'REST API Design', platform: 'YouTube - Web Dev Simplified', url: 'https://www.youtube.com/@WebDevSimplified', tags: ['backend', 'frontend'] },
  { skill: 'Node.js', title: 'Node.js & Express', platform: 'freeCodeCamp', url: 'https://www.freecodecamp.org/learn/back-end-development-and-apis/', tags: ['backend'] },
  { skill: 'FastAPI', title: 'FastAPI Practice', platform: 'FastAPI Docs', url: 'https://fastapi.tiangolo.com/', tags: ['backend'] },
  { skill: 'PostgreSQL', title: 'PostgreSQL', platform: 'YouTube - Hussein Nasser', url: 'https://www.youtube.com/@hnasr', tags: ['backend'] },
  { skill: 'MongoDB', title: 'MongoDB University', platform: 'MongoDB University', url: 'https://learn.mongodb.com', tags: ['backend'] },
  { skill: 'Docker', title: 'Docker', platform: 'YouTube - TechWorld with Nana', url: 'https://www.youtube.com/@TechWorldwithNana', tags: ['devops', 'backend'] },
  { skill: 'Kubernetes', title: 'Kubernetes', platform: 'YouTube - TechWorld with Nana', url: 'https://www.youtube.com/@TechWorldwithNana', tags: ['devops'] },
  { skill: 'Terraform', title: 'Terraform Tutorials', platform: 'HashiCorp Tutorials', url: 'https://developer.hashicorp.com/terraform/tutorials', tags: ['devops'] },
  { skill: 'CI/CD', title: 'CI/CD with GitHub Actions', platform: 'YouTube - Fireship', url: 'https://www.youtube.com/@Fireship', tags: ['devops'] },
  { skill: 'Git', title: 'Git & GitHub', platform: 'YouTube - Fireship', url: 'https://www.youtube.com/@Fireship', tags: ['all'] },
  { skill: 'Python', title: 'Python for Data Science', platform: 'Kaggle Learn', url: 'https://www.kaggle.com/learn', tags: ['aiml', 'backend'] },
  { skill: 'Machine Learning', title: 'Machine Learning Specialization', platform: 'Coursera Audit', url: 'https://www.coursera.org/specializations/machine-learning-introduction', tags: ['aiml'] },
  { skill: 'PyTorch', title: 'PyTorch Basics', platform: 'YouTube - Patrick Loeber', url: 'https://www.youtube.com/@patloeber', tags: ['aiml'] },
  { skill: 'TensorFlow', title: 'TensorFlow Developer Cert', platform: 'Coursera', url: 'https://www.coursera.org/professional-certificates/tensorflow-in-practice', tags: ['aiml'] },
  { skill: 'NLP', title: 'Hugging Face NLP', platform: 'Hugging Face', url: 'https://huggingface.co/learn', tags: ['aiml'] },
  { skill: 'Prompt Engineering', title: 'Prompt Engineering', platform: 'DeepLearning.AI', url: 'https://www.deeplearning.ai/short-courses/', tags: ['aiml'] },
  { skill: 'Figma', title: 'Figma UI Design', platform: 'Figma Community', url: 'https://www.figma.com/resources/learn-design/', tags: ['frontend'] },
  { skill: 'Accessibility', title: 'Google UX Design', platform: 'Coursera', url: 'https://www.coursera.org/professional-certificates/google-ux-design', tags: ['frontend'] },
  { skill: 'Tailwind CSS', title: 'Tailwind CSS', platform: 'YouTube - Traversy Media', url: 'https://www.youtube.com/@TraversyMedia', tags: ['frontend'] },
  { skill: 'SQL', title: 'SQL for Data Analysis', platform: 'Mode Analytics', url: 'https://mode.com/sql-tutorial/', tags: ['backend', 'data'] },
  { skill: 'Linux', title: 'Linux Command Line', platform: 'Linux Foundation Free', url: 'https://training.linuxfoundation.org', tags: ['devops'] },
  { skill: 'Monitoring', title: 'Prometheus & Grafana', platform: 'YouTube - Nana', url: 'https://www.youtube.com/@TechWorldwithNana', tags: ['devops'] },
  { skill: 'Testing', title: 'freeCodeCamp Testing', platform: 'freeCodeCamp', url: 'https://www.freecodecamp.org', tags: ['all'] }
];

export function findCourseForSkill(skill: string) {
  const normalized = skill.toLowerCase();
  return COURSE_RESOURCES.find((resource) => {
    const resourceSkill = resource.skill.toLowerCase();
    return normalized.includes(resourceSkill) || resourceSkill.includes(normalized);
  });
}

export function getSkillResourceBundle(skill: string): SkillResourceBundle {
  const exact = findCourseForSkill(skill);
  const query = encodeURIComponent(`${skill} free course youtube tutorial`);

  return {
    exact,
    youtube: {
      skill,
      title: `${skill} on YouTube`,
      platform: 'YouTube search',
      url: `https://www.youtube.com/results?search_query=${query}`
    },
    web: {
      skill,
      title: `${skill} free web learning`,
      platform: 'Web search',
      url: `https://www.google.com/search?q=${query}`
    }
  };
}

export function buildLinkedInApplyLink(title: string, company: string, domain?: string) {
  const keywords = [title, company, domain].filter(Boolean).join(' ');
  return `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(keywords)}&location=Remote`;
}

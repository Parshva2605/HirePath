# HirePath

HirePath is a local career acceleration platform for resume analysis, ATS scoring, skill-gap planning, GitHub portfolio evaluation, and job matching.

## What This Workspace Contains

- `hirepath_final/`
- `hirepath_final/agent/`: FastAPI backend for analysis pipeline
- `hirepath_final/product-dashboard/`: Next.js product dashboard UI
- `hirepath_final/skill_gap_db/`: domain and company skill requirement data
- `hirepath_final/job_folder/`: job dataset for matching
- `job_matcher/`: standalone job ranking module
- `github-analyzer/`: auxiliary GitHub analysis utilities

## Core Features

- Resume parsing (PDF/DOCX)
- ATS scoring and improvement guidance
- Skill-gap analysis by target domain/company
- GitHub profile and repository detail analysis
- Personalized learning path, roadmap, and interview prep
- Job matching with score-based ranking and apply links

## Local Architecture

- Backend API: FastAPI (`hirepath_final/agent/main.py`)
- Frontend: Next.js dashboard (`hirepath_final/product-dashboard/app/page.tsx`)
- Local AI integration: Ollama endpoint for roadmap/interview/GitHub quality generation

## Quick Start

### 1. Start backend

From `hirepath_final/agent`:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend docs:

- `http://localhost:8000/docs`

### 2. Start dashboard

From `hirepath_final/product-dashboard`:

```powershell
npm install
npm run dev
```

Dashboard URL:

- `http://localhost:3000`

### 3. (Optional) Production build

From `hirepath_final/product-dashboard`:

```powershell
npm run build
npm run start
```

## API Highlights

- `POST /api/analyze`: full end-to-end analysis
- `POST /api/ats-check`: quick ATS check
- `POST /api/skill-gap`: standalone gap analysis
- `GET /api/status`: backend and Ollama health
- `POST /api/validate-github`: GitHub profile validation

## Notes

- Keep environment values in local `.env` files.
- The root `.gitignore` is configured to ignore build outputs, runtime folders, and local environment files.
- Recommended run order: backend first, then dashboard.

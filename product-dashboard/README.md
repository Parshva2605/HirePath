# HirePath Product Dashboard

Single-page Next.js dashboard for the HirePath workflow.

## What it does

- Accepts one resume upload, GitHub URL, target company, and domain
- Runs the backend analysis pipeline once
- Shows ATS score first
- Shows the ATS optimization plan and projected improved score
- Surfaces skill gaps with course links
- Summarizes GitHub quality and project ideas
- Lists matched jobs with LinkedIn apply links and match percentages
- Shows roadmap, learning path, and interview prep on the same page

## Setup

1. Install dependencies:

```bash
cd d:\HirePath\product-dashboard
npm install
```

2. Configure the backend URL if needed:

```bash
set NEXT_PUBLIC_HIREPATH_API=http://localhost:8000
```

3. Run the app:

```bash
npm run dev
```

4. Open:

```bash
http://localhost:3000
```

## Notes

- The dashboard calls the local FastAPI backend at `http://localhost:8000` by default.
- LinkedIn links are generated as search/apply links from the matched job title and company.

## Vercel Deployment

1. Deploy this repository to Vercel.
2. Set the project Root Directory to `product-dashboard`.
3. Add environment variable in Vercel:

```bash
NEXT_PUBLIC_HIREPATH_API=https://your-backend-domain.com
```

4. Deploy. The frontend will call your hosted backend URL.

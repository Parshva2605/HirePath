# HirePath Web Interface

Professional multi-page career acceleration platform with minimal black & white design.

## 🚀 Quick Start

### 1. Backend Running
The FastAPI backend should already be running on `http://localhost:8000`

To verify:
```bash
curl http://localhost:8000/api/status
```

### 2. Open Web Interface
Open this file in your browser:
```
file:///d:/HirePath/hirepath_final/web/index.html
```

Or serve it locally:
```bash
# Option 1: Python simple HTTP server
cd d:\HirePath\hirepath_final\web
python -m http.server 8001
# Then visit: http://localhost:8001
```

## 📄 Pages

### Home
Dashboard overview with quick access to all features and system status

### Analyze (Full Pipeline)
Complete career assessment combining:
- Resume ATS scoring
- Skill gap analysis
- GitHub profile evaluation
- Job matching
- Career roadmap generation

### ATS Check
Quick resume scoring tool for instant ATS feedback

### Skills
Skill gap analyzer for target domains and companies

### Jobs
Find positions matching your skills

### GitHub
Professional portfolio evaluation

### Status
System diagnostics and health checks

## 🛠️ Features

✅ **Zero Color Design** - Minimal black and white theme
✅ **Responsive Layout** - Works on desktop, tablet, mobile
✅ **Multi-Page Structure** - Clean separation of features
✅ **Client-Side Navigation** - Fast page transitions
✅ **Real-Time Status** - Backend health monitoring
✅ **Progressive Enhancement** - Works even if Ollama is offline

## 🔌 API Integration

All pages connect to backend endpoints:

| Feature | Endpoint | Method |
|---------|----------|--------|
| Full Analysis | `/api/analyze` | POST |
| ATS Check | `/api/ats-check` | POST |
| Skill Gap | `/api/skill-gap` | POST |
| Job Matches | `/api/job-matches` | POST |
| GitHub Validation | `/api/validate-github` | POST |
| System Status | `/api/status` | GET |

## 📁 Structure

```
web/
├── index.html          # Main application (all pages included)
├── pages/              # (Optional) Individual page snippets
└── assets/
    ├── style.css       # Minimal B&W styling (10KB)
    └── script.js       # Navigation & API integration (4KB)
```

## 🎨 Design System

- **Colors**: Black, White, Grays
- **Spacing**: 8px, 12px, 16px, 20px, 24px units
- **Typography**: System fonts for performance
- **Components**: Cards, Buttons, Forms, Tables, Badges
- **Responsive**: 0px, 768px, 1024px breakpoints

## ⚙️ Configuration

Edit `index.html` to customize:

1. **API URL** (line ~6 in script):
   ```javascript
   const API_URL = 'http://localhost:8000';
   ```

2. **Domain Options** (in form selects):
   - AI/Machine Learning
   - DevOps
   - Frontend Development
   - Backend Development
   - (Add more as needed)

3. **Company Options**:
   - Google
   - Amazon
   - Microsoft
   - Startup

## 🐞 Troubleshooting

### Backend Offline
- ❌ Shows warning on home page
- ✅ Try: `cd d:\HirePath\hirepath_final && python -m uvicorn agent.main:app --reload`

### Ollama Offline
- ❌ AI features show "requires Ollama"
- ✅ Try: `ollama serve` in another terminal

### CORS Issues
- ❌ API calls fail from browser
- ✅ Ensure backend has CORS enabled:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

### File Upload Issues
- ❌ Resume upload fails
- ✅ Ensure `resume_uploads/` folder exists in backend
- ✅ Check file size < 10MB
- ✅ Ensure PDF/DOCX format

## 📊 Page Templates

Each page has consistent structure:
1. **Page Header** - Title and description
2. **Form Panel** - User inputs
3. **Results Panel** - Dynamic content
4. **Status Indicators** - Success/warning/error alerts

## 🔄 API Response Handling

All pages handle three response states:

```javascript
// Loading
showLoading(element);

// Success
element.innerHTML = htmlResults;

// Error
showError(element, error.message);
```

## 🎯 Next Steps

1. Test each page with sample data
2. Create sample resume files for testing
3. Create sample GitHub profiles
4. Configure domain/company databases as needed
5. Set up actual job listings in job database

## 📖 Documentation

- [Backend API Docs](http://localhost:8000/docs)
- [Backend README](../README.md)
- [Setup Guide](../SETUP.md)
- [Project Status](../PROJECT_READY.txt)

## 🔐 Security Notes

- This is a local application - no data is sent externally
- Resume files are stored in `resume_uploads/`
- All processing happens on your machine
- No external API keys required

## 💡 Tips

- Use browser DevTools (F12) to debug API calls
- Check browser console for JavaScript errors
- Network tab shows all API requests/responses
- Clear browser cache if styles/scripts don't update

---

**Version**: 1.0
**Last Updated**: March 4, 2026
**Status**: ✅ Production Ready

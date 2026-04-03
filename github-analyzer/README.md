# 🚀 GitHub Profile Analyzer

**AI-Powered GitHub Profile Analyzer with Local LLM Integration**

Analyze any GitHub profile, get personalized project recommendations, and improve your developer profile to land jobs at top tech companies like Microsoft, Google, and more!

## ✨ Features

- 📊 **Enhanced Rating System** - Accurate 0-100 scoring with 5-dimension analysis
- ⭐ **Per-Repository Analysis** - Each repo gets a 5-star quality rating
- 🎯 **Domain Detection** - Automatic categorization (AI/ML, Web Dev, DevOps, etc.)
- 🤖 **AI Recommendations** - Personalized project suggestions using local Ollama LLM
- 📈 **Progress Tracking** - API usage monitoring and quality metrics
- 🎨 **Beautiful UI** - Modern dark theme with interactive visualizations
- 🔒 **Privacy First** - All data processing happens locally

## 📋 Prerequisites

- **Python 3.10+** (tested on Python 3.10 and 3.13)
- **Ollama** (for local LLM) - [Download here](https://ollama.ai)
- **GitHub Personal Access Token** - [Generate here](https://github.com/settings/tokens)
- **Operating System**: Windows, macOS, or Linux

## 🛠️ Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/github-analyzer.git
cd github-analyzer
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Ollama

1. **Install Ollama** from [https://ollama.ai](https://ollama.ai)

2. **Pull a model** (recommended: qwen2.5:3b for speed, llama3.1:8b for quality):
```bash
ollama pull qwen2.5:3b
# OR
ollama pull llama3.1:8b
```

3. **Start Ollama** (it should auto-start, or run):
```bash
ollama serve
```

### Step 5: Configure Environment Variables

1. **Copy the example environment file:**
```bash
cp .env.example .env
```

2. **Edit `.env` and add your credentials:**
```env
# GitHub Personal Access Token (required)
GITHUB_TOKEN=ghp_your_token_here

# Ollama Configuration (required)
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_HOST=http://localhost:11434
```

3. **Generate GitHub Token:**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `repo`, `read:user`
   - Copy the token and paste in `.env`

## 🚀 Usage

### Start the Server

**Windows:**
```bash
.\venv\Scripts\activate
python run.py
```

**macOS/Linux:**
```bash
source venv/bin/activate
python run.py
```

**Or use the batch file (Windows only):**
```bash
start.bat
```

### Access the Application

Open your browser and go to:
```
http://localhost:8000
```

### Analyze a Profile

1. Enter a GitHub URL (e.g., `https://github.com/torvalds`)
2. Select target domain (e.g., AI/ML, Web Development, DevOps)
3. Enter target companies (e.g., Microsoft, Google)
4. Click **Analyze Profile**
5. View detailed results with ratings, recommendations, and insights!

## 📊 What You'll Get

### Overall Rating (0-100)
- **80-100**: Excellent profile, ready for top-tier opportunities
- **60-79**: Good profile, focus on recommendations
- **40-59**: Developing profile, implement action items
- **0-39**: Great potential, follow the recommendations

### Rating Breakdown (5 Dimensions)
- **Repository Impact** (35 points): Stars, forks, repository count
- **Community Engagement** (25 points): Followers, follower/following ratio
- **Tech Stack Alignment** (20 points): Relevance to target domain
- **Project Quality** (15 points): Documentation, topics, high-quality repos
- **Activity Consistency** (5 points): Regular contributions

### Per-Repository Analysis
Each repository receives:
- **Domain**: AI/ML, Web Dev, DevOps, Mobile, etc.
- **Quality Rating**: 0-5 stars based on:
  - Popularity (stars/forks)
  - Community engagement
  - Documentation quality
  - Discoverability (topics/tags)
- **Impact Level**: 🔥 High, ⭐ Medium, 📈 Growing, 🌱 Early
- **Maturity Status**: ✅ Mature, 🔄 Active, ⚠️ Needs Polish, 🚧 WIP

### AI-Powered Recommendations
- 3 personalized project ideas targeting your specific gaps
- Technologies aligned with target companies
- Specific reasoning based on your profile statistics
- Actionable improvement suggestions

### Additional Insights
- Domain distribution across all projects
- Quality summary and metrics
- Company alignment scores
- API usage tracking
- Strengths and weaknesses analysis

## 🔧 Configuration

### Switch LLM Model

```bash
python switch_model.py
```

Choose from available models:
- `qwen2.5:3b` - Fast, lightweight (recommended for most users)
- `llama3.1:8b` - Higher quality responses
- `mistral:latest` - Good balance
- Any other Ollama model you have installed

### Validate GitHub Token

```bash
python check_token.py
```

This will verify your GitHub token and show remaining API calls.

## 🗂️ Project Structure

```
github-analyzer/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── github_fetcher.py          # GitHub API integration
│   ├── enhanced_analyzer.py       # Rating algorithm
│   ├── repo_analyzer.py           # Per-repository analysis
│   ├── llm_client.py              # Ollama LLM integration
│   ├── analyzer.py                # Legacy analyzer
│   └── models.py                  # Data models
├── templates/
│   └── index.html                 # Web interface
├── static/
│   └── css/
│       └── style.css              # Styling
├── venv/                          # Virtual environment (git-ignored)
├── .env                           # Environment variables (git-ignored)
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── run.py                         # Main launcher
├── start.bat                      # Windows launcher
├── check_token.py                 # Token validator
├── switch_model.py                # Model switcher
└── README.md                      # This file
```

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Make sure virtual environment is activated
```bash
# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Issue: GitHub API 403 Forbidden

**Solution:** Check your token
```bash
python check_token.py
```
If invalid, generate a new token at https://github.com/settings/tokens

### Issue: Ollama connection failed

**Solution:** Ensure Ollama is running
```bash
ollama serve
```
The app will use fallback recommendations if Ollama is unavailable.

### Issue: Port 8000 already in use

**Solution:** Find and kill the process
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue: NaN values in rating breakdown

**Solution:** Restart the server (CTRL+C, then `python run.py`)

## 🔒 Privacy & Security

- All analysis happens **locally** - no data sent to external services
- Your GitHub token is stored in `.env` (git-ignored)
- LLM runs on your machine via Ollama
- No telemetry or tracking

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **PyGithub** - GitHub API wrapper
- **Ollama** - Local LLM runtime
- **Uvicorn** - ASGI server

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/github-analyzer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/github-analyzer/discussions)

## 🚀 Roadmap

- [ ] Export results to PDF
- [ ] Historical tracking (compare progress over time)
- [ ] Multiple profile comparison
- [ ] Custom domain definitions
- [ ] Integration with LinkedIn profiles
- [ ] VSCode extension

---

**Made with ❤️ by developers, for developers**

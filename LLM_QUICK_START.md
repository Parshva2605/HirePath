# Quick Start: LLM Configuration

## Development (Local Ollama - FREE)

1. Start Ollama:
```bash
ollama serve
```

2. Create `.env` file in `agent/` folder:
```
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3
```

3. Start backend:
```bash
cd agent
python -m uvicorn main:app --reload
```

---

## Production (Vercel) - Choose ONE Option

### Option A: Groq (Recommended - FREE TIER!)
```bash
# 1. Get key from https://console.groq.com/
# 2. Set environment variables in Vercel:
LLM_PROVIDER=groq
LLM_API_KEY=gsk_your_api_key_here
LLM_MODEL=mixtral-8x7b-32768

# 3. Install locally for testing:
pip install groq
```

### Option B: OpenAI (Most Popular)
```bash
# 1. Get key from https://platform.openai.com/api-keys/
# 2. Set environment variables in Vercel:
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-3.5-turbo

# 3. Install locally for testing:
pip install openai
```

### Option C: Anthropic Claude (Best Quality)
```bash
# 1. Get key from https://console.anthropic.com/
# 2. Set environment variables in Vercel:
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-your-api-key-here
LLM_MODEL=claude-3-haiku

# 3. Install locally for testing:
pip install anthropic
```

---

## How Adaptive Routing Works

The `llm_adapter.py` module automatically:
- ✅ Detects which provider is configured
- ✅ Routes to the correct API
- ✅ Falls back to deterministic content if provider unavailable
- ✅ Works on both local and Vercel

---

## Test Your Setup

```bash
# Test local Ollama
curl http://localhost:8000/api/status

# Response:
{
  "ollama": {
    "available": true,
    "provider": "ollama",
    "model": "llama3"
  }
}
```

---

## Costs Comparison

| Provider | Cost per Analysis | Setup | Free Tier |
|----------|------------------|-------|-----------|
| **Groq** | ~$0 (free tier) | 5 min | YES (30 req/min) |
| **OpenAI** | ~$0.001-0.03 | 5 min | NO |
| **Claude** | ~$0.0008-0.003 | 5 min | NO |
| **Ollama** | FREE | Setup server | YES |

---

## Next: Deploy to Vercel

1. Choose a provider above and get API key
2. Add env vars to Vercel dashboard
3. Push code to GitHub
4. Vercel auto-deploys
5. Your app will use cloud LLM on Vercel, local Ollama in development

**That's it!** 🚀

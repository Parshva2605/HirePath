# LLM Provider Setup Guide for Vercel Deployment

## Current Setup
- **Default:** Local Ollama (development)
- **For Vercel:** Switch to cloud API (needed because Vercel functions are stateless)

---

## **Option 1: OpenAI GPT (Recommended for beginners)**

### Setup:
1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`:
```
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-3.5-turbo
# or for better quality: gpt-4
```

3. Install dependency:
```bash
pip install openai
```

### Cost:
- GPT-3.5: ~$0.001 per analysis
- GPT-4: ~$0.03 per analysis

---

## **Option 2: Anthropic Claude (Best quality)**

### Setup:
1. Get API key from https://console.anthropic.com/
2. Add to `.env`:
```
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-your-api-key-here
LLM_MODEL=claude-3-haiku
# or for better: claude-3-sonnet or claude-3-opus
```

3. Install dependency:
```bash
pip install anthropic
```

### Cost:
- Claude Haiku: ~$0.0008 per analysis
- Claude Sonnet: ~$0.003 per analysis

---

## **Option 3: Groq (Fastest & cheapest)**

### Setup:
1. Get API key from https://console.groq.com/
2. Add to `.env`:
```
LLM_PROVIDER=groq
LLM_API_KEY=your-groq-api-key
LLM_MODEL=mixtral-8x7b-32768
# or: llama2-70b-4096
```

3. Install dependency:
```bash
pip install groq
```

### Cost:
- Free tier: 30 requests per minute (great for testing!)
- Paid tier: Very cheap

---

## **Option 4: Self-Hosted Ollama on VPS**

### Setup:
1. Deploy Ollama on DigitalOcean, AWS, or Render
2. Add to `.env`:
```
LLM_PROVIDER=ollama
LLM_BASE_URL=https://your-ollama-server.com:11434
LLM_MODEL=llama3
```

### Cost:
- Server: $5-20/month
- Data transfer: Minimal

---

## **Development Setup (Local Ollama)**

Keep this in local `.env`:
```
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=llama3
```

Then start Ollama:
```bash
ollama serve
```

---

## **Vercel Deployment**

### Steps:
1. Choose a provider (OpenAI/Anthropic/Groq recommended)
2. In Vercel dashboard:
   - Go to Settings → Environment Variables
   - Add: `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`
3. Redeploy your app
4. The backend will automatically use the cloud API

### Example Vercel env vars:
```
LLM_PROVIDER=groq
LLM_API_KEY=gsk_xxxxx
LLM_MODEL=mixtral-8x7b-32768
```

---

## **Testing LLM Connection**

```bash
curl http://localhost:8000/api/status
```

Output will show:
```json
{
  "llm": {
    "available": true,
    "provider": "groq",
    "model": "mixtral-8x7b-32768"
  }
}
```

---

## **Fallback Behavior**

If the LLM is unavailable, the system will:
- Return pre-generated analysis (deterministic)
- No API call made
- Response still useful for the user
- No error thrown to frontend

---

## **My Recommendation for You**

📌 **For Vercel deployment:** Use **Groq** (free tier, fast, cheap)
📌 **For production:** Use **OpenAI GPT-4** or **Claude Sonnet** (quality > cost)
📌 **Keep local Ollama** for development (free, fast iteration)

---

## **Next Steps**

1. Pick a provider from above
2. Get the API key
3. I'll update your code to use it
4. Deploy to Vercel

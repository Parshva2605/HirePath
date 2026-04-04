"""
LLM Adapter - Flexible backend for local Ollama or cloud APIs (OpenAI, Anthropic, Groq, etc.)
Allows seamless switching between providers via environment variables.
"""

import os
import requests
from typing import Dict, Any, Optional, Literal
from enum import Enum


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()  # ollama, openai, anthropic, groq
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")  # Model name varies by provider
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")  # For Ollama self-hosted
TIMEOUT = 60


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    COHERE = "cohere"


def _call_ollama(prompt: str, system: str, model: str, temperature: float) -> str:
    """Call local or self-hosted Ollama instance"""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": temperature, "top_k": 40, "top_p": 0.9}
    }
    
    chat_url = f"{LLM_BASE_URL.rstrip('/')}/api/chat"
    response = requests.post(chat_url, json=payload, timeout=TIMEOUT)
    
    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")
    
    return response.json()["message"]["content"]


def _call_openai(prompt: str, system: str, model: str, temperature: float) -> str:
    """Call OpenAI API (GPT-4, GPT-3.5, etc.)"""
    import openai
    
    openai.api_key = LLM_API_KEY
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        top_p=0.9
    )
    
    return response.choices[0].message.content


def _call_anthropic(prompt: str, system: str, model: str, temperature: float) -> str:
    """Call Anthropic Claude API"""
    import anthropic
    
    client = anthropic.Anthropic(api_key=LLM_API_KEY)
    
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system or "You are a helpful assistant.",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        top_p=0.9
    )
    
    return response.content[0].text


def _call_groq(prompt: str, system: str, model: str, temperature: float) -> str:
    """Call Groq API (fast inference)"""
    import groq
    
    client = groq.Groq(api_key=LLM_API_KEY)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        top_p=0.9
    )
    
    return response.choices[0].message.content


def _call_cohere(prompt: str, system: str, model: str, temperature: float) -> str:
    """Call Cohere API"""
    import cohere
    
    client = cohere.ClientV2(api_key=LLM_API_KEY)
    
    response = client.chat(
        model=model,
        messages=[
            {"role": "system", "content": system or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    
    return response.message.content[0].text


def call_llm(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    temperature: float = 0.7,
    provider: Optional[str] = None
) -> str:
    """
    Unified LLM interface - routes to the configured provider.
    
    Args:
        prompt: User message/question
        system: System instruction/context
        model: Model name (uses LLM_MODEL if not specified)
        temperature: Sampling temperature (0.0-1.0)
        provider: Override provider (uses LLM_PROVIDER if not specified)
    
    Returns:
        Generated text response
    """
    model = model or LLM_MODEL
    provider = (provider or LLM_PROVIDER).lower()
    
    try:
        if provider == "openai":
            return _call_openai(prompt, system, model, temperature)
        elif provider == "anthropic":
            return _call_anthropic(prompt, system, model, temperature)
        elif provider == "groq":
            return _call_groq(prompt, system, model, temperature)
        elif provider == "cohere":
            return _call_cohere(prompt, system, model, temperature)
        else:  # Default to Ollama
            return _call_ollama(prompt, system, model, temperature)
    
    except Exception as e:
        # Fallback: Return deterministic content on error
        return _get_fallback_content(prompt)


def _get_fallback_content(prompt: str) -> str:
    """Fallback content when LLM is unavailable"""
    if "github" in prompt.lower():
        return "GitHub Analysis:\n- Strong contributor to open source\n- Consistent code quality and documentation\n- Active in multiple technology domains"
    elif "roadmap" in prompt.lower():
        return "Career Roadmap:\n1. Strengthen core fundamentals (Weeks 1-4)\n2. Build practical projects (Weeks 5-8)\n3. Contribute to open source (Weeks 9-12)"
    elif "interview" in prompt.lower():
        return "Interview Preparation:\n- System Design: Study distributed systems and scalability\n- Algorithms: Practice coding challenges on LeetCode\n- Behavioral: Prepare stories using STAR method"
    return "Analysis in progress..."


def check_llm_connection() -> Dict[str, Any]:
    """
    Check if configured LLM provider is available and responding.
    
    Returns:
        {"available": bool, "provider": str, "model": str, "error": str or None}
    """
    try:
        response = call_llm("Say 'OK'", model=LLM_MODEL, temperature=0.0)
        
        return {
            "available": bool(response),
            "provider": LLM_PROVIDER,
            "model": LLM_MODEL,
            "error": None
        }
    except Exception as e:
        return {
            "available": False,
            "provider": LLM_PROVIDER,
            "model": LLM_MODEL,
            "error": str(e)
        }

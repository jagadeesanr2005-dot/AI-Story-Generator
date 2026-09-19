"""AI story generation service with Groq/Gemini support and safe fallback."""

import os
import re
from typing import Dict

import requests
from dotenv import load_dotenv

from story_engine import generate_story as fallback_generate, GENRES, LENGTHS

load_dotenv()

WORD_RANGES = LENGTHS


def _extract_jsonish(text: str) -> Dict[str, str]:
    """Extract title/story from a model response without requiring JSON mode."""
    text = text.strip()
    title = "Untitled Story"
    story = text
    match = re.search(r"(?:TITLE|Title)\s*:\s*(.+?)(?:\n|$)", text)
    if match:
        title = match.group(1).strip().strip('"')
        story = re.sub(r"^(?:TITLE|Title)\s*:.+?(?:\n|$)", "", text, count=1).strip()
    match = re.search(r"(?:STORY|Story)\s*:\s*(.*)$", story, flags=re.S)
    if match:
        story = match.group(1).strip()
    return {"title": title[:120], "story": story.strip()}


def _prompt(user_prompt: str, genre: str, length: str) -> str:
    lo, hi = WORD_RANGES[length]
    genre_name = GENRES.get(genre, genre.title())
    return f"""You are a professional fiction writer.

Create ONE original, self-contained {genre_name} story based on this user's idea:
{user_prompt}

Requirements:
- Target approximately {lo}-{hi} words. Do not produce a tiny summary.
- Follow the requested idea closely while adding original details.
- Give the story a clear beginning, rising conflict, meaningful turning point, and satisfying ending.
- Use natural dialogue when it improves the story.
- Keep character motivations consistent and avoid random unrelated events.
- Do not mention AI, prompts, word counts, these instructions, or content-generation limitations.
- Do not use headings inside the story.
- Return exactly two lines/sections:
TITLE: <short compelling title>
STORY: <the complete story>
"""


def _groq(prompt: str) -> Dict[str, str]:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You write high-quality original fiction."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.9,
            "max_tokens": 2500,
        },
        timeout=60,
    )
    if not response.ok:
        raise RuntimeError(f"Groq API error {response.status_code}: {response.text[:300]}")
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return _extract_jsonish(content)


def _gemini(prompt: str) -> Dict[str, str]:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    response = requests.post(
        url,
        params={"key": key},
        json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.9}},
        timeout=60,
    )
    if not response.ok:
        raise RuntimeError(f"Gemini API error {response.status_code}: {response.text[:300]}")
    data = response.json()
    content = data["candidates"][0]["content"]["parts"][0]["text"]
    return _extract_jsonish(content)


def generate_story(genre: str, length: str, prompt: str) -> Dict[str, str]:
    provider = os.getenv("AI_PROVIDER", "auto").strip().lower()
    ai_prompt = _prompt(prompt, genre, length)

    providers = [provider] if provider in {"groq", "gemini"} else ["groq", "gemini"]
    errors = []
    for selected in providers:
        try:
            result = _groq(ai_prompt) if selected == "groq" else _gemini(ai_prompt)
            if len(result["story"].split()) < 100:
                raise RuntimeError("AI returned an unusually short story")
            return {**result, "genre": genre, "length": length, "provider": selected}
        except Exception as exc:
            errors.append(f"{selected}: {exc}")

    result = fallback_generate(genre=genre, length=length, prompt=prompt)
    result["warning"] = "AI provider unavailable; generated with the built-in offline fallback."
    result["provider_errors"] = errors
    return result

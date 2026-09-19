"""AI story generation and translation service with AI + free web fallback."""
import os
import re
from typing import Dict, List
import requests
from dotenv import load_dotenv
from story_engine import generate_story as fallback_generate, GENRES, LENGTHS

load_dotenv()


def _clean_model_name(value: str, default: str) -> str:
    value = (value or "").strip()

    # Remove accidental model= prefix
    if value.lower().startswith("model="):
        value = value[6:].strip()

    # Remove accidental quotes
    value = value.strip('"').strip("'").strip()

    return value or default


WORD_RANGES = LENGTHS

LANGUAGE_CODES = {
    "Tamil": "ta",
    "Malayalam": "ml",
    "Hindi": "hi",
    "Telugu": "te",
    "Kannada": "kn",
    "English": "en"
}


def _extract_jsonish(text: str) -> Dict[str, str]:
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
    return f"""You are a professional fiction writer.\n\nCreate ONE original, self-contained {genre_name} story based on this user's idea:\n{user_prompt}\n\nRequirements:\n- Target approximately {lo}-{hi} words. Do not produce a tiny summary.\n- Follow the requested idea closely while adding original details.\n- Give the story a clear beginning, rising conflict, meaningful turning point, and satisfying ending.\n- Use natural dialogue when it improves the story.\n- Keep character motivations consistent and avoid random unrelated events.\n- Do not mention AI, prompts, word counts, these instructions, or content-generation limitations.\n- Do not use headings inside the story.\n- Return exactly two sections:\nTITLE: <short compelling title>\nSTORY: <the complete story>\n"""


def _groq(prompt: str) -> Dict[str, str]:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key: raise RuntimeError("GROQ_API_KEY is not configured")
    model = _clean_model_name(
    os.getenv("GROQ_MODEL"),
    "openai/gpt-oss-120b"
)
    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"}, json={"model":model,"messages":[{"role":"system","content":"You write high-quality original fiction."},{"role":"user","content":prompt}],"temperature":0.9,"max_tokens":2500}, timeout=60)
    if not r.ok: raise RuntimeError(f"Groq API error {r.status_code}: {r.text[:300]}")
    return _extract_jsonish(r.json()["choices"][0]["message"]["content"])


def _gemini(prompt: str) -> Dict[str, str]:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key: raise RuntimeError("GEMINI_API_KEY is not configured")
    model = _clean_model_name(
    os.getenv("GEMINI_MODEL"),
    "gemini-3.6-flash"
)
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    r=requests.post(url,params={"key":key},json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.9}},timeout=60)
    if not r.ok: raise RuntimeError(f"Gemini API error {r.status_code}: {r.text[:300]}")
    return _extract_jsonish(r.json()["candidates"][0]["content"]["parts"][0]["text"])


def generate_story(genre: str, length: str, prompt: str) -> Dict[str, str]:
    provider = os.getenv("AI_PROVIDER", "auto").strip().lower()

    if provider in {"groq", "gemini"}:
        providers = [provider]
    else:
        providers = ["groq", "gemini"]

    errors = []

    for selected in providers:
        try:
            print(f"\n[AI] Trying provider: {selected}")

            if selected == "groq":
                result = _groq(_prompt(prompt, genre, length))
            else:
                result = _gemini(_prompt(prompt, genre, length))

            if len(result["story"].split()) < 100:
                raise RuntimeError(
                    "AI returned an unusually short story"
                )

            print(f"[AI] SUCCESS: {selected}")

            return {
                **result,
                "genre": genre,
                "length": length,
                "provider": selected
            }

        except Exception as exc:
            error_message = f"{selected}: {exc}"
            print(f"[AI] FAILED: {error_message}")
            errors.append(error_message)

    # Offline fallback
    result = fallback_generate(
        genre=genre,
        length=length,
        prompt=prompt
    )

    result["warning"] = (
        "AI provider unavailable; generated with the built-in offline fallback."
    )

    result["provider"] = "offline"
    result["provider_errors"] = errors

    print("\n[AI] ALL AI PROVIDERS FAILED")

    for error in errors:
        print(f"[AI] {error}")

    return result


def _translate_with_ai(text: str, language: str) -> str:
    prompt=f"""Translate the following fiction into {language}. Preserve the meaning, names, dialogue, paragraph breaks, emotion, and story structure. Return ONLY the translation. Do not summarize or explain.\n\n{text}"""
    provider=os.getenv("AI_PROVIDER","auto").strip().lower()
    providers=[provider] if provider in {"groq","gemini"} else ["groq","gemini"]
    errors=[]
    for selected in providers:
        try:
            if selected=="groq": return _groq_text(prompt)
            return _gemini_text(prompt)
        except Exception as exc: errors.append(f"{selected}: {exc}")
    raise RuntimeError("AI translation unavailable: " + " | ".join(errors))


def _groq_text(prompt: str) -> str:
    key=os.getenv("GROQ_API_KEY","").strip()
    if not key: raise RuntimeError("GROQ_API_KEY is not configured")
    model = _clean_model_name(
    os.getenv("GROQ_MODEL"),
    "openai/gpt-oss-120b"
)
    r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},json={"model":model,"messages":[{"role":"user","content":prompt}],"temperature":0.2,"max_tokens":3000},timeout=60)
    if not r.ok: raise RuntimeError(f"Groq API error {r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]["content"].strip()


def _gemini_text(prompt: str) -> str:
    key=os.getenv("GEMINI_API_KEY","").strip()
    if not key: raise RuntimeError("GEMINI_API_KEY is not configured")
    model = _clean_model_name(
    os.getenv("GEMINI_MODEL"),
    "gemini-3.6-flash"
)
    r=requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",params={"key":key},json={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.2}},timeout=60)
    if not r.ok: raise RuntimeError(f"Gemini API error {r.status_code}: {r.text[:300]}")
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def _google_free_translate(text: str, target: str) -> str:
    """No-key fallback using Google's public translation endpoint. Splits long text to avoid URL limits."""
    code=LANGUAGE_CODES[target]
    if code=="en": return text
    paragraphs=text.split("\n\n")
    out=[]
    for paragraph in paragraphs:
        if not paragraph.strip(): out.append(""); continue
        chunks=[]; words=paragraph.split(); current=[]; size=0
        for word in words:
            if current and size+len(word)+1>900:
                chunks.append(" ".join(current)); current=[]; size=0
            current.append(word); size+=len(word)+1
        if current: chunks.append(" ".join(current))
        translated=[]
        for chunk in chunks:
            r=requests.get("https://translate.googleapis.com/translate_a/single",params={"client":"gtx","sl":"auto","tl":code,"dt":"t","q":chunk},timeout=20)
            if not r.ok: raise RuntimeError(f"Free translation service returned HTTP {r.status_code}")
            data=r.json()
            translated.append("".join(part[0] for part in data[0] if part and part[0]))
        out.append(" ".join(translated))
    return "\n\n".join(out)


def translate_story(title: str, story: str, language: str) -> Dict[str, str]:
    if language not in LANGUAGE_CODES: raise RuntimeError("Unsupported translation language")
    if language=="English": return {"title":title,"story":story,"language":language,"provider":"original"}
    errors=[]
    try:
        translated=_translate_with_ai(story,language)
        translated_title=_translate_with_ai(title,language)
        return {"title":translated_title,"story":translated,"language":language,"provider":"ai-translation"}
    except Exception as exc: errors.append(str(exc))
    try:
        translated=_google_free_translate(story,language)
        translated_title=_google_free_translate(title,language)
        return {"title":translated_title,"story":translated,"language":language,"provider":"free-translation"}
    except Exception as exc: errors.append(str(exc))
    raise RuntimeError("Translation failed. Add a GROQ_API_KEY or GEMINI_API_KEY, or make sure your PC has internet access for the free translator. " + " | ".join(errors))

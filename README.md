# StoryForge — AI Story Generator

A polished Flask story-writing app that turns a user's idea into an original story using an AI provider when configured, with a prompt-aware offline fallback when no API key is available.

## What was improved

### Problems in the original version
- It was not actually AI generation; it stitched together pre-written template fragments.
- The user's prompt had very little influence on the generated plot.
- Short/Medium/Long were not reliable length controls.
- History and favorites disappeared on refresh.
- No clear provider/fallback state was shown.
- No JSON export.
- The README contained unresolved Git merge-conflict markers.
- The frontend had limited error handling and no persistent theme preference.

### New version
- Real AI generation through **Groq** or **Gemini**.
- Automatic provider selection (`AI_PROVIDER=auto`) with Groq first and Gemini second.
- Offline fallback still works without an API key.
- Length targets: Short 250–350, Medium 600–800, Long 1,100–1,400 words.
- Prompt-aware generation with a proper beginning, conflict, turning point, and ending.
- Persistent history and favorites using browser local storage.
- Regenerate, copy, TXT download, and JSON export.
- Light/dark theme persists between sessions.
- Clear AI/offline provider badge and friendly errors.
- `/health` endpoint for quick server checks.
- Secret-safe `.env.example` and `.gitignore`.
- Responsive UI for desktop and mobile.

## Setup

1. Create a virtual environment:

```bash
python -m venv .venv
.venv\\Scripts\\activate
```

2. Install packages:

```bash
pip install -r requirements.txt
```

3. Optional: create `.env` from `.env.example` and add your own provider key. **Never paste the real key into GitHub or chat.**

Example:

```env
AI_PROVIDER=groq
GROQ_API_KEY=your-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

Or use Gemini:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-2.5-flash
```

If no key is configured, the app automatically uses its offline fallback.

4. Run:

```bash
python app.py
```

5. Open `http://127.0.0.1:5000`.

## Project structure

```text
AI-Story-Generator-main/
├── app.py
├── story_generator.py      # AI provider integration + fallback selection
├── story_engine.py         # Offline prompt/length-aware generator
├── requirements.txt
├── .env.example
├── .gitignore
├── templates/index.html
└── static/
    ├── script.js
    └── style.css
```

## Security

- `.env` is ignored by Git.
- API keys are read from environment variables and never sent to the frontend.
- Keep `.env.example` key-free.
- If a real API key was ever exposed publicly, revoke it and create a replacement.

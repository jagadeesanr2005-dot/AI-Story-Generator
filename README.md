<<<<<<< HEAD
# AI Story Generator

A modern, responsive web app that generates unique, never-repeated stories
from a prompt and genre — no AI API key required.

## Features

- 14 genres: Sad, Horror, Romantic, Comedy, Adventure, Fantasy, Mystery,
  Thriller, Angry, Friendship, Family, Science Fiction, Historical, Inspirational
- Short / Medium / Long story lengths
- A new story every time you click Generate — even with the same prompt
  and genre, the procedural engine randomly recombines characters, places,
  weather, plot twists, and endings
- Typewriter reveal animation
- Copy to clipboard, download as `.txt`
- Session history and favorites
- Dark mode / light mode toggle
- Fully responsive, glassmorphism UI

## How story generation works

`story_engine.py` contains hand-written template banks for each genre
(openers, middle beats, twists, endings) plus pools of names, places, and
weather/atmosphere phrases. Each generation request randomly samples from
these pools and stitches them together, so the same prompt and genre will
produce a different combination of characters and events nearly every time.

If you want to add real AI-generated stories instead (using OpenAI or
Gemini), you can swap the body of `generate_story()` in `app.py`'s
`/generate` route to call an external API instead of `story_engine.py` —
the frontend and routes don't need to change.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open your browser to:

```
http://127.0.0.1:5000
```

## Project structure

```
Story_Generator/
├── app.py              # Flask routes
├── story_engine.py      # Procedural story generation logic
├── requirements.txt
├── static/
│   ├── style.css
│   ├── script.js
│   └── images/
├── templates/
│   └── index.html
└── README.md
```

## Notes

- History and favorites are kept in memory in the browser tab (JavaScript
  variables) for the current session — they reset on page reload. If you
  want them to persist across reloads or across devices, that would need
  either browser storage (not recommended for sensitive use) or a backend
  database table, which can be added on request.
- No API key, signup, or internet connection is required to generate
  stories — everything runs locally through the template engine.
=======
# AI-Story-Generator
AI Story Generator built using Python, Flask, HTML, CSS, and JavaScript.
>>>>>>> 3660b608875a8898a484d031cc104e6d8949f943

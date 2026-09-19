"""Fallback story engine used when no AI provider is configured.

It is intentionally prompt-aware and length-aware. The app's preferred path is
an LLM provider (Groq/Gemini), but the fallback keeps the project usable
without an API key or internet connection.
"""

import random
import re

GENRES = {
    "sad": "Sad", "horror": "Horror", "romantic": "Romantic", "comedy": "Comedy",
    "adventure": "Adventure", "fantasy": "Fantasy", "mystery": "Mystery", "thriller": "Thriller",
    "angry": "Angry / Emotional", "friendship": "Friendship", "family": "Family",
    "scifi": "Science Fiction", "historical": "Historical", "inspirational": "Inspirational",
}

LENGTHS = {
    "short": (260, 360),
    "medium": (600, 800),
    "long": (1100, 1400),
}

NAMES = ["Maya", "Daniel", "Aria", "Leo", "Noor", "Ethan", "Zara", "Kabir", "Elena", "Priya", "Jonas", "Amara", "Felix", "Omar", "Lucia", "Marcus", "Yuki", "Aiden"]
PLACES = ["a quiet coastal town", "an abandoned house at the edge of the forest", "a mountain village", "a crowded city street at midnight", "a forgotten railway station", "a lighthouse on a rocky cliff", "a riverside cafe", "an attic full of old photographs", "a snow-covered cabin", "a rooftop above the city"]
ATMOSPHERE = ["as rain tapped against the windows", "under a sky full of stars", "while distant thunder rolled across the sky", "in the pale light before sunrise", "as the last light of evening disappeared"]

GENRE_WORDS = {
    "sad": ("loss", "memory", "goodbye", "hope"),
    "horror": ("shadow", "whisper", "door", "darkness"),
    "romantic": ("heart", "promise", "distance", "love"),
    "comedy": ("mistake", "chaos", "laughter", "surprise"),
    "adventure": ("map", "journey", "danger", "discovery"),
    "fantasy": ("kingdom", "magic", "dragon", "curse"),
    "mystery": ("clue", "letter", "secret", "truth"),
    "thriller": ("chase", "signal", "threat", "escape"),
    "angry": ("betrayal", "rage", "truth", "forgiveness"),
    "friendship": ("trust", "promise", "team", "loyalty"),
    "family": ("home", "family", "memory", "forgiveness"),
    "scifi": ("station", "signal", "planet", "machine"),
    "historical": ("letter", "village", "war", "legacy"),
    "inspirational": ("failure", "courage", "effort", "dream"),
}


def _clean_prompt(prompt: str) -> str:
    prompt = re.sub(r"\s+", " ", prompt.strip())
    return prompt[:300]


def _title(prompt: str, genre: str) -> str:
    words = re.findall(r"[A-Za-z0-9']+", prompt)
    if words:
        seed = " ".join(words[:5]).title()
        return f"{seed}: A {GENRES.get(genre, 'Story')}"
    return f"The {GENRES.get(genre, 'Story')} We Remember"


def generate_story(genre="adventure", length="medium", prompt=""):
    genre = genre if genre in GENRES else "adventure"
    length = length if length in LENGTHS else "medium"
    prompt = _clean_prompt(prompt)
    target_min, target_max = LENGTHS[length]
    name, name2 = random.sample(NAMES, 2)
    place = random.choice(PLACES)
    atmosphere = random.choice(ATMOSPHERE)
    words = GENRE_WORDS[genre]

    opening = (
        f"{name} had carried one thought for years: {prompt}. "
        f"That idea finally pulled {name} toward {place}, {atmosphere}. "
        f"At first it seemed like an ordinary decision, but the feeling of {words[0]} would not leave."
    )
    paragraphs = [opening]

    beats = [
        f"The first clue appeared when {name} met {name2}, who knew more about the situation than they admitted.",
        f"Together they followed a trail of small details, each one connected to the {words[1]} at the center of the story.",
        f"The deeper they went, the more the original plan changed. A problem that looked simple became a choice between fear and courage.",
        f"Then everything turned. What {name} believed about the past was incomplete, and the missing piece was tied to the {words[2]} they had been searching for.",
        f"For one quiet moment, {name} considered walking away. Instead, they remembered why the journey had begun: {prompt}.",
        f"The final confrontation came at {place}. There was no perfect answer, only a decision that would change what happened next.",
        f"{name2} finally told the truth. It was painful, surprising, and strangely freeing.",
        f"By the end, {name} understood that the real meaning of the journey was not the {words[3]} they expected to find, but what they had become while searching for it.",
    ]

    random.shuffle(beats)
    while len(" ".join(paragraphs).split()) < target_min:
        take = beats[len(paragraphs) % len(beats)]
        paragraphs.append(take)
        if len(paragraphs) > 12:
            break

    ending = (
        f"When morning arrived, the world looked almost unchanged. Yet {name} was not. "
        f"They kept the memory of that night close, not as a perfect ending, but as proof that a single idea can begin a completely different life."
    )
    paragraphs.append(ending)

    story = "\n\n".join(paragraphs)
    # Expand deterministically if the fallback is still below the selected minimum.
    while len(story.split()) < target_min:
        story += "\n\n" + random.choice(beats)
    return {
        "title": _title(prompt, genre),
        "story": story,
        "genre": genre,
        "length": length,
        "provider": "local-fallback",
    }

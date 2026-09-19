"""Flask application for the AI Story Generator."""

import os
from flask import Flask, render_template, request, jsonify
from story_engine import GENRES, LENGTHS
from story_generator import generate_story, translate_story

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

VALID_LENGTHS = set(LENGTHS)
MAX_PROMPT_LENGTH = 300

GENRE_LIST = list(GENRES.items())


@app.route("/")
def index():
    return render_template("index.html", genres=GENRE_LIST)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "AI Story Generator"})


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt") or "").strip()
    genre = str(data.get("genre") or "adventure").strip().lower()
    length = str(data.get("length") or "medium").strip().lower()

    if not prompt:
        return jsonify({"error": "Please enter a story idea first."}), 400
    if len(prompt) > MAX_PROMPT_LENGTH:
        return jsonify({"error": f"Please keep your prompt under {MAX_PROMPT_LENGTH} characters."}), 400
    if genre in {"sci-fi", "science fiction"}:
        genre = "scifi"
    if genre not in GENRES:
        return jsonify({"error": "Please select a valid genre."}), 400
    if length not in VALID_LENGTHS:
        return jsonify({"error": "Please select Short, Medium, or Long."}), 400

    try:
        result = generate_story(genre=genre, length=length, prompt=prompt)
        return jsonify({
            "title": result["title"],
            "story": result["story"],
            "genre": result["genre"],
            "length": result["length"],
            "provider": result.get("provider", "unknown"),
            "warning": result.get("warning", ""),
        })
    except Exception as exc:
        app.logger.exception("Story generation failed")
        return jsonify({"error": "Story generation failed. Please try again.", "detail": str(exc)}), 500


@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title") or "Untitled Story").strip()
    story = str(data.get("story") or "").strip()
    language = str(data.get("language") or "").strip().lower()

    languages = {
        "english": "English", "tamil": "Tamil", "malayalam": "Malayalam",
        "hindi": "Hindi", "telugu": "Telugu", "kannada": "Kannada",
    }
    if not story:
        return jsonify({"error": "There is no story to translate."}), 400
    if language not in languages:
        return jsonify({"error": "Please select a supported language."}), 400
    if language == "english":
        return jsonify({"title": title, "story": story, "language": "English", "provider": "original"})

    try:
        result = translate_story(title=title, story=story, language=languages[language])
        return jsonify(result)
    except Exception as exc:
        app.logger.exception("Translation failed")
        return jsonify({"error": str(exc)}), 503


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "False").lower() == "true", host="0.0.0.0", port=int(os.getenv("PORT", "5000")))

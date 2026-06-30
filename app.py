"""
app.py
------
Flask backend for the AI Story Generator.

Routes:
  GET  /            -> renders the main page
  POST /generate     -> accepts {prompt, genre, length} JSON, returns a
                         generated story as JSON

No external AI API key is required. Stories are generated using the
procedural template engine in story_engine.py, which randomly combines
characters, settings, and plot beats so the same prompt/genre can produce
a different story every time.
"""

from flask import Flask, render_template, request, jsonify
from story_engine import generate_story, GENRES

app = Flask(__name__)

VALID_GENRES = set(GENRES.keys()) | {"sci-fi", "science fiction"}
VALID_LENGTHS = {"short", "medium", "long"}


@app.route("/")
def index():
    """Render the homepage."""
    genre_list = [
        ("sad", "Sad"),
        ("horror", "Horror"),
        ("romantic", "Romantic"),
        ("comedy", "Comedy"),
        ("adventure", "Adventure"),
        ("fantasy", "Fantasy"),
        ("mystery", "Mystery"),
        ("thriller", "Thriller"),
        ("angry", "Angry"),
        ("friendship", "Friendship"),
        ("family", "Family"),
        ("scifi", "Science Fiction"),
        ("historical", "Historical"),
        ("inspirational", "Inspirational"),
    ]
    return render_template("index.html", genres=genre_list)


@app.route("/generate", methods=["POST"])
def generate():
    """
    Accepts JSON: { "prompt": str, "genre": str, "length": str }
    Returns JSON: { "title": str, "story": str, "genre": str, "length": str }
    """
    data = request.get_json(silent=True) or {}

    prompt = (data.get("prompt") or "").strip()
    genre = (data.get("genre") or "adventure").strip().lower()
    length = (data.get("length") or "medium").strip().lower()

    if not prompt:
        return jsonify({"error": "Please enter a story prompt."}), 400

    # Normalize a couple of common genre aliases
    if genre in ("sci-fi", "science fiction"):
        genre = "scifi"

    if genre not in GENRES:
        genre = "adventure"

    if length not in VALID_LENGTHS:
        length = "medium"

    result = generate_story(genre=genre, length=length, prompt=prompt)

    return jsonify({
        "title": result["title"],
        "story": result["story"],
        "genre": result["genre"],
        "length": result["length"],
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

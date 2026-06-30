"""
story_engine.py
----------------
Procedural story generator. Builds unique stories by randomly combining
characters, places, emotional beats, plot twists, and endings for each
genre. No external AI API required — every call produces a different
result because selections are randomized each time.
"""

import random

# ---------------------------------------------------------------------------
# Shared word banks used across genres
# ---------------------------------------------------------------------------

NAMES = [
    "Maya", "Daniel", "Aria", "Leo", "Noor", "Ethan", "Zara", "Kabir",
    "Elena", "Samuel", "Priya", "Jonas", "Amara", "Felix", "Ines", "Omar",
    "Lucia", "Marcus", "Yuki", "Aiden"
]

PLACES = [
    "a quiet coastal town", "an old abandoned house at the edge of the forest",
    "a small village in the mountains", "a bustling city street at midnight",
    "a forgotten train station", "a lighthouse on a rocky cliff",
    "a sleepy countryside farm", "a crowded marketplace in winter",
    "a hospital corridor", "an attic full of old photographs",
    "a riverside cafe", "a school playground after hours",
    "a desert highway", "a snowed-in cabin", "a rooftop overlooking the city"
]

WEATHER = [
    "under a heavy grey sky", "as rain tapped gently on the windows",
    "while the wind howled outside", "beneath a blanket of falling snow",
    "as the last light of sunset faded", "in the stillness of early morning fog",
    "while thunder rumbled in the distance", "under a sky full of stars"
]

# ---------------------------------------------------------------------------
# Genre-specific building blocks
# Each genre has: openers, middles, twists, endings
# Templates use {name}, {name2}, {place}, {weather} placeholders
# ---------------------------------------------------------------------------

GENRES = {
    "sad": {
        "openers": [
            "{name} waited every evening at {place}, holding onto a promise that was never kept.",
            "{weather}, {name} sat alone in {place}, remembering a voice that had gone quiet.",
            "{name} had not spoken a word since the day {name2} disappeared from {place}.",
        ],
        "middles": [
            "Every letter {name} wrote was never sent, kept instead in a small wooden box under the bed.",
            "Years passed, but {name} still set two cups of tea each morning out of habit.",
            "Even the old songs they once sang together now felt too heavy to hum.",
        ],
        "twists": [
            "One day, a stranger arrived carrying {name2}'s old coat, and {name} finally understood the truth.",
            "A letter long lost in the mail finally arrived — written by {name2}, years too late.",
            "{name} found an old photograph hidden behind a frame, and the grief returned all at once.",
        ],
        "endings": [
            "{name} smiled through the tears, finally able to say goodbye.",
            "The ache never fully left, but {name} learned to carry it gently.",
            "{name} placed a single flower at {place} and walked away, lighter than before.",
        ],
    },
    "horror": {
        "openers": [
            "{name} should never have stepped into {place} {weather}.",
            "The lights flickered the moment {name} entered {place}, and a cold breath followed.",
            "{name} heard the whisper first — faint, almost gentle — coming from inside {place}.",
        ],
        "middles": [
            "Footsteps echoed behind {name}, but every time they turned, nothing was there.",
            "The walls of {place} seemed to breathe, shifting slightly whenever {name} looked away.",
            "A child's laughter drifted from an empty room, growing closer with each passing minute.",
        ],
        "twists": [
            "{name} realized the reflection in the mirror was no longer moving in sync.",
            "The door {name} had locked behind them was now standing wide open.",
            "{name2}, who had vanished years ago, was standing silently at the end of the hall.",
        ],
        "endings": [
            "{name} ran, but {place} had already changed the way out.",
            "By morning, {name} was gone — only a faint whisper remained in {place}.",
            "{name} escaped, but something followed them home that night, and never quite left.",
        ],
    },
    "romantic": {
        "openers": [
            "{name} first noticed {name2} {weather}, sitting quietly in {place}.",
            "It began with a spilled coffee and an apology, in {place} {weather}.",
            "{name} never believed in fate until {name2} sat beside them in {place}.",
        ],
        "middles": [
            "Their conversations stretched late into the night, full of laughter and quiet confessions.",
            "{name} found themselves returning to {place} again and again, hoping to see {name2}.",
            "A simple walk turned into hours, and hours turned into something neither wanted to end.",
        ],
        "twists": [
            "Just as their feelings deepened, {name2} announced they were moving far away.",
            "{name} discovered a secret {name2} had been keeping, and everything suddenly made sense.",
            "An old rival reappeared, threatening to pull {name} and {name2} apart.",
        ],
        "endings": [
            "{name} and {name2} chose each other, distance and doubts aside.",
            "Standing in {place}, {name} finally said the words {name2} had been waiting to hear.",
            "Their story was far from perfect, but it was unmistakably theirs.",
        ],
    },
    "comedy": {
        "openers": [
            "{name} had one simple task in {place}, and somehow turned it into complete chaos.",
            "It all started when {name} mistook {name2}'s coffee for their own {weather}.",
            "Nobody warned {name} that {place} on a Monday was basically a circus.",
        ],
        "middles": [
            "Things spiraled further when {name2} tried to help and accidentally made everything worse.",
            "A runaway shopping cart, a very confused goat, and {name} somehow ended up in the middle of it all.",
            "{name} attempted to act casual, which only made the entire situation more suspicious.",
        ],
        "twists": [
            "Just when {name} thought it couldn't get worse, the mayor walked in.",
            "{name2} revealed they had filmed the entire thing, and it was already trending online.",
            "The 'emergency' turned out to be a very dramatic squirrel.",
        ],
        "endings": [
            "{name} and {name2} couldn't stop laughing about it for weeks.",
            "In the end, {place} had never seen anything quite like it — and probably never would again.",
            "{name} learned an important lesson: never trust a Monday.",
        ],
    },
    "adventure": {
        "openers": [
            "{name} packed only a worn map and a flask of water before setting off toward {place}.",
            "The journey began {weather}, with {name} chasing a legend few believed was real.",
            "{name} and {name2} had one chance to reach {place} before the path closed forever.",
        ],
        "middles": [
            "The trail grew treacherous, but {name} pressed on, driven by something stronger than fear.",
            "A sudden storm forced {name} and {name2} to find shelter deep within {place}.",
            "Every step revealed new dangers, but also clues to a mystery older than either of them.",
        ],
        "twists": [
            "The map {name} trusted turned out to be leading somewhere entirely different.",
            "{name2} was not who they claimed to be, and the truth changed everything.",
            "{name} discovered the legend was real — and it had been waiting for them all along.",
        ],
        "endings": [
            "{name} stood at last at {place}, forever changed by the journey.",
            "{name} and {name2} returned home as different people than the ones who had left.",
            "The adventure ended, but {name} already knew it wasn't truly over.",
        ],
    },
    "fantasy": {
        "openers": [
            "In {place}, where the old magic still lingered, {name} discovered a power they never asked for.",
            "{weather}, a door appeared where none had stood before, and {name} stepped through it.",
            "{name} was the last of a forgotten bloodline, though no one in {place} knew it yet.",
        ],
        "middles": [
            "Ancient symbols glowed faintly whenever {name} drew near, awakening something long dormant.",
            "{name2}, a guardian sworn to silence, finally revealed the truth about {place}.",
            "The deeper {name} ventured, the more the boundary between worlds seemed to blur.",
        ],
        "twists": [
            "The kingdom {name} sought to save had been gone for a thousand years — or so they thought.",
            "{name2} was bound by an ancient curse, and only {name} could break it.",
            "The power {name} carried was never a gift — it was a warning.",
        ],
        "endings": [
            "{name} chose to stay, becoming the new guardian of {place}.",
            "The magic faded, but {name} carried its memory forever.",
            "{name} and {name2} closed the door behind them, and the old world finally rested.",
        ],
    },
    "mystery": {
        "openers": [
            "No one had entered {place} in years, until {name} found the door unlocked {weather}.",
            "The case seemed simple at first — until {name} found {name2}'s name in the file.",
            "{name} had one clue, one name, and one chance to uncover the truth behind {place}.",
        ],
        "middles": [
            "Every answer {name} found only led to three more questions.",
            "{name2} kept changing their story, and {name} began to wonder who else was lying.",
            "A hidden room in {place} held evidence that changed the entire investigation.",
        ],
        "twists": [
            "The person {name} trusted most had been there from the very beginning.",
            "{name2} had staged the entire disappearance themselves.",
            "The real culprit had been hiding in plain sight at {place} all along.",
        ],
        "endings": [
            "{name} finally closed the case, though some questions would never be answered.",
            "The truth was darker than {name} expected, but justice was served.",
            "{name} walked away from {place}, certain the mystery wasn't fully over.",
        ],
    },
    "thriller": {
        "openers": [
            "{name} had exactly one hour to escape {place} before everything fell apart.",
            "The phone rang once, then went silent — {name} knew {name2} was in danger.",
            "{weather}, {name} realized they were being watched from somewhere inside {place}.",
        ],
        "middles": [
            "Every move {name} made seemed to be anticipated, as if someone already knew the plan.",
            "{name2} appeared out of nowhere, claiming to be the only one who could help.",
            "The deeper {name} dug, the more dangerous the people around them seemed.",
        ],
        "twists": [
            "{name2} had been working against {name} from the very start.",
            "The danger wasn't coming from outside {place} — it was already inside.",
            "{name} realized too late that the trap had been set days ago.",
        ],
        "endings": [
            "{name} barely escaped {place}, but the danger was far from over.",
            "In the end, {name} trusted no one — and survived because of it.",
            "{name} walked away alive, but nothing would ever feel safe again.",
        ],
    },
    "angry": {
        "openers": [
            "{name} slammed the door of {place}, fists clenched, unable to hold back any longer.",
            "Years of silence finally broke when {name} confronted {name2} {weather}.",
            "{name} had warned them once. {weather}, the warning ran out.",
        ],
        "middles": [
            "Every word {name2} spoke only fed the fire building inside {name}.",
            "The unfairness of it all became too much for {name} to carry quietly any longer.",
            "{name} replayed every broken promise, and the anger only grew sharper.",
        ],
        "twists": [
            "{name} discovered {name2} had been lying the entire time, and the betrayal cut deeper than expected.",
            "Just as {name} prepared to walk away for good, the real reason behind it all came to light.",
            "The anger {name} carried had been protecting a much deeper hurt.",
        ],
        "endings": [
            "{name} finally said everything they had been holding back, and felt the weight lift.",
            "{name} walked away from {place}, choosing peace over the fight.",
            "The anger faded into something quieter — not forgiveness yet, but a start.",
        ],
    },
    "friendship": {
        "openers": [
            "{name} and {name2} had been inseparable since the day they met at {place}.",
            "It was {name2} who found {name} sitting alone at {place}, and nothing was the same after that.",
            "{weather}, {name} and {name2} made a promise neither ever forgot.",
        ],
        "middles": [
            "Through every hard season, {name2} was the one constant {name} could count on.",
            "They argued, they laughed, they grew — but {place} always brought them back together.",
            "{name} realized that {name2} had been quietly carrying them through more than they knew.",
        ],
        "twists": [
            "Distance and time tried to pull {name} and {name2} apart, but never quite succeeded.",
            "A misunderstanding nearly ended everything, until the truth finally came out.",
            "{name} learned that {name2} had been struggling in silence the whole time.",
        ],
        "endings": [
            "{name} and {name2} returned to {place}, older now, but just as close as ever.",
            "No matter how far apart they grew, {name} always knew {name2} was one call away.",
            "Some friendships fade. Theirs only grew stronger.",
        ],
    },
    "family": {
        "openers": [
            "{name} returned to {place} after years away, unsure of the welcome that awaited.",
            "{weather}, the whole family gathered at {place} for the first time in a long while.",
            "{name} found an old letter from {name2} tucked inside a drawer at {place}.",
        ],
        "middles": [
            "Old arguments resurfaced, but so did old memories neither had truly forgotten.",
            "{name} began to understand {name2}'s choices from years ago in a new light.",
            "Around the dinner table, silence slowly gave way to honest conversation.",
        ],
        "twists": [
            "{name} discovered a family secret that reshaped everything they thought they knew.",
            "{name2} finally admitted the truth they had carried alone for years.",
            "A health scare brought the family back to {place}, faster than anyone expected.",
        ],
        "endings": [
            "{name} and {name2} hugged for the first time in years, nothing left unsaid.",
            "{place} felt like home again, in a way it hadn't in a long time.",
            "Family, {name} realized, wasn't about being perfect — it was about staying.",
        ],
    },
    "scifi": {
        "openers": [
            "{name} woke up in {place}, though the stars outside the window belonged to no sky they knew.",
            "The signal had been silent for years, until it suddenly returned from {place}.",
            "{name} was the last crew member aboard the station orbiting above {place}.",
        ],
        "middles": [
            "The AI guiding {name} began behaving strangely, as if it were hiding something.",
            "{name2} warned {name} that the mission briefing had left out something important.",
            "Every system check revealed more anomalies than answers.",
        ],
        "twists": [
            "{name} discovered the mission had happened before — many times, in fact.",
            "{name2} was not human, and had been guiding {name} toward something far larger.",
            "The signal wasn't coming from outside {place}. It was coming from within {name}.",
        ],
        "endings": [
            "{name} made the choice that would alter the timeline forever.",
            "{place} disappeared behind them as {name} set a course for the unknown.",
            "{name} finally understood: this had never been an ending, only a beginning.",
        ],
    },
    "historical": {
        "openers": [
            "In the years before the war reached {place}, {name} still believed peace would hold.",
            "{weather}, {name} watched the old world begin to change forever at {place}.",
            "{name} kept a journal through it all, starting the day soldiers first marched through {place}.",
        ],
        "middles": [
            "Letters from {name2} grew further apart, and each one carried more worry than the last.",
            "{name} made choices that would echo far beyond their own lifetime.",
            "Rationing, fear, and quiet courage became the rhythm of daily life at {place}.",
        ],
        "twists": [
            "{name} learned {name2} had been part of the resistance the entire time.",
            "A decision made in secret at {place} would change the course of the years that followed.",
            "The war ended, but {name} realized nothing would ever return to how it was.",
        ],
        "endings": [
            "{name} stood once more at {place}, now rebuilt, carrying the weight of all that had passed.",
            "Decades later, {name}'s journal was found — a quiet record of an extraordinary time.",
            "{name} survived, and chose to remember rather than forget.",
        ],
    },
    "inspirational": {
        "openers": [
            "{name} had failed more times than they could count before finally arriving at {place}.",
            "Everyone told {name} it was impossible — everyone except {name2}.",
            "{weather}, {name} made a decision that would change the rest of their life.",
        ],
        "middles": [
            "Every setback taught {name} something the easy path never could have.",
            "{name2}'s belief in {name} never wavered, even when {name}'s own did.",
            "Slowly, step by step, {name} rebuilt what once felt impossible to recover.",
        ],
        "twists": [
            "Just before giving up, {name} received the one piece of encouragement they needed most.",
            "{name} realized the obstacle had been teaching them the very lesson they needed.",
            "The opportunity {name} had been chasing finally arrived — disguised as a setback.",
        ],
        "endings": [
            "{name} stood at {place}, proof that persistence had finally paid off.",
            "{name} looked back at how far they'd come, and felt nothing but gratitude.",
            "{name}'s story became the encouragement {name2} needed to chase their own dream.",
        ],
    },
}

LENGTH_PARAGRAPHS = {
    "short": 2,
    "medium": 3,
    "long": 5,
}

TITLE_PREFIXES = [
    "The Story of", "A Tale of", "Whispers of", "The Day of",
    "Echoes of", "The Memory of", "Beneath", "The Last",
]


def _pick_two_names():
    a, b = random.sample(NAMES, 2)
    return a, b


def _fill(template, name, name2, place, weather):
    text = template.format(name=name, name2=name2, place=place, weather=weather)
    # Ensure the paragraph always starts with a capital letter, even when a
    # template begins with a lowercase placeholder like {weather} or {place}.
    if text:
        text = text[0].upper() + text[1:]
    return text


def generate_title(genre, name):
    prefix = random.choice(TITLE_PREFIXES)
    return f"{prefix} {name}"


def generate_story(genre: str, length: str = "medium", prompt: str = "") -> dict:
    """
    Generate a unique story for the given genre and length.
    Returns a dict with 'title' and 'story' (full text) and 'paragraphs'.
    """
    genre = genre.lower().strip()
    if genre not in GENRES:
        genre = "adventure"  # safe fallback

    bank = GENRES[genre]
    name, name2 = _pick_two_names()
    place = random.choice(PLACES)
    weather = random.choice(WEATHER)

    opener = _fill(random.choice(bank["openers"]), name, name2, place, weather)
    twist = _fill(random.choice(bank["twists"]), name, name2, place, weather)
    ending = _fill(random.choice(bank["endings"]), name, name2, place, weather)

    # How many distinct "middle" beats to use per length, each pulled from
    # the genre's middle bank without repeats so paragraphs never duplicate.
    # short: no middle beats at all (just opener -> twist -> ending)
    # medium: 1 middle beat
    # long: all available middle beats (currently 3 per genre)
    middle_target = {"short": 0, "medium": 1, "long": len(bank["middles"])}
    middle_count = min(middle_target.get(length, 1), len(bank["middles"]))

    middles = random.sample(bank["middles"], k=middle_count)
    middles = [_fill(m, name, name2, place, weather) for m in middles]

    paragraphs = [opener] + middles + [twist, ending]

    title = generate_title(genre, name)
    story_text = "\n\n".join(paragraphs)

    return {
        "title": title,
        "story": story_text,
        "paragraphs": paragraphs,
        "genre": genre,
        "length": length,
    }

import json
import os
import re
from typing import Dict, Set

# Path to the JSON file containing banned words
_BANNED_PATH = os.path.join(os.path.dirname(__file__), "banned_words.json")


def _load_banned_words() -> Set[str]:
    """Load the set of banned words from the JSON file."""
    try:
        with open(_BANNED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {w.lower() for w in data}
    except FileNotFoundError:
        return set()


_BANNED: Set[str] = _load_banned_words()

# Example synonym replacements. Only a small subset is provided; callers can
# supply their own mapping for more comprehensive coverage.
_DEFAULT_REPLACEMENTS: Dict[str, str] = {
    "shadows": "darkness",
    "ancient": "age-old",
    "harmony": "balance",
    "heartbeat": "pulse",
}


def sanitize_lyrics(text: str, replacements: Dict[str, str] | None = None) -> str:
    """Replace banned words in ``text`` using synonyms.

    Parameters
    ----------
    text:
        The input string to sanitize.
    replacements:
        Optional mapping of banned words to their allowed synonyms. The mapping
        is case-insensitive.
    """
    reps = {k.lower(): v for k, v in (replacements or _DEFAULT_REPLACEMENTS).items()}
    if not _BANNED:
        return text
    pattern = re.compile(r"\b(" + "|".join(map(re.escape, _BANNED)) + r")\b", re.IGNORECASE)

    def _sub(match: re.Match) -> str:
        word = match.group(0)
        return reps.get(word.lower(), "")

    return pattern.sub(_sub, text)


def generate_lyrics(idea: str) -> str:
    """Generate a small, structured lyric from a user idea.

    The function applies :func:`sanitize_lyrics` to both the incoming idea and
    the final result so that banned words from ``banned_words.json`` are
    filtered consistently.
    """

    idea_clean = sanitize_lyrics(idea or "").strip()
    if not idea_clean:
        idea_clean = "love"

    def line(txt: str) -> str:
        return sanitize_lyrics(txt)

    verse1 = [
        line(f"{idea_clean} found me at dawn's first light,"),
        line("It traced my days and steered them right,"),
        line("Across old roads where memories play,"),
        line("Each step a verse along the way."),
    ]

    chorus = [
        line(f"Hold the {idea_clean} close tonight,"),
        line("Let it set the stars alight,"),
        line("Through every wind and pouring rain,"),
        line("The heart repeats that one old line."),
    ]

    verse2 = [
        line("Years may flow but feelings stay,"),
        line("In quiet corners they find their way,"),
        line("From distant hills to open sea,"),
        line(f"Your {idea_clean} truth still shelters me."),
    ]

    bridge = [
        line("If night grows cold and hopes seem far,"),
        line(f"Your {idea_clean} spark becomes my star."),
    ]

    parts = [
        "Verse 1:", *verse1, "",
        "Chorus:", *chorus, "",
        "Verse 2:", *verse2, "",
        "Bridge:", *bridge, "",
        "Chorus:", *chorus,
    ]

    final = "\n".join(parts)
    return sanitize_lyrics(final)


__all__ = ["sanitize_lyrics", "generate_lyrics"]

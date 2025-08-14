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


__all__ = ["sanitize_lyrics"]

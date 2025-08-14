import os
import sys

# Ensure the project root is importable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lyrics import sanitize_lyrics


def test_sanitize_replaces_banned_words():
    text = "shadows and Ancient harmony heartbeat"
    result = sanitize_lyrics(text)
    out = result.lower()
    assert "shadows" not in out
    assert "ancient" not in out
    assert "harmony" not in out
    assert "heartbeat" not in out
    assert "darkness" in out
    assert "age-old" in out
    assert "balance" in out
    assert "pulse" in out

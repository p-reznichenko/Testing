import os
import sys
import pytest

# Ensure the project root is importable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lyrics import sanitize_lyrics, generate_lyrics


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


def test_generate_lyrics_sanitizes_and_structures():
    res = generate_lyrics("ancient harmony")
    low = res.lower()
    assert "ancient" not in low
    assert "harmony" not in low
    assert "Verse 1:" in res
    assert "Chorus:" in res


def test_lyrics_endpoint_returns_json():
    pytest.importorskip("flask")
    from module1_patched import app
    client = app.test_client()
    resp = client.post("/lyrics", json={"idea": "ancient harmony"})
    assert resp.status_code == 200
    data = resp.get_json()
    low = data["lyrics"].lower()
    assert "ancient" not in low
    assert "harmony" not in low

def test_sanitize_leaves_clean_text_unchanged():
    clean = "plain words"
    assert sanitize_lyrics(clean) == clean

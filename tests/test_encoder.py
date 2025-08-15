import os
import sys

# Ensure project root is importable
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from encoder import encode_string, ZW_SEQUENCE, _glitch_tag


def test_encode_string_inserts_zero_width_and_glitch_tag():
    seed = "hello"
    encoded = encode_string(seed)
    assert encoded.startswith("hel" + ZW_SEQUENCE + "lo")
    assert encoded.endswith(f" {ZW_SEQUENCE}[{_glitch_tag(seed)}]")


def test_encode_string_deterministic_and_joiner():
    text = "alpha, beta"
    encoded1 = encode_string(text)
    encoded2 = encode_string(text)
    assert encoded1 == encoded2
    assert f",{ZW_SEQUENCE} " in encoded1

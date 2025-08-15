"""Utility to obfuscate strings with zero-width characters and glitch tags."""
from __future__ import annotations

import argparse
import hashlib
import math

ZW_SEQUENCE = "\u200e\u200d\ufeff\u200c\u200d\ufeff"

_PREFIXES = [
    "flicker",
    "v0id",
    "gl1tch",
    "fray",
    "static",
    "ghost",
    "pulse",
]
_SUFFIXES = [
    "mirror",
    "sync",
    "halo",
    "lullaby",
    "crown",
    "loop",
    "m0saic",
]
_SYMBOLS = ["/\u221e", "\u2260", "\u2e2e", "/\u29d6", "~", "\u00b0", "/"]


def _glitch_tag(seed: str) -> str:
    """Return a deterministic glitch tag based on *seed*.

    The tag is a combination of a prefix, suffix and symbol pulled from the
    lists above. Using a hash of *seed* keeps the transformation stable for the
    same input while still appearing random.
    """
    idx = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16)
    idx %= len(_PREFIXES)
    return f"{_PREFIXES[idx]}.{_SUFFIXES[idx]}{_SYMBOLS[idx]}"


def encode_string(input_str: str) -> str:
    """Encode *input_str* using zero-width characters and glitch tags.

    Each comma separated token is transformed by inserting a sequence of
    zero-width characters into the first word and appending a bracketed glitch
    tag. Tokens are then joined using commas that also carry the zero-width
    sequence. This mirrors the obfuscation described in ``encoder.md``.
    """

    parts = [part.strip() for part in input_str.split(",") if part.strip()]
    encoded_parts = []
    for part in parts:
        words = part.split()
        if words:
            first = words[0]
            split_idx = math.ceil(len(first) / 2)
            first = first[:split_idx] + ZW_SEQUENCE + first[split_idx:]
            words[0] = first
        encoded = " ".join(words) + f" {ZW_SEQUENCE}[{_glitch_tag(part)}]"
        encoded_parts.append(encoded)

    joiner = f",{ZW_SEQUENCE} "
    return joiner.join(encoded_parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Encode a string with hidden glyphs.")
    parser.add_argument("text", help="text to encode")
    args = parser.parse_args()
    print(encode_string(args.text))


if __name__ == "__main__":
    main()

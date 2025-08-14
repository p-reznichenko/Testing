import json, os, random, re
from collections import Counter
from typing import List, Dict, Tuple

DATA_PATH = os.path.join(os.path.dirname(__file__), "unified-suno-weights-expanded.json")

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        J = json.load(f)
        DEFAULTS = J.get("default_styles", []) or []
        CO = J.get("co_existing_styles_dict", {}) or {}
except Exception:
    DEFAULTS = ["rock", "pop", "jazz", "ambient"]
    CO = {}

# map for quick normalization
_CANON_MAP = {s.lower(): s for s in DEFAULTS}

def _edit_distance(a: str, b: str) -> int:
    """Simple Levenshtein distance for small strings."""
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            cur = dp[j]
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[j] = min(prev + cost, dp[j] + 1, dp[j - 1] + 1)
            prev = cur
    return dp[n]

class StyleBuilder:
    """Implements the style building pipeline from Style_Builder.md."""

    def __init__(self, defaults: List[str] = None, co: Dict[str, Dict[str, float]] = None):
        self.defaults = defaults or DEFAULTS
        self.co = co or CO
        self.canon_map = {s.lower(): s for s in self.defaults}

    # --- normalization ---
    def normalize(self, tag: str) -> str:
        t = tag.strip()
        low = t.lower()
        if low in self.canon_map:
            return self.canon_map[low]
        best = None
        best_d = 2  # edit distance threshold 1
        for s in self.defaults:
            d = _edit_distance(low, s.lower())
            if d < best_d:
                best_d = d
                best = s
                if d == 0:
                    break
        if best is not None and best_d <= 1:
            return best
        return t

    # --- augmentation ---
    def augment(self, canon: List[str]) -> List[Dict[str, object]]:
        adds: List[Dict[str, object]] = []
        for T in canon:
            neigh = self.co.get(T, {})
            if not isinstance(neigh, dict):
                continue
            items = sorted(neigh.items(), key=lambda kv: kv[1], reverse=True)[:3]
            for S, w in items:
                if S not in canon and all(a["tag"] != S for a in adds):
                    adds.append({"tag": S, "from": T, "weight": w})
                    if len(adds) >= 6:
                        return adds
        return adds

    # --- conflict resolution (simplified) ---
    def resolve(self, canon: List[str], adds: List[Dict[str, object]], constraints: List[str]) -> List[str]:
        target = list(canon)
        for a in adds:
            tag = a["tag"]
            if tag not in target and tag not in constraints:
                target.append(tag)
        return target

    # --- negative steering ---
    def gravity_map(self, target: List[str]) -> Counter:
        g = Counter()
        for t in target:
            for s, w in self.co.get(t, {}).items():
                if s not in target:
                    g[s] += w
        return g

    def mismatch_penalty(self, style: str, target: List[str]) -> float:
        low = style.lower()
        if any("metal" in t.lower() for t in target) and "ambient" in low:
            return 2.0
        if any("ambient" in t.lower() for t in target) and "metal" in low:
            return 2.0
        return 1.0

    def choose_excludes(self, target: List[str], constraints: List[str]) -> List[str]:
        g = self.gravity_map(target)
        cand = g.most_common(12)
        scored: List[Tuple[str, float]] = []
        for s, w in cand:
            risk = w * self.mismatch_penalty(s, target)
            if s in constraints:
                risk *= 5
            scored.append((s, risk))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:6]]

    # --- description generation ---
    def describe(self, target: List[str], constraints: List[str]) -> str:
        if not target:
            return ""
        random.seed(0)
        spatial = ["lush", "cavernous", "immersive", "atmospheric", "distant", "washed in reverb", "enveloped", "echoing", "spectral"]
        timbre = ["saturated", "rich", "resonant", "warped", "warbling", "abrasive", "granular", "shimmering", "hazy", "dense"]
        mood = ["brooding", "hypnotic", "melancholic", "triumphant", "nostalgic", "haunting", "unsettling", "compulsive", "stately", "ancient"]
        progression = ["builds", "drifts", "punctuates", "swells", "ebbs", "evolves", "retreats"]
        tag1 = target[0]
        tag2 = target[1] if len(target) > 1 else target[0]
        tag3 = target[2] if len(target) > 2 else target[0]
        s1 = f"{random.choice(spatial)}, {random.choice(spatial)} {tag1} with {random.choice(timbre)} textures opens a {random.choice(mood)} atmosphere."
        s2 = f"Supporting layers of {tag2} and {tag3} {random.choice(progression)} through the mix."
        s3 = f"Contrasts emerge as elements {random.choice(progression)} against each other."
        s4 = f"The piece resolves with {random.choice(mood)} afterglow."
        return " ".join([s1, s2, s3, s4])

    # --- full build ---
    def build(self, user_input: str) -> Tuple[str, List[str]]:
        tokens = [t.strip() for t in re.split(r",|\n", user_input) if t.strip()]
        constraints = [t[3:].strip() for t in tokens if t.lower().startswith("no ")]
        tags = [t for t in tokens if not t.lower().startswith("no ")]
        canon = [self.normalize(t) for t in tags]
        adds = self.augment(canon)
        target = self.resolve(canon, adds, constraints)
        excludes = self.choose_excludes(target, constraints)
        description = self.describe(target, constraints)
        return description, excludes

_default_builder = StyleBuilder()

def build_style_prompt(user_input: str) -> Tuple[str, List[str]]:
    """Convenience wrapper around the default builder."""
    return _default_builder.build(user_input)

__all__ = [
    "StyleBuilder",
    "build_style_prompt",
]

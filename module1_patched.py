#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suno Full Generator — All‑in‑One (OFFLINE)
Запуск:
    pip install flask
    python suno_full_generator.py
Открой в браузере: http://127.0.0.1:5000
"""

from flask import Flask, request, render_template, send_file, Response
import io, json, random, datetime
import traceback
from style_builder import build_style_prompt as run_style_builder

app = Flask(__name__, static_folder="static")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["ENV"] = "development"
app.config["DEBUG"] = True  # включаем подробные ошибки

# ------------------------------
# Embedded mini datasets (offline)
# ------------------------------

CORE_EMOTIONS = [
    "melancholic","uplifting","haunting","aggressive","romantic",
    "mysterious","playful","epic","introspective","joyful"
]

# Emotion → (vocal styles, genres)
EMOTION_MAP = {
    "melancholic": (["breathy female vocals","soft male vocals","ethereal contralto"], ["ambient","neoclassical","post-rock"]),
    "uplifting": (["powerful soprano","soulful tenor","gospel choir"], ["soul","gospel","anthemic rock"]),
    "haunting": (["ethereal female vocals","low chanting","echoed soprano"], ["dark ambient","world fusion","cinematic"]),
    "aggressive": (["raspy rock vocals","metal growl","gritty male vocals"], ["metal","industrial","punk"]),
    "romantic": (["smooth crooner","soft jazz vocals","warm alto"], ["jazz","bossa nova","soul"]),
    "mysterious": (["whispered female vocals","low male chant","ethereal soprano"], ["ambient","downtempo","world fusion"]),
    "playful": (["quirky female vocals","light male vocals","scat singing"], ["swing","electro-swing","funk"]),
    "epic": (["operatic soprano","baritone choir","epic tenor"], ["epic orchestral","symphonic metal","cinematic"]),
    "introspective": (["fragile female vocals","spoken word","soft falsetto"], ["indie folk","acoustic","minimalist"]),
    "joyful": (["gospel choir","upbeat pop vocals","soulful alto"], ["soul","funk","gospel"])
}

# World Atlas (short)
WORLD_REGIONS = {
    "Mongolia / Tuva": ["throat singing","khoomii","overtone singing"],
    "Bulgaria / Eastern Europe": ["bulgarian choir","open throat singing","balkan folk"],
    "India / South Asia": ["hindustani","carnatic","bollywood vocals"],
    "Middle East / North Africa": ["maqam","arabic chant","muezzin style"],
    "Nordic / Arctic": ["joik","kulning"],
    "Latin America": ["flamenco cante","tango vocals","bossa nova vocals"]
}

# Instruments (short)
INSTRUMENT_TAGS = [
    "acoustic guitar","electric guitar","grand piano","upright bass","drum kit","frame drum",
    "violin","cello","harp","flute","sitar","tabla","duduk","bansuri","oud","qanun","erhu",
    "shakuhachi","organ","analog synth pads","modular synth","taiko drums"
]

ERAS = ["1920s","1940s","1960s","1980s","modern","future"]

# High‑gravity conflicting pairs (short demo list)
HIGH_CONFLICTS = [
    ("operatic soprano","lofi whisper"),
    ("metal growl","smooth crooner"),
    ("gospel choir","low male chant"),
    ("raspy rock vocals","ethereal soprano")
]

# Song impact tags (summarized)
SONG_IMPACT_TAGS = {
    "vocal_emotion":[
        "[BREATHY INTIMACY]","[PASSIONATE BELT]","[TEARFUL DELIVERY]","[SMILING TONE]",
        "[RAW EMOTIONAL EDGE]","[HAUNTED VOCAL PRESENCE]","[CONFIDENT STAGE DELIVERY]",
        "[WHISPERED SECRECY]","[ANGUISHED CRY]","[VULNERABLE TONE]","[TRIUMPHANT LIFT]"
    ],
    "pronunciation":[
        "[PRECISION DICTION]","[SOFT CONSONANT EDGE]","[ROLLED R’S]","[BREATH-DRIVEN PHRASES]",
        "[SUSTAINED VOWELS]","[CRISP CONSONANTS]","[SLURRED DELIVERY]","[NASAL RESONANCE]",
        "[OPEN VOWEL SPACE]","[FORWARD PLACEMENT]","[RETRO ACCENT INFLECTION]"
    ],
    "instrument_interaction":[
        "[VOCAL-INSTRUMENT CALL AND RESPONSE]","[VOCALS INTERWEAVE WITH STRINGS]",
        "[VOCALS FLOAT ABOVE PERCUSSION]","[PIANO AND VOCAL IN SYNC]",
        "[SOLO INSTRUMENT MIRRORS VOCAL]","[GUITAR HARMONIZES VOCAL]",
        "[VOCALS RIDE THE BASS GROOVE]","[VOCAL-INSTRUMENT SWELL MATCH]",
        "[ORCHESTRAL SWELL SUPPORTS VOCAL]","[SPARSE INSTRUMENTATION FOR VOCAL SPACE]"
    ],
    "mix_engineering":[
        "[CLEAR LEAD VOCAL]","[CLARITY IN VOCAL BREATHS]","[VOCALS CUT THROUGH MIX]","[SOFT VOCAL PRESENCE]",
        "[EMOTIONAL RESONANCE FOCUSED]","[WARM VINTAGE VOCAL TONE]","[ETHEREAL VOCAL GLOW]","[OPERATIC POWER]","[RAW RASPY TEXTURE]",
        "[CINEMATIC SPATIAL MIX]","[DYNAMIC RANGE PRESERVED]","[DYNAMIC CRESTS MAINTAINED]","[PRECISE ENERGY TRANSLATION]",
        "[WIDE STEREO FIELD]","[CENTERED LEAD VOCAL]","[HYPER-REAL REVERB]","[ANALOG WARMTH]","[CRISP HIGH-END]","[RICH LOW-END PRESERVED]",
        "[ORCHESTRAL DEPTH]","[LAYERED HARMONIES]","[SPARSE ARRANGEMENT]","[INSTRUMENTS BLEND NATURALLY]","[PERCUSSIVE EMPHASIS]",
        "[STRINGS LUSH AND FULL]","[SYNTH TEXTURE RICH]","[WORLD INSTRUMENT DETAIL]","[HAUNTING AMBIENCE]","[MELANCHOLIC WARMTH]",
        "[EPIC EMOTIONAL SWELL]","[JOYFUL ENERGY FLOW]","[MYSTICAL SPACE]","[ROMANTIC INTIMACY]","[DARK CINEMATIC TENSION]"
    ]
}

# Sound effects & combos
SFX = {
    "Natural":["[OCEAN WAVES]","[RAIN ON ROOF]","[FOREST AMBIENCE]","[WIND WHISTLE]","[BIRDSONG]","[THUNDER RUMBLE]"],
    "Atmospheric":["[TAPE HISS]","[VINYL CRACKLE]","[ANALOG NOISE]","[REVERSED REVERB]","[CINEMATIC RISE]","[LOW DRONE]"],
    "Electronic":["[WHITE NOISE WASH]","[LASER SWEEP]","[MODULAR SYNTH PULSES]","[BITCRUSHED TEXTURE]"],
    "Textural":["[SAND MOVEMENT]","[GLASS SHIMMER]","[METALLIC CLANG]","[FOOTSTEPS IN HALL]"]
}
SFX_COMBOS = {
    "Ambient/Chillout":[["[OCEAN WAVES]","[VINYL CRACKLE]"],["[RAIN ON ROOF]","[LOW DRONE]"],["[FOREST AMBIENCE]","[BIRDSONG]"]],
    "Cinematic/Epic":[["[THUNDER RUMBLE]","[CINEMATIC RISE]"],["[LOW DRONE]","[REVERSED REVERB]"],["[METALLIC CLANG]","[FOOTSTEPS IN HALL]"]],
    "Electronic/Glitch":[["[WHITE NOISE WASH]","[BITCRUSHED TEXTURE]"],["[LASER SWEEP]","[MODULAR SYNTH PULSES]"],["[REVERSED REVERB]","[TAPE HISS]"]],
    "Folk/World":[["[SAND MOVEMENT]","[FOREST AMBIENCE]"],["[OCEAN WAVES]","[GLASS SHIMMER]"],["[BIRDSONG]","[VINYL CRACKLE]"]]
}

# Emotion Compatibility (0..1)
EMOTION_COMPAT = {
    "melancholic":{"melancholic":0.8,"uplifting":0.5,"haunting":0.9,"aggressive":0.3,"romantic":0.8,"mysterious":0.8,"playful":0.3,"epic":0.6,"introspective":0.9,"joyful":0.4},
    "uplifting":{"melancholic":0.5,"uplifting":1.0,"haunting":0.4,"aggressive":0.6,"romantic":0.7,"mysterious":0.5,"playful":0.9,"epic":0.8,"introspective":0.5,"joyful":0.95},
    "haunting":{"melancholic":0.9,"uplifting":0.4,"haunting":1.0,"aggressive":0.3,"romantic":0.6,"mysterious":0.95,"playful":0.2,"epic":0.7,"introspective":0.85,"joyful":0.3},
    "aggressive":{"melancholic":0.3,"uplifting":0.6,"haunting":0.3,"aggressive":1.0,"romantic":0.2,"mysterious":0.4,"playful":0.5,"epic":0.9,"introspective":0.2,"joyful":0.6},
    "romantic":{"melancholic":0.8,"uplifting":0.7,"haunting":0.6,"aggressive":0.2,"romantic":1.0,"mysterious":0.6,"playful":0.6,"epic":0.5,"introspective":0.8,"joyful":0.7},
    "mysterious":{"melancholic":0.8,"uplifting":0.5,"haunting":0.95,"aggressive":0.4,"romantic":0.6,"mysterious":1.0,"playful":0.3,"epic":0.7,"introspective":0.8,"joyful":0.4},
    "playful":{"melancholic":0.3,"uplifting":0.9,"haunting":0.2,"aggressive":0.5,"romantic":0.6,"mysterious":0.3,"playful":1.0,"epic":0.6,"introspective":0.3,"joyful":0.95},
    "epic":{"melancholic":0.6,"uplifting":0.8,"haunting":0.7,"aggressive":0.9,"romantic":0.5,"mysterious":0.7,"playful":0.6,"epic":1.0,"introspective":0.5,"joyful":0.75},
    "introspective":{"melancholic":0.9,"uplifting":0.5,"haunting":0.85,"aggressive":0.2,"romantic":0.8,"mysterious":0.8,"playful":0.3,"epic":0.5,"introspective":1.0,"joyful":0.4},
    "joyful":{"melancholic":0.4,"uplifting":0.95,"haunting":0.3,"aggressive":0.6,"romantic":0.7,"mysterious":0.4,"playful":0.95,"epic":0.75,"introspective":0.4,"joyful":1.0},
}

# Engineering: Mastering presets
MASTERING_PRESETS = {
    "Epic Orchestral":["[CINEMATIC SPATIAL MIX]","[WIDE STEREO FIELD]","[DYNAMIC RANGE PRESERVED]","[BALANCED FREQUENCY SPECTRUM]","[IMPACTFUL LOW END]"],
    "Ambient / Chillout":["[DEPTH IN AMBIENCE]","[SMOOTH HIGH FREQUENCIES]","[BALANCED FREQUENCY SPECTRUM]","[WIDE STEREO FIELD]","[CLEAR LEAD VOCAL]"],
    "Electronic / Synthwave":["[PUNCHY LOW END]","[CONTROLLED BASS RESPONSE]","[WIDE STUDIO FIELD]" if False else "[WIDE STEREO FIELD]","[NO HARSHNESS IN HIGHS]","[RHYTHMIC DRIVE EMPHASIZED]"],
    "Rock / Metal":["[IMPACTFUL LOW END]","[PRESERVE TRANSIENT IMPACT]","[VOCALS CUT THROUGH MIX]","[BALANCED FREQUENCY SPECTRUM]","[CONTROLLED BASS RESPONSE]"],
    "Lo-fi / Hip-Hop":["[SOFTENED HIGH FREQUENCIES]","[VINYL TEXTURE RETAINED]" if False else "[VINYL CRACKLE]","[BALANCED FREQUENCY SPECTRUM]","[SMOOTH LOW END]","[WARM MIDRANGE PRESENCE]"]
}

# Common mistakes initial
COMMON_MISTAKES = [
    {"pattern":"too_many_instruments","rule":"Более 7 инструментов в одной секции","fix":"Свести к 4–6 ключевым или использовать [Rich Layered Arrangement]","comment":"Слишком большой список инструментов замыливает аранжировку"},
    {"pattern":"too_many_vocals","rule":"Более 4-х вокальных стилей сразу","fix":"Оставить 1–2 для лид‑вокала + 1–2 для бэков","comment":"Система путается с ролью голоса"},
    {"pattern":"duplicate_tags","rule":"Дублирующиеся теги","fix":"Оставить только уникальные","comment":"Не усиливает стиль, только шумит"}
]

# ------------------------------
# Helper functions
# ------------------------------

def choose_related(emotion):
    vocals, genres = EMOTION_MAP.get(emotion, (["expressive vocals"],["cinematic world fusion"]))
    return random.choice(vocals), random.choice(genres)

def choose_region_tag(region=None):
    if not region:
        region = random.choice(list(WORLD_REGIONS.keys()))
    return region, random.choice(WORLD_REGIONS[region])

def suggest_params(emotion, genre):
    # Auto recommendations for Suno sliders
    if genre in ["epic orchestral","symphonic metal","cinematic"] or emotion=="epic":
        return 0.35, 0.8, 0.3
    if genre in ["ambient","dark ambient","world fusion","downtempo"]:
        return 0.4, 0.7, 0.3
    if genre in ["metal","industrial","punk"]:
        return 0.45, 0.7, 0.2
    if genre in ["indie folk","acoustic","minimalist"]:
        return 0.3, 0.7, 0.2
    return 0.5, 0.6, 0.3

def build_style_prompt(emotion=None, region=None, era=None, extend=False, extra_tags=None, sfx_list=None, instruments=None, vocal_override=None, genre_override=None):
    if not emotion:
        emotion = random.choice(CORE_EMOTIONS)
    vocal, genre = choose_related(emotion)
    if vocal_override: vocal = vocal_override
    if genre_override: genre = genre_override
    region, region_tag = choose_region_tag(region)
    era = era or random.choice(ERAS)
    instrument = random.choice(INSTRUMENT_TAGS) if not instruments else ", ".join(instruments)

    base = f"{emotion.capitalize()} {vocal} over {genre} with {region_tag} influence, {instrument} accompaniment, {era} production aesthetic"
    if extend:
        # EXTEND: richer connective phrasing + tag ordering
        ext_bits = []
        if extra_tags: ext_bits += extra_tags
        if sfx_list: ext_bits += sfx_list
        # Reorder: genre/emotion → vocal → instruments → region → sfx → engineering
        base = (f"{emotion.capitalize()} {genre} narrative where {vocal} leads with nuanced phrasing, "
                f"supported by {instrument}; subtle {region_tag} colorations shape the timbre across a {era} aesthetic. ")
        if sfx_list:
            base += "Atmospheric textures " + ", ".join(sfx_list) + " frame transitions. "
        if extra_tags:
            base += "Engineering focus: " + " ".join(extra_tags)
    # Exclude list from conflicts
    excludes = []
    for a,b in HIGH_CONFLICTS:
        if a in base and b not in excludes: excludes.append(b)
        if b in base and a not in excludes: excludes.append(a)
    return base, ", ".join(excludes)

def variation_remix(prompt, intensity="light"):
    # light: swap instrument/effect words; radical: switch genre/vocal adjectives
    if intensity=="light":
        swaps = [("accompaniment","layers"),("atmospheric","textural"),("subtle","gentle"),("deep","low")]
    else:
        swaps = [("ambient","trip-hop"),("neoclassical","cinematic"),("soft","gritty"),("breathy","raspy")]
    out = prompt
    for a,b in swaps:
        out = out.replace(a,b,1)
    return out

# ------------------------------
# HTML (single page, dark theme)
# ------------------------------


# ---------- Unified weights (extended) ----------
UNIFIED_PATH = "./unified-suno-weights-expanded.json"
DEFAULT_STYLE_TAGS = []
CO_WEIGHTS = {}
try:
    with open(UNIFIED_PATH, "r", encoding="utf-8") as _f:
        _J = json.load(_f)
        DEFAULT_STYLE_TAGS = sorted(set(_J.get("default_styles", [])))
        CO_WEIGHTS = _J.get("co_existing_styles_dict", {})
except Exception as _e:
    DEFAULT_STYLE_TAGS = DEFAULT_STYLE_TAGS or ["pop","rock","rap","electro","ambient"]
    CO_WEIGHTS = CO_WEIGHTS or {}

def _compress_co(co, top=30):
    import math
    out = {}
    for t, neigh in (co or {}).items():
        if not isinstance(neigh, dict) or not neigh: 
            continue
        items = sorted(neigh.items(), key=lambda kv: kv[1], reverse=True)[:top]
        logs = [math.log1p(v) for _, v in items]
        if not logs: 
            continue
        mn, mx = min(logs), max(logs)
        span = (mx - mn) or 1.0
        out[t] = {str(k): round((math.log1p(v)-mn)/span, 4) for k, v in items}
    return out

CO_CLIENT = _compress_co(CO_WEIGHTS, top=30)

# derive tag universes
REGION_TAGS = sorted({t for arr in WORLD_REGIONS.values() for t in arr})
SFX_TAGS = sorted({t for arr in SFX.values() for t in arr})
ENGINEERING_TAGS = sorted({t for arr in SONG_IMPACT_TAGS.values() for t in arr})
ALL_TAGS = sorted(set(DEFAULT_STYLE_TAGS) | set(INSTRUMENT_TAGS) | set(REGION_TAGS) | set(SFX_TAGS) | set(ENGINEERING_TAGS))

# ------------------------------
# Flask routes
# ------------------------------


def _assert_jsonable(name, obj):
    try:
        json.dumps(obj, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"{name} is not JSON serializable: {type(obj).__name__} -> {e}")

@app.errorhandler(500)
def _err(e):
    tb = traceback.format_exc()
    html = f"<pre style='color:#eee;background:#111;padding:16px;border:1px solid #444;border-radius:8px'>{tb}</pre>"
    return Response(html, status=500, mimetype="text/html")

@app.route("/__ping")
def _ping():
    return "OK :: Flask is serving", 200

@app.route("/build_style", methods=["POST"])
def build_style_api():
    data = request.get_json(force=True) or {}
    tags = data.get("tags") or []
    if isinstance(tags, list):
        user_input = ", ".join(tags)
    else:
        user_input = str(tags)
    desc, excl = run_style_builder(user_input)
    return {"description": desc, "excludes": excl}

@app.route("/", methods=["GET"])
def index():
    data = {
        "emotions": CORE_EMOTIONS,
        "emap": EMOTION_MAP,
        "regions": WORLD_REGIONS,
        "eras": ERAS,
        "conflicts": HIGH_CONFLICTS,
        "impact": SONG_IMPACT_TAGS,
        "sfx": SFX,
        "combos": SFX_COMBOS,
        "ecompat": EMOTION_COMPAT,
        "mpresets": MASTERING_PRESETS,
        "mistakes": COMMON_MISTAKES,
        "all_tags": ALL_TAGS,
        "co_weights": CO_CLIENT,
        "instruments": sorted(INSTRUMENT_TAGS),
        "DEFAULT_STYLE_TAGS": DEFAULT_STYLE_TAGS,
    }
    for k, v in data.items():
        _assert_jsonable(k, v)

    print(f"[INDEX] tags={len(ALL_TAGS)} styles={len(DEFAULT_STYLE_TAGS)}")
    return render_template("index.html", data=data)

# ---------- MAIN ----------
if __name__ == "__main__":
    
    print(f"Запущено. Открой: http://127.0.0.1:5000  |  /__ping")
    app.run(host="127.0.0.1", port=5000, debug=True)

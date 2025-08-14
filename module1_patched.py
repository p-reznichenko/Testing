#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suno Full Generator — All‑in‑One (OFFLINE)
Запуск:
    pip install flask
    python suno_full_generator.py
Открой в браузере: http://127.0.0.1:5000
"""

from flask import Flask, request, render_template_string, send_file
import io, json, random, datetime
import traceback
from flask import Flask, render_template_string, Response

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["ENV"] = "development"
app.config["DEBUG"] = True  # включаем подробные ошибки


app = Flask(__name__)

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
PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Suno Full Generator — All-in-One</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
:root{--bg:#0d0f14;--panel:#141822;--accent:#6ea8fe;--text:#e7e9ee;--muted:#9aa3b2;--warn:#f7b267;--bad:#ff6b6b;--good:#58d68d;}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Roboto,Inter,Arial}
h1,h2,h3{margin:0 0 .6rem} a{color:var(--accent)}
.header{padding:16px 20px;background:#0b0e12;border-bottom:1px solid #1e2430}
.tabs{display:flex;flex-wrap:wrap;gap:6px;padding:10px 12px;background:#0b0e12;position:sticky;top:0;z-index:5}
.tab{padding:8px 12px;border:1px solid #1e2430;border-radius:8px;background:var(--panel);cursor:pointer}
.tab.active{outline:1px solid var(--accent)}
.section{display:none;padding:16px 20px}
.section.active{display:block}
.grid{display:grid;gap:12px}
.col2{grid-template-columns:1fr 1fr}
.col3{grid-template-columns:1fr 1fr 1fr}
.input, select, textarea{width:100%;background:#0f131b;color:var(--text);border:1px solid #262c3a;border-radius:8px;padding:10px}
.btn{background:var(--accent);color:#00142a;border:none;border-radius:8px;padding:10px 12px;cursor:pointer}
.btn.alt{background:#2a3347;color:var(--text)}
.btn.warn{background:var(--warn);color:#2b1600}
.btn.bad{background:var(--bad);color:#210000}
.small{color:var(--muted);font-size:.9rem}
.box{background:var(--panel);border:1px solid #1e2430;border-radius:10px;padding:12px}
.kbd{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.95rem}
.table{width:100%;border-collapse:collapse}
.table th,.table td{border-bottom:1px solid #242b3a;padding:6px 8px;text-align:left}
.tag{display:inline-block;padding:4px 8px;border-radius:999px;background:#1e2430;margin:2px;border:1px solid #2c3447}
.badge{padding:2px 6px;border-radius:6px;background:#1e2430;border:1px solid #2c3447;margin-left:6px}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.slider-row{display:grid;gap:6px;grid-template-columns:160px 1fr 60px}
progress{width:100%}
.note{padding:8px;border-left:3px solid var(--accent);background:#0f131b;border-radius:6px}
.warnbox{padding:8px;border-left:3px solid var(--warn);background:#1d140b;border-radius:6px}
.goodbox{padding:8px;border-left:3px solid var(--good);background:#0b1c14;border-radius:6px}
.tag{display:inline-block;padding:6px 10px;border:1px solid #1e2430;border-radius:999px;background:#131a29;cursor:pointer}
.tag.disabled{opacity:.45;filter:grayscale(1);pointer-events:none}
.tag.sel{outline:1px solid var(--accent);box-shadow:0 0 0 2px rgba(110,168,254,.15) inset}
.pill{display:inline-flex;gap:6px;align-items:center;padding:4px 8px;background:#1e2430;border:1px solid #2c3447;border-radius:999px}
#tagGrid{min-height:240px}
#sentinel{height:1px}
</style>   <!-- ← закрываем стиль -->
</head>
<body>
<div class="header">
  <h1>Suno Full Generator — All‑in‑One (Offline)</h1>
  <div class="small">Everything we discussed, in one dark UI. LocalStorage for history, rules, presets. No internet required.</div>
</div>

<!-- Tabs -->
<div class="tabs" id="tabs">
  <div class="tab active" data-tab="gen">1) Hybrid Prompt Generator</div>
  <div class="tab" data-tab="atlas">2) World Vocal Atlas & Instruments</div>
  <div class="tab" data-tab="emap">3) Emotion Compatibility Map</div>
  <div class="tab" data-tab="guide">4) Vocal & Mix Engineering Guide</div>
  <div class="tab" data-tab="sfx">5) Sound Effects & Textures</div>
  <div class="tab" data-tab="orch">6) Vocal & Instrument Orchestrator</div>
  <div class="tab" data-tab="extend">7) EXTEND Section Planner</div>
  <div class="tab" data-tab="advance">8) Advanced & Secrets</div>
  <div class="tab" data-tab="vault">9) History / Instant Remix / AI Suggest</div>
  <div class="tab" data-tab="info">10) INFO • Settings • Mastering</div>
  <div class="tab" data-tab="tags">11) Tag Browser</div>
</div>

<!-- 1) GENERATOR -->
<div class="section active" id="gen">
  <div class="grid col2">
    <div class="box">
      <h2>Hybrid Prompt Generator</h2>
      <div class="row">
        <label>Mode</label>
        <select id="mode" class="input">
          <option value="random">Random</option>
          <option value="manual">Manual</option>
          <option value="batch">Batch</option>
        </select>
        <label>Special Emotion Hybrid Preset</label>
        <select id="preset" class="input">
          <option value="">(none)</option>
          <option>Epic + Melancholic</option>
          <option>Joyful + Haunting</option>
          <option>Romantic + Aggressive</option>
          <option>Introspective + Triumphant</option>
          <option>Mysterious + Uplifting</option>
        </select>
      </div>
      <div id="manualBlock" class="grid col3" style="margin-top:8px;">
        <div>
          <label>Emotion</label>
          <select id="emotion" class="input"></select>
        </div>
        <div>
          <label>Region</label>
          <select id="region" class="input"></select>
        </div>
        <div>
          <label>Era</label>
          <select id="era" class="input"></select>
        </div>
      </div>
      <div class="row" style="margin-top:8px;">
        <label>Count</label><input id="count" type="number" class="input" min="1" max="50" value="1" style="max-width:120px">
        <label><input type="checkbox" id="extendToggle"> EXTEND mode</label>
        <button class="btn" id="genBtn">Generate</button>
        <button class="btn alt" id="gen10">Generate 10 Variations</button>
      </div>
      <div style="margin-top:10px" class="note">
        <b>Auto‑Params</b> — Weirdness, Style Influence, Audio Influence подбираются автоматически; можно изменить вручную ниже.
      </div>
      <div class="grid">
        <div class="slider-row"><div>Weirdness</div><input id="weird" type="range" min="0" max="1" step="0.01"><input id="weirdVal" class="input" style="max-width:60px"></div>
        <div class="slider-row"><div>Style Influence</div><input id="styleinf" type="range" min="0" max="1" step="0.01"><input id="styleVal" class="input" style="max-width:60px"></div>
        <div class="slider-row"><div>Audio Influence</div><input id="audioinf" type="range" min="0" max="1" step="0.01"><input id="audioVal" class="input" style="max-width:60px"></div>
      </div>
      <div class="grid col2" style="margin-top:10px;">
        <div>
          <label>Style Prompt (ready for Suno)</label>
          <textarea id="styleOut" rows="8" class="input kbd"></textarea>
          <button class="btn alt" id="copyStyle">Copy</button>
        </div>
        <div>
          <label>Exclude Styles</label>
          <textarea id="excludeOut" rows="8" class="input kbd"></textarea>
          <button class="btn alt" id="copyExclude">Copy</button>
        </div>
      </div>
      <div class="row" style="margin-top:8px;">
        <button class="btn" id="exportTxt">Export TXT</button>
        <button class="btn" id="exportJson">Export JSON</button>
        <button class="btn alt" id="addImpact">+ Add Impact Tags</button>
      </div>
      <div id="actionLog" class="box" style="margin-top:10px;">
        <b>Action Log</b>
        <div id="logLines" class="small"></div>
      </div>
    </div>

    <div class="box">
      <h3>Impact Tags (click to append)</h3>
      <div id="impactLists"></div>
      <hr>
      <h3>Suggest Mode (AI‑like, offline)</h3>
      <div class="small">Предлагает 3 альтернативных версии в духе AI Suggest Mode на основе текущих настроек.</div>
      <button class="btn" id="suggest3">Suggest 3 Alternatives</button>
      <div id="suggestBox" class="grid"></div>
      <hr>
      <h3>Style Clash Detector</h3>
      <div id="clashResult" class="small"></div>
    </div>
  </div>
</div>

<!-- 2) ATLAS & INSTRUMENTS -->
<div class="section" id="atlas">
  <div class="grid col2">
    <div class="box">
      <h2>World Vocal Atlas</h2>
      <div id="atlasList"></div>
    </div>
    <div class="box">
      <h2>Instrument Pack</h2>
      <div id="instList"></div>
      <hr>
      <button class="btn alt" id="pushToPrompt">Insert selected into Style Prompt</button>
    </div>
  </div>
</div>

<!-- 3) EMOTION MAP -->
<div class="section" id="emap">
  <div class="box">
    <h2>Emotion Compatibility Map</h2>
    <div class="small">🟢 0.7–1.0 high • 🟡 0.4–0.69 medium • 🔴 0–0.39 conflict</div>
    <table class="table" id="emapTable"></table>
  </div>
</div>

<!-- 4) ENGINEERING GUIDE -->
<div class="section" id="guide">
  <div class="grid col2">
    <div class="box">
      <h2>Compact Tags</h2>
      <div id="compactTags" class="kbd"></div>
      <button class="btn alt" id="copyCompact">Copy All</button>
    </div>
    <div class="box">
      <h2>Expanded Examples</h2>
      <div class="note kbd">[CLEAR LEAD VOCAL] — основной вокал чисто читается в миксе. Использовать: баллады, акустика, джаз.</div>
      <div class="note kbd">[CLARITY IN VOCAL BREATHS] — подчёркнутые вдохи/дыхание для интимности. Lo‑fi, folk, world.</div>
      <div class="note kbd">[CINEMATIC SPATIAL MIX] — объёмный «кино‑микс». Epic/Score.</div>
      <div class="note kbd">[DYNAMIC RANGE PRESERVED] — динамика сохранена, трек «дышит».</div>
      <div class="note kbd">[WIDE STEREO FIELD] — широкая панорама (осторожно с интимными жанрами).</div>
    </div>
  </div>
</div>

<!-- 5) SFX -->
<div class="section" id="sfx">
  <div class="grid col2">
    <div class="box">
      <h2>Effects & Textures</h2>
      <div id="sfxLists"></div>
    </div>
    <div class="box">
      <h2>Effect Combos</h2>
      <div id="comboList"></div>
      <div class="row" style="margin-top:8px;">
        <button class="btn" id="randomCombo">Random Combo</button>
        <button class="btn alt" id="clearEffects">Clear Effects</button>
      </div>
      <div class="note" style="margin-top:8px;">
        <b>Prompt Preview</b>
        <div id="previewBox" class="kbd small"></div>
      </div>
    </div>
  </div>
</div>

<!-- 6) ORCHESTRATOR -->
<div class="section" id="orch">
  <div class="grid col2">
    <div class="box">
      <h2>Vocal & Instrument Orchestrator</h2>
      <div class="grid col3">
        <div><label>Vocalists</label><input id="vocCount" type="number" class="input" min="1" max="6" value="2"></div>
        <div><label>Instruments</label><input id="instCount" type="number" class="input" min="1" max="12" value="5"></div>
        <div><label>Interactions</label><select id="interact" class="input">
          <option>call & response</option><option>layered harmonies</option><option>overlapping phrases</option></select>
        </div>
      </div>
      <button class="btn" id="calcComplex">Analyze Density</button>
      <div id="complexBox" style="margin-top:8px"></div>
      <div class="warnbox small" style="margin-top:8px;">
        Tips: для дуэтов — добавляй [WIDE STEREO FIELD]. Если много вокалов — избегай жёсткого [CENTERED LEAD VOCAL].
      </div>
    </div>
    <div class="box">
      <h3>Quick Structure</h3>
      <div class="kbd small">[Verse: Male lead + acoustic guitar], [Chorus: Male‑Female duet + full band], [Bridge: Solo flute + soft choir]</div>
      <button class="btn alt" id="orchToPrompt">Insert structure into Style Prompt</button>
    </div>
  </div>
</div>

<!-- 7) EXTEND PLANNER -->
<div class="section" id="extend">
  <div class="grid col2">
    <div class="box">
      <h2>EXTEND Section Planner</h2>
      <div class="row">
        <select id="tpl" class="input" style="max-width:260px">
          <option value="song">Standard Song</option>
          <option value="cinema">Cinematic</option>
          <option value="edm">Electronic</option>
        </select>
        <button class="btn" id="loadTpl">Load Template</button>
        <button class="btn alt" id="addSection">+ Section</button>
      </div>
      <div id="sections"></div>
      <div class="row" style="margin-top:8px;">
        <button class="btn" id="suggestSections">Suggest Section Tags</button>
        <button class="btn" id="analyzeSections">Analyze Conflicts</button>
        <button class="btn alt" id="balanceSections">Balance Meter</button>
      </div>
      <div id="sectionReport" class="small" style="margin-top:6px"></div>
      <button class="btn" style="margin-top:10px" id="buildExtend">Build EXTEND Style</button>
    </div>
    <div class="box">
      <h3>EXTEND Output → Style Prompt</h3>
      <textarea id="extendOut" rows="14" class="input kbd"></textarea>
      <button class="btn alt" id="pushExtend">Push to Main Style Prompt</button>
      <div class="note small" style="margin-top:6px;">
        EXTEND упорядочит жанр→вокал→инструменты→регион→эффекты→инж. теги и свяжет фразы.
      </div>
    </div>
  </div>
</div>

<!-- 8) ADVANCED -->
<div class="section" id="advance">
  <div class="box">
    <h2>Advanced Prompting & Secrets (offline)</h2>
    <ul class="small">
      <li><b>Prompt Weighting</b>: keywords:weight — напр. <span class="kbd">epic orchestral:1.3, cinematic choir:1.2</span></li>
      <li><b>Tag Group Lock</b>: «замораживай» блоки (вокал/эффекты), меняя только инструменты → стабильные вариации</li>
      <li><b>Dynamic Bridge Builder</b>: для конфликтных эмоций добавляй мост: <span class="kbd">in ethereal trip‑hop setting</span></li>
      <li><b>Sectional Prompting</b>: описывай секции в [] — Suno лучше держит форму</li>
      <li><b>Rare Tag Explorer</b>: используй редкие теги из Atlas/PRO‑предложений (подсвечиваются как rare)</li>
    </ul>
    <div class="note">Встроенные материалы: encoder / style builder / banned list — учтены в логике порядка тегов, исключений и проверок.</div>
  </div>
</div>

<!-- 9) HISTORY / REMIX / AI SUGGEST -->
<div class="section" id="vault">
  <div class="grid col2">
    <div class="box">
      <h2>Prompt History Vault</h2>
      <div class="small">Сохраняется локально в браузере (localStorage). Можно искать и клонировать.</div>
      <div class="row">
        <input id="hSearch" class="input" placeholder="Search in history…">
        <button class="btn alt" id="hClear">Clear All</button>
      </div>
      <div id="historyList" class="small" style="margin-top:8px"></div>
    </div>
    <div class="box">
      <h2>Instant Remix & AI Suggest Mode</h2>
      <div class="row"><button class="btn" id="remixLight">Instant Remix (light)</button><button class="btn alt" id="remixRad">Instant Remix (radical)</button></div>
      <div style="margin-top:8px" class="grid" id="aiBox"></div>
    </div>
  </div>
</div>

<!-- 11) TAG BROWSER -->
  <div class="section" id="tags">
    <div class="box">
      <h2>Tag Browser</h2>
      <div class="row" style="gap:8px;flex-wrap:wrap">
        <input id="tagSearch" class="input" placeholder="Поиск по тегам…" style="max-width:360px">
        <span class="pill"><input type="checkbox" id="onlyEnabled"> показать только доступные</span>
        <span class="pill"><input type="checkbox" id="appendComma" checked> добавлять с запятой</span>
        <button class="btn alt" id="addSelected">Добавить выбранные в Style</button>
        <button class="btn alt" id="clearSelected">Очистить выбор</button>
      </div>
      <div class="row" style="gap:10px;flex-wrap:wrap;margin-top:8px">
        <span class="pill">
          Совместимость ≥ <b id="compatVal">35</b>%
          <input type="range" id="compatSlider" min="0" max="100" value="35" style="width:180px;margin-left:8px">
        </span>
        <span class="pill">
          Порог «жёсткого конфликта»
          <select id="hardMode">
            <option value="auto">auto (по весам)</option>
            <option value="off">off</option>
            <option value="strict">strict</option>
          </select>
        </span>
      </div>
      <div id="tagStats" class="small" style="margin-top:6px"></div>
    </div>

    <div class="box" style="margin-top:10px">
      <div id="tagGrid" class="row" style="gap:6px;flex-wrap:wrap"></div>
      <div id="sentinel"></div>
    </div>

    <div class="note small">
      Клик — добавляет тег в Style Prompt. Правый клик — добавляет в Exclude Styles.
      Конфликтующие с выбранными становятся <b>неактивными</b>.
    </div>
  </div>

<!-- 10) INFO / SETTINGS / MASTERING -->
<div class="section" id="info">
  <div class="grid col2">
    <div class="box">
      <h2>Suno Settings Guide</h2>
      <ul class="small">
        <li><b>Weirdness</b> — 0–0.2 предсказуемо; 0.3–0.6 гибриды; 0.7–1.0 эксперимент.</li>
        <li><b>Style Influence</b> — 0.8–1.0 строго по промпту; 0.5–0.7 баланс; 0.3–0.5 свободно.</li>
        <li><b>Audio Influence</b> — 0.3–0.5 тонкая подмешка референса; 0.8–1.0 почти копия атмосферы.</li>
      </ul>
      <h3>Settings</h3>
      <label><input type="checkbox" id="strictMode"> Strict Mode (block on errors)</label>
      <div class="small">По умолчанию выключен.</div>
    </div>
    <div class="box">
      <h2>Mastering Checklist + Genre Presets</h2>
      <div class="row">
        <select id="masterPreset" class="input" style="max-width:260px">
          <option value="">(choose preset)</option>
          <option>Epic Orchestral</option>
          <option>Ambient / Chillout</option>
          <option>Electronic / Synthwave</option>
          <option>Rock / Metal</option>
          <option>Lo-fi / Hip-Hop</option>
        </select>
        <button class="btn" id="applyMaster">Apply to Style Prompt</button>
      </div>
      <div class="grid col2" style="margin-top:8px;">
        <div class="goodbox small">
          <b>Pro Mixing Tips</b><br>
          • Use [VOCALS CUT THROUGH MIX] for dense arrangements.<br>
          • Prefer [CLARITY IN VOCAL BREATHS] for intimate tracks.<br>
          • [WIDE STEREO FIELD] for duets/ensembles; avoid over‑widening lo‑fi.<br>
        </div>
        <div class="warnbox small">
          <b>Common Mistakes (editable)</b>
          <div id="mistakesBox"></div>
          <div class="row" style="margin-top:6px">
            <input id="mRule" class="input" placeholder="Rule/Pattern">
            <input id="mFix" class="input" placeholder="Fix/Advice">
            <input id="mNote" class="input" placeholder="Comment">
            <button class="btn alt" id="mAdd">Add</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  

</div>

<script>
// ---------- datasets from server ----------
const CORE_EMOTIONS = {{ emotions|tojson }};
const EMOTION_MAP = {{ emap|tojson }};
const WORLD_REGIONS = {{ regions|tojson }};
const INSTRUMENT_TAGS = {{ instruments|tojson }};
const ERAS = {{ eras|tojson }};
const HIGH_CONFLICTS = {{ conflicts|tojson }};
const SONG_IMPACT_TAGS = {{ impact|tojson }};
const SFX = {{ sfx|tojson }};
const SFX_COMBOS = {{ combos|tojson }};
const EMOTION_COMPAT = {{ ecompat|tojson }};
const MASTERING_PRESETS = {{ mpresets|tojson }};
let COMMON_MISTAKES = JSON.parse(localStorage.getItem("COMMON_MISTAKES")||"null") || {{ mistakes|tojson }};
const ALL_TAGS = {{ all_tags|default([])|tojson }};
const CO = {{ co_weights|default({})|tojson }};
const REGION_TAGS = Object.values(WORLD_REGIONS||{}).flat();
const SFX_TAGS = Object.values(SFX||{}).flat();
const ENGINEERING_TAGS = Object.values(SONG_IMPACT_TAGS||{}).flat();
const DEFAULT_STYLE_TAGS = {{ DEFAULT_STYLE_TAGS|tojson }};


// ---------- tabs ----------
const tabs = document.querySelectorAll(".tab");
const sections = document.querySelectorAll(".section");
tabs.forEach(t=>{
  t.onclick=()=>{
    tabs.forEach(x=>x.classList.remove("active"));
    sections.forEach(s=>s.classList.remove("active"));
    t.classList.add("active");
    document.getElementById(t.dataset.tab).classList.add("active");
  };
});

// ---------- populate selects ----------
function fillSelect(id, arr){const sel=document.getElementById(id); sel.innerHTML=""; arr.forEach(v=>{const o=document.createElement("option");o.textContent=v;o.value=v; sel.appendChild(o);});}
fillSelect("emotion", CORE_EMOTIONS);
fillSelect("region", Object.keys(WORLD_REGIONS));
fillSelect("era", ERAS);

// ---------- manual hide/show ----------
const modeSel=document.getElementById("mode");
const manualBlock=document.getElementById("manualBlock");
modeSel.onchange=()=>{manualBlock.style.display = (modeSel.value==="manual"?"grid":"none");};
modeSel.onchange();

// ---------- utils ----------
function log(msg){const box=document.getElementById("logLines"); const t = new Date().toLocaleTimeString(); box.innerHTML = `<div>• ${t} — ${msg}</div>` + box.innerHTML; localStorage.setItem("ACTION_LOG", box.innerHTML);}
function copyText(id){const el=document.getElementById(id); el.select(); document.execCommand("copy");}
document.getElementById("copyStyle").onclick=()=>copyText("styleOut");
document.getElementById("copyExclude").onclick=()=>copyText("excludeOut");

// ---------- auto params sliders ----------
const weird=document.getElementById("weird"), styleinf=document.getElementById("styleinf"), audioinf=document.getElementById("audioinf");
const weirdVal=document.getElementById("weirdVal"), styleVal=document.getElementById("styleVal"), audioVal=document.getElementById("audioVal");
[weird,styleinf,audioinf].forEach(s=>s.oninput=()=>{ if(s===weird) weirdVal.value=s.value; if(s===styleinf) styleVal.value=s.value; if(s===audioinf) audioVal.value=s.value; });

// ---------- impact tags panel ----------
const impactBox=document.getElementById("impactLists");
function drawImpact(){
  impactBox.innerHTML="";
  for(const k of Object.keys(SONG_IMPACT_TAGS)){
    const wrap=document.createElement("div"); wrap.className="box"; wrap.style.marginBottom="8px";
    wrap.innerHTML=`<b>${k}</b><div id="imp_${k}"></div>`;
    impactBox.appendChild(wrap);
    const holder=wrap.querySelector("#imp_"+k);
    SONG_IMPACT_TAGS[k].forEach(tag=>{
      const t=document.createElement("span"); t.className="tag"; t.textContent=tag; t.onclick=()=>{
        const st=document.getElementById("styleOut");
        st.value = (st.value+" "+tag).trim();
        log(`Added impact tag ${tag}`);
      }; holder.appendChild(t);
    });
  }
}
drawImpact();

document.getElementById("addImpact").onclick=()=>{
  const st=document.getElementById("styleOut");
  const block = Object.values(SONG_IMPACT_TAGS).flat().slice(0,5).join(" ");
  st.value = (st.value+" "+block).trim();
  log("Added default impact tag bundle");
};

// ---------- atlas & instruments ----------
const atlasList=document.getElementById("atlasList"), instList=document.getElementById("instList");
for(const [reg,tags] of Object.entries(WORLD_REGIONS)){
  const b=document.createElement("div"); b.className="box";
  b.innerHTML=`<b>${reg}</b><div>${tags.map(t=>`<span class="tag atlasTag">${t}</span>`).join(" ")}</div>`;
  atlasList.appendChild(b);
}
WORLD_REGIONS; document.querySelectorAll(".atlasTag").forEach(el=>el.onclick=()=>pushToPrompt(el.textContent));
instList.innerHTML = INSTRUMENT_TAGS.map(t=>`<label style="display:block"><input type="checkbox" class="ckInst" value="${t}"> ${t}</label>`).join("");
document.getElementById("pushToPrompt").onclick=()=>{
  const sel=[...document.querySelectorAll(".ckInst:checked")].map(x=>x.value);
  const st=document.getElementById("styleOut");
  if(sel.length){ st.value = (st.value+" "+sel.join(", ")).trim(); log(`Inserted instruments: ${sel.join(", ")}`); }
};

// ---------- Emotion Map ----------
const mapTable=document.getElementById("emapTable");
(function drawMap(){
  const rows = [];
  const head = `<tr><th></th>${CORE_EMOTIONS.map(e=>`<th>${e}</th>`).join("")}</tr>`;
  rows.push(head);
  for(const r of CORE_EMOTIONS){
    let tds = `<td><b>${r}</b></td>`;
    for(const c of CORE_EMOTIONS){
      const v = EMOTION_COMPAT[r][c];
      let col = v>=0.7? "#15351f" : v>=0.4? "#3a2f12" : "#3a1313";
      tds += `<td style="background:${col};cursor:pointer" data-r="${r}" data-c="${c}" class="cell">${v.toFixed(2)}</td>`;
    }
    rows.push(`<tr>${tds}</tr>`);
  }
  mapTable.innerHTML = rows.join("");
  mapTable.querySelectorAll(".cell").forEach(td=>{
    td.onclick=()=>{
      const r=td.dataset.r, c=td.dataset.c;
      // Simple hybrid prompt using two emotions
      const e1=r, e2=c;
      const v1 = EMOTION_MAP[e1][0][0], g1 = EMOTION_MAP[e1][1][0];
      const region = Object.keys(WORLD_REGIONS)[0], rtag = WORLD_REGIONS[region][0];
      const inst = INSTRUMENT_TAGS[0];
      const text = `${e1}+${e2} ${v1} over ${g1} with ${rtag}, ${inst} accompaniment`;
      document.getElementById("styleOut").value = text;
      document.getElementById("excludeOut").value = suggestExcludes(text);
      autoParams(e1,g1);
      log(`Emotion pair → ${e1} + ${e2}`);
    };
  });
})();

// ---------- SFX ----------
const sfxLists=document.getElementById("sfxLists");
for(const [cat,arr] of Object.entries(SFX)){
  const b=document.createElement("div"); b.className="box";
  b.innerHTML=`<b>${cat}</b><div>${arr.map(s=>`<span class="tag sfxTag">${s}</span>`).join(" ")}</div>`;
  sfxLists.appendChild(b);
}
document.querySelectorAll(".sfxTag").forEach(el=>el.onclick=()=>pushToPrompt(el.textContent));
const comboList=document.getElementById("comboList");
for(const [grp,combos] of Object.entries(SFX_COMBOS)){
  const b=document.createElement("div"); b.className="box";
  b.innerHTML=`<b>${grp}</b><div>${combos.map(c=>`<span class="tag combo">${c.join(" + ")}</span>`).join(" ")}</div>`;
  comboList.appendChild(b);
}
document.querySelectorAll(".combo").forEach(el=>el.onclick=()=>{
  const parts = el.textContent.split(" + ");
  const st=document.getElementById("styleOut");
  st.value = (st.value+" "+parts.join(" ")).trim();
  document.getElementById("previewBox").textContent = st.value;
  log(`Inserted combo: ${el.textContent}`);
});
document.getElementById("randomCombo").onclick=()=>{
  const groups=Object.values(SFX_COMBOS); const group = groups[Math.floor(Math.random()*groups.length)];
  const combo = group[Math.floor(Math.random()*group.length)];
  const st=document.getElementById("styleOut");
  st.value = (st.value+" "+combo.join(" ")).trim();
  document.getElementById("previewBox").textContent = st.value;
  log("Random effect combo added");
};
document.getElementById("clearEffects").onclick=()=>{
  const st=document.getElementById("styleOut");
  st.value = st.value.replace(/\[(.*?)\]/g,"").replace(/\s{2,}/g," ").trim();
  document.getElementById("previewBox").textContent = st.value;
  log("Effects cleared");
};

// ---------- Orchestrator ----------
document.getElementById("calcComplex").onclick=()=>{
  const v=+document.getElementById("vocCount").value;
  const i=+document.getElementById("instCount").value;
  const x=document.getElementById("interact").value;
  const score = v*2 + i*1.2 + (x.includes("overlap")?3:(x.includes("layered")?2:1));
  let msg = `Complexity score: ${score.toFixed(1)} — `;
  if(score<=10.9) msg += "OK ✅";
  else if(score<=15.9) msg += "Aroma/Clutter Notice ⚠ — близко к перебору";
  else msg += "Overload Warning ⚠ — упростите до ≤3 вокалов и ≤7 инструментов";
  document.getElementById("complexBox").innerHTML = `<div class="${score>15.9?'warnbox':(score>10.9?'warnbox':'goodbox')} small">${msg}</div>`;
  log(msg);
};
document.getElementById("orchToPrompt").onclick=()=>{
  const txt = "[Verse: Male Lead + acoustic guitar] [Chorus: Male‑Female Duet + full band] [Bridge: Solo flute + soft choir]";
  const st=document.getElementById("styleOut"); st.value = (st.value+" "+txt).trim(); log("Inserted quick structure");
};

// ---------- EXTEND PLANNER ----------
let SEC_ID=0;
const sectionsWrap=document.getElementById("sections");
function sectionRow(name="Section"){
  const id=++SEC_ID;
  const row=document.createElement("div"); row.className="box"; row.dataset.sid=id;
  row.innerHTML = `
    <div class="row"><b>${name}</b><span class="badge">id:${id}</span><button class="btn alt" onclick="this.closest('.box').remove()">Remove</button></div>
    <div class="grid col3" style="margin-top:6px;">
      <div><label>Emotion</label><select class="input secEmotion">${CORE_EMOTIONS.map(e=>`<option>${e}</option>`).join("")}</select></div>
      <div><label>Vocal</label><input class="input secVocal" placeholder="male/female/duet/choir + style"></div>
      <div><label>Instruments</label><input class="input secInst" placeholder="up to 6 key instruments"></div>
    </div>
    <div class="grid col2" style="margin-top:6px;">
      <div><label>Effects/Atmosphere</label><input class="input secFx" placeholder="[OCEAN WAVES], [LOW DRONE] ..."></div>
      <div><label>Engineering Tags</label><input class="input secEng" placeholder="[CLEAR LEAD VOCAL] [CINEMATIC SPATIAL MIX]"></div>
    </div>
  `;
  sectionsWrap.appendChild(row);
}
function loadTemplate(kind){
  sectionsWrap.innerHTML="";
  if(kind==="song"){
    ["Intro","Verse 1","Chorus","Verse 2","Bridge","Chorus","Outro"].forEach(n=>sectionRow(n));
  }else if(kind==="cinema"){
    ["Ambient Intro","Build‑up","Climactic Section","Soft Bridge","Grand Finale","Atmospheric Outro"].forEach(n=>sectionRow(n));
  }else{
    ["FX Intro","Drop 1","Breakdown","Drop 2","FX Outro"].forEach(n=>sectionRow(n));
  }
}
document.getElementById("loadTpl").onclick=()=>loadTemplate(document.getElementById("tpl").value);
document.getElementById("addSection").onclick=()=>sectionRow("Custom");

document.getElementById("suggestSections").onclick=()=>{
  [...sectionsWrap.querySelectorAll(".box")].forEach((box,idx)=>{
    const emo=box.querySelector(".secEmotion").value;
    const voc=box.querySelector(".secVocal");
    const inst=box.querySelector(".secInst");
    const fx=box.querySelector(".secFx");
    const eng=box.querySelector(".secEng");
    // Safe vs Bold suggestions (simple demo)
    const safe = EMOTION_MAP[emo][0][0];
    const bold = EMOTION_MAP[emo][0].slice(-1)[0] + " + rare timbre";
    voc.value = idx%2? bold : safe;
    inst.value = idx%2? "bowed vibraphone, deep frame drums" : "acoustic guitar, soft strings";
    fx.value = idx%2? "[REVERSED REVERB], [LOW DRONE]" : "[ETHEREAL VOCAL GLOW]";
    eng.value = "[WIDE STEREO FIELD]" + (idx%2?" [DYNAMIC RANGE PRESERVED]":" [CLEAR LEAD VOCAL]");
  });
  document.getElementById("sectionReport").textContent="Smart Tag Suggestions applied (safe/bold alternation, rare tags included).";
  log("Section suggestions applied");
};

function gatherSections(){
  const list=[];
  [...sectionsWrap.querySelectorAll(".box")].forEach(box=>{
    list.push({
      id: box.dataset.sid,
      emo: box.querySelector(".secEmotion").value,
      voc: box.querySelector(".secVocal").value,
      inst: box.querySelector(".secInst").value,
      fx: box.querySelector(".secFx").value,
      eng: box.querySelector(".secEng").value
    });
  });
  return list;
}

document.getElementById("analyzeSections").onclick=()=>{
  const S = gatherSections();
  if(!S.length){ document.getElementById("sectionReport").textContent="No sections."; return; }
  // persistent detection
  const tally={}; const fields=["inst","fx","voc"];
  S.forEach(s=>fields.forEach(f=>{
    (s[f]||"").split(",").map(x=>x.trim()).filter(Boolean).forEach(tag=>{
      tally[tag]=(tally[tag]||0)+1;
    });
  }));
  const pers = Object.entries(tally).filter(([k,v])=>v>=S.length).map(([k])=>k);
  let out="";
  if(pers.length){
    out += "⚠ Persistent elements across ALL sections: "+pers.join(", ")+" — consider muting or varying in some parts.\n";
  } else out += "No persistent conflicts detected.\n";
  // duplicate emotions neighbors
  for(let i=1;i<S.length;i++){
    if(S[i].emo===S[i-1].emo){ out += `• Low contrast: ${S[i-1].emo} → ${S[i].emo} (adjacent)\n`; }
  }
  document.getElementById("sectionReport").textContent = out.trim();
};

document.getElementById("balanceSections").onclick=()=>{
  const S=gatherSections();
  if(!S.length){ document.getElementById("sectionReport").textContent="No sections."; return; }
  // naive balance: count non-empty slots per category per section
  let msg="Balance Meter:\n";
  S.forEach((s,i)=>{
    const emo= s.emo?1:0, voc=s.voc?1:0, inst=s.inst.split(",").filter(x=>x.trim()).length, fx=(s.fx.match(/\[[^\]]+\]/g)||[]).length, eng=(s.eng.match(/\[[^\]]+\]/g)||[]).length;
    msg+=`• Sec#${i+1}: Emo=${emo} Voc=${voc} Inst=${inst} FX=${fx} Eng=${eng}\n`;
  });
  document.getElementById("sectionReport").textContent=msg.trim();
};

document.getElementById("buildExtend").onclick=()=>{
  const S=gatherSections();
  if(!S.length){ document.getElementById("extendOut").value=""; return; }
  const parts = S.map(s=>`[${s.emo} — ${s.voc}; instruments: ${s.inst}; fx: ${s.fx}; eng: ${s.eng}]`);
  const text = "Extended cinematic narrative: " + parts.join(" ").replace(/\s+/g," ").trim();
  document.getElementById("extendOut").value=text;
  log("EXTEND style built from sections");
};
document.getElementById("pushExtend").onclick=()=>{
  const t=document.getElementById("extendOut").value;
  const st=document.getElementById("styleOut"); st.value = (st.value+" "+t).trim();
  log("EXTEND output pushed to main style");
};

// ---------- generator core ----------
function suggestExcludes(text){
  const out=[];
  HIGH_CONFLICTS.forEach(p=>{
    if(text.includes(p[0]) && !out.includes(p[1])) out.push(p[1]);
    if(text.includes(p[1]) && !out.includes(p[0])) out.push(p[0]);
  });
  return out.join(", ");
}
function autoParams(emo, genre){
  // rough mapping like server
  let w=0.5, s=0.6, a=0.3;
  if(emo==="epic"||["epic orchestral","symphonic metal","cinematic"].includes(genre)){w=0.35;s=0.8;a=0.3;}
  else if(["ambient","dark ambient","world fusion","downtempo"].includes(genre)){w=0.4;s=0.7;a=0.3;}
  else if(["metal","industrial","punk"].includes(genre)){w=0.45;s=0.7;a=0.2;}
  else if(["indie folk","acoustic","minimalist"].includes(genre)){w=0.3;s=0.7;a=0.2;}
  weird.value=w; styleinf.value=s; audioinf.value=a;
  weirdVal.value=w; styleVal.value=s; audioVal.value=a;
  log(`Auto‑params → W:${w} S:${s} A:${a}`);
}

function genOne(emotion, region, era, extendMode){
  // pick vocal/genre
  const voc = EMOTION_MAP[emotion][0][0];
  const gen = EMOTION_MAP[emotion][1][0];
  const rtag = WORLD_REGIONS[region][0];
  const inst = INSTRUMENT_TAGS[0];
  let text;
  if(extendMode){
    text = `${emotion[0].toUpperCase()+emotion.slice(1)} ${gen} narrative where ${voc} leads, supported by ${inst}; subtle ${rtag} colorations in ${era} aesthetic.`;
  } else {
    text = `${emotion[0].toUpperCase()+emotion.slice(1)} ${voc} over ${gen} with ${rtag} influence, ${inst} accompaniment, ${era} production aesthetic`;
  }
  const excl = suggestExcludes(text);
  autoParams(emotion, gen);
  return {style:text, exclude:excl, emotion, region, era, genre:gen, vocal:voc};
}

document.getElementById("genBtn").onclick=()=>{
  const mode=document.getElementById("mode").value;
  const preset=document.getElementById("preset").value;
  const cnt=parseInt(document.getElementById("count").value||"1");
  const extendMode=document.getElementById("extendToggle").checked;
  const res=[];
  if(mode==="manual"){
    const e=document.getElementById("emotion").value;
    const r=document.getElementById("region").value;
    const era=document.getElementById("era").value;
    for(let i=0;i<cnt;i++) res.push(genOne(e,r,era,extendMode));
  }else{
    for(let i=0;i<cnt;i++){
      const e = CORE_EMOTIONS[Math.floor(Math.random()*CORE_EMOTIONS.length)];
      const r = Object.keys(WORLD_REGIONS)[Math.floor(Math.random()*Object.keys(WORLD_REGIONS).length)];
      const era = ERAS[Math.floor(Math.random()*ERAS.length)];
      res.push(genOne(e,r,era,extendMode));
    }
  }
  // preset hybrid (simple merge of first item)
  if(preset){
    const first = res[0];
    const [e1,e2]=preset.split(" + ").map(x=>x.toLowerCase());
    first.style = `${e1}+${e2} ${first.vocal} over ${first.genre} with ${first.region} flavor`.replace(first.region, Object.keys(WORLD_REGIONS)[0]);
    first.exclude = suggestExcludes(first.style);
  }
  // show first result to boxes
  const one=res[0];
  document.getElementById("styleOut").value = one.style;
  document.getElementById("excludeOut").value = one.exclude;
  saveHistory(one);
  clashCheck();
  log(`Generated ${res.length} prompt(s)`);
  window._lastBatch = res;
};

document.getElementById("gen10").onclick=()=>{
  document.getElementById("count").value=10;
  document.getElementById("genBtn").click();
};

// ---------- clash detector ----------
function clashCheck(){
  const txt=document.getElementById("styleOut").value.toLowerCase();
  let notes=[];
  // simple checks
  const instCount = (txt.match(/guitar|piano|violin|cello|harp|drum|sitar|tabla|synth|brass|flute|duduk|bansuri|oud|qanun|erhu|taiko/g)||[]).length;
  if(instCount>7) notes.push("Too many instruments: consider 4–6 key elements.");
  const vocCount = (txt.match(/vocal|soprano|tenor|alto|choir|falsetto|whisper|growl|raspy/g)||[]).length;
  if(vocCount>4) notes.push("Too many vocal styles: keep 1–2 lead + 1–2 backing.");
  // duplicates
  const dups = [];
  ["epic","orchestral","ambient","cinematic"].forEach(k=>{
    const m = (txt.match(new RegExp(k,"g"))||[]).length; if(m>2) dups.push(k);
  });
  if(dups.length) notes.push("Duplicate tags: "+dups.join(", "));
  // common mistakes rules
  COMMON_MISTAKES.forEach(r=>{ if(r.pattern==="too_many_instruments" && instCount>7) notes.push(`Rule: ${r.rule} → ${r.fix}`); });
  document.getElementById("clashResult").innerHTML = notes.length? "<div class='warnbox small'>"+notes.join("<br>")+"</div>" : "<div class='goodbox small'>No clashes detected.</div>";
}

// ---------- Suggest 3 Alternatives ----------
document.getElementById("suggest3").onclick=()=>{
  const base = document.getElementById("styleOut").value || "Expressive vocals over cinematic world fusion";
  const A = [variationRemix(base,"light"), variationRemix(base,"light"), variationRemix(base,"radical")];
  const box=document.getElementById("suggestBox"); box.innerHTML="";
  A.forEach((t,i)=>{
    const d=document.createElement("div"); d.className="box"; d.innerHTML=`<div class="kbd">${t}</div><div class="row"><button class="btn alt">Use</button></div>`;
    d.querySelector("button").onclick=()=>{document.getElementById("styleOut").value=t; clashCheck(); log(`Applied Suggestion #${i+1}`);};
    box.appendChild(d);
  });
};

// ---------- History Vault ----------
function saveHistory(item){
  const H = JSON.parse(localStorage.getItem("PROMPT_HISTORY")||"[]");
  H.unshift({ts:new Date().toISOString(),...item});
  localStorage.setItem("PROMPT_HISTORY", JSON.stringify(H.slice(0,300)));
  drawHistory();
}
function drawHistory(){
  const list = JSON.parse(localStorage.getItem("PROMPT_HISTORY")||"[]");
  const q = (document.getElementById("hSearch")||{value:""}).value.toLowerCase();
  const box=document.getElementById("historyList");
  box.innerHTML = list.filter(x=>!q || JSON.stringify(x).toLowerCase().includes(q)).slice(0,50)
    .map(x=>`<div class="box small">
      <b>${new Date(x.ts).toLocaleString()}</b> — ${x.emotion}/${x.genre}<br>
      <div class="kbd">${x.style}</div>
      <div class="row"><button class="btn alt" onclick='useHist(${JSON.stringify(x).replace(/'/g,"&#39;")})'>Use</button></div>
    </div>`).join("");
}
function useHist(x){
  document.getElementById("styleOut").value = x.style;
  document.getElementById("excludeOut").value = x.exclude||"";
  autoParams(x.emotion||"epic", x.genre||"cinematic");
  log("Loaded from history");
  clashCheck();
}
document.getElementById("hSearch").oninput=drawHistory;
document.getElementById("hClear").onclick=()=>{localStorage.removeItem("PROMPT_HISTORY"); drawHistory(); log("History cleared");};
drawHistory();

// ---------- Instant Remix ----------
document.getElementById("remixLight").onclick=()=>{
  const base=document.getElementById("styleOut").value; if(!base) return;
  document.getElementById("styleOut").value = base.replace("accompaniment","layers").replace("atmospheric","textural");
  clashCheck(); log("Instant Remix (light)");
};
document.getElementById("remixRad").onclick=()=>{
  const base=document.getElementById("styleOut").value; if(!base) return;
  document.getElementById("styleOut").value = variationRemix(base,"radical");
  clashCheck(); log("Instant Remix (radical)");
};

// ---------- Mastering presets ----------
document.getElementById("applyMaster").onclick=()=>{
  const p = document.getElementById("masterPreset").value;
  if(!p) return;
  const tags = MASTERING_PRESETS[p]||[];
  const st=document.getElementById("styleOut");
  st.value = (st.value+" "+tags.join(" ")).trim();
  log(`Applied mastering preset: ${p}`);
  clashCheck();
};

// ---------- Common mistakes editor ----------
function drawMistakes(){
  const box=document.getElementById("mistakesBox");
  box.innerHTML = COMMON_MISTAKES.map((m,i)=>`<div class="row"><span class="kbd">• ${m.rule}</span><button class="btn bad" onclick="delM(${i})">Del</button></div><div class="small">${m.fix} — ${m.comment||""}</div>`).join("");
}
window.delM=(i)=>{COMMON_MISTAKES.splice(i,1); localStorage.setItem("COMMON_MISTAKES", JSON.stringify(COMMON_MISTAKES)); drawMistakes(); log("Common mistake removed");}
document.getElementById("mAdd").onclick=()=>{
  const r=document.getElementById("mRule").value.trim(), f=document.getElementById("mFix").value.trim(), n=document.getElementById("mNote").value.trim();
  if(!r||!f) return;
  COMMON_MISTAKES.push({pattern:"custom_"+Date.now(), rule:r, fix:f, comment:n});
  localStorage.setItem("COMMON_MISTAKES", JSON.stringify(COMMON_MISTAKES));
  drawMistakes(); log("Common mistake added");
}
drawMistakes();

// ---------- Presets/Lists init ----------
function pushToPrompt(text){
  const st=document.getElementById("styleOut");
  st.value = (st.value+" "+text).trim();
  document.getElementById("previewBox").textContent = st.value;
  log(`Inserted: ${text}`);
  clashCheck();
}

// ---------- Export ----------
document.getElementById("exportTxt").onclick=()=>{
  const style=document.getElementById("styleOut").value, exc=document.getElementById("excludeOut").value;
  const s=`Style Prompt:\n${style}\n\nExclude Styles:\n${exc}\n`;
  fetch("/download_txt",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:s})})
    .then(r=>r.blob()).then(b=>downloadBlob(b,"suno_prompts.txt"));
};
document.getElementById("exportJson").onclick=()=>{
  const batch = window._lastBatch || [];
  const data = batch.length? batch : [{style:document.getElementById("styleOut").value,exclude:document.getElementById("excludeOut").value,ts:new Date().toISOString()}];
  fetch("/download_json",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({data})})
    .then(r=>r.blob()).then(b=>downloadBlob(b,"suno_prompts.json"));
};
function downloadBlob(blob, filename){
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a"); a.href=url; a.download=filename; a.click(); URL.revokeObjectURL(url);
}

// ---------- Strict Mode ----------
const strictToggle=document.getElementById("strictMode");
strictToggle.checked = JSON.parse(localStorage.getItem("STRICT_MODE")||"false");
strictToggle.onchange=()=>{ localStorage.setItem("STRICT_MODE", JSON.stringify(strictToggle.checked)); log(`Strict Mode ${strictToggle.checked?'ON':'OFF'}`); };

// ---------- Compact tags (copy) ----------
const compact = Object.values(SONG_IMPACT_TAGS).flat().join(" ");
document.getElementById("compactTags").textContent = compact;
document.getElementById("copyCompact").onclick=()=>{navigator.clipboard.writeText(compact); log("Compact engineering tags copied");};

// ---------- Auto restore last log ----------
const oldlog = localStorage.getItem("ACTION_LOG"); if(oldlog) document.getElementById("logLines").innerHTML = oldlog;


// ---------- TAG BROWSER ----------
(function initTagBrowser(){
  const grid = document.getElementById("tagGrid");
  const sentinel = document.getElementById("sentinel");
  const search = document.getElementById("tagSearch");
  const onlyEnabled = document.getElementById("onlyEnabled");
  const appendComma = document.getElementById("appendComma");
  const addSelected = document.getElementById("addSelected");
  const clearSelected = document.getElementById("clearSelected");
  const tagStats = document.getElementById("tagStats");
  const slider = document.getElementById("compatSlider");
  const compatVal = document.getElementById("compatVal");
  const hardMode = document.getElementById("hardMode");

  let currentCat = "all";
  let selected = new Set();

  // --- Навигация по категориям
  document.querySelectorAll('[data-cat]').forEach(btn=>{
    btn.onclick = ()=>{ currentCat = btn.dataset.cat; fullRecompute(); };
  });

  // --- Утилиты совместимости/конфликтов (как было)
  function compatScore(tag, cluster){
    if(!cluster.size) return 1;
    let sum=0, n=0;
    for(const s of cluster){
      const a = (CO[s] && CO[s][tag]) || 0;
      const b = (CO[tag] && CO[tag][s]) || 0;
      const v = Math.max(a,b);
      sum += v; n++;
    }
    return n? (sum/n) : 0;
  }
  function hardConflict(tag, cluster, mode, sliderVal){
    if(mode === "off") return false;
    let anyStrong = false;
    let avg = 0, n=0;
    for(const s of cluster){
      const a = (CO[s] && CO[s][tag]) || 0;
      const b = (CO[tag] && CO[tag][s]) || 0;
      const v = Math.max(a,b);
      if(v > (mode==="strict"?0.20:0.10)) anyStrong = true;
      avg += v; n++;
    }
    avg = n?avg/n:0;
    if(mode==="strict") return !anyStrong;
    const th = (sliderVal/200);
    return (!anyStrong) && (avg < th);
  }

  // ---------- FUZZY INDEX ----------
  // Предподготовим нормализованный словарь + простые n-граммы (3-граммы)
  const norm = s => s.toLowerCase().trim();
  const TAG_CATEGORIES = {
    all: ALL_TAGS,
    styles: DEFAULT_STYLE_TAGS,
    instruments: INSTRUMENT_TAGS,
    regions: REGION_TAGS,
    sfx: SFX_TAGS,
    engineering: ENGINEERING_TAGS
  };

  function trigrams(str){
    const s = "  " + str + "  ";
    let out = [];
    for(let i=0;i<s.length-2;i++) out.push(s.slice(i,i+3));
    return out;
  }

  function jaccard(a,b){
    if(a.length===0||b.length===0) return 0;
    const A=new Set(a), B=new Set(b);
    let inter=0;
    for(const x of A) if(B.has(x)) inter++;
    return inter / (A.size + B.size - inter);
  }

  // Быстрый Левенштейн с ранней остановкой (dist>2 нас не интересует)
  function lev2(a,b,maxDist=2){
    if(Math.abs(a.length-b.length)>maxDist) return maxDist+1;
    const dp = Array(b.length+1).fill(0).map((_,i)=>i);
    for(let i=1;i<=a.length;i++){
      let prev=dp[0]; dp[0]=i;
      let best = dp[0];
      for(let j=1;j<=b.length;j++){
        const temp = dp[j];
        dp[j] = (a[i-1]===b[j-1]) ? prev : 1+Math.min(prev, dp[j], dp[j-1]);
        prev = temp;
        if(dp[j]<best) best = dp[j];
      }
      if(best>maxDist) return maxDist+1;
    }
    return dp[b.length];
  }

  // Счёт: комбинация префикс/подстрока/3‑граммы/левенштейн
  function fuzzyScore(query, cand){
    if(!query) return 1; // пустой запрос — все видим
    const q = norm(query), c = norm(cand);
    if(c.startsWith(q)) return 1.0;                // префикс — топ
    if(c.includes(q))  return 0.88;                // подстрока — почти топ
    // n‑gram сходство
    const j = jaccard(trigrams(q), trigrams(c));
    // маленькая поправка на левенштейн (до 2)
    const d = lev2(q, c, 2);
    const l = (d>2) ? 0 : (1 - d/3)*0.25;          // максимум +0.25
    // итоговый
    return Math.max(j*0.8 + l, 0);
  }

  // ---------- ВИРТУАЛИЗАЦИЯ (пакетный DOM) ----------
  const BATCH_SIZE = 300;          // сколько чипов добавлять за раз
  const RERANK_LIMIT = 1200;       // максимум кандидатов после сортировки по score
  let filteredRanked = [];         // {tag, score, disabled}
  let renderedCount = 0;           // сколько отрендерено в grid
  let observer = null;

  // DOM helpers
  function chip(tag, disabled, score){
    const el = document.createElement("span");
    el.className = "tag";
    if(disabled) el.classList.add("disabled");
    if(selected.has(tag)) el.classList.add("sel");
    el.title = `compat ${(score*100).toFixed(0)}%`;
    el.textContent = tag;

    el.onclick = (ev)=>{
      ev.preventDefault();
      if(disabled) return;
      if(selected.has(tag)){ selected.delete(tag); el.classList.remove("sel"); }
      else { selected.add(tag); el.classList.add("sel"); appendToStyle(tag); }
      fullRecompute(); // пересчёт, так как (не)совместимость изменилась
    };
    el.oncontextmenu = (ev)=>{
      ev.preventDefault();
      appendToExclude(tag);
    };
    return el;
  }

  function appendToStyle(tag){
    const st = document.getElementById("styleOut");
    const sep = appendComma.checked ? ", " : " ";
    const needsSep = st.value && !/[,\s]$/.test(st.value);
    st.value = st.value + (needsSep?sep:"") + tag;
  }
  function appendToExclude(tag){
    const ex = document.getElementById("excludeOut");
    const list = ex.value.split(",").map(s=>s.trim()).filter(Boolean);
    if(!list.includes(tag)){ list.push(tag); ex.value = list.join(", "); }
  }
  addSelected.onclick = ()=>{
    if(!selected.size) return;
    const st = document.getElementById("styleOut");
    const arr = Array.from(selected);
    const chunk = appendComma.checked ? arr.join(", ") : arr.join(" ");
    const needsSep = st.value && !/[,\s]$/.test(st.value);
    st.value = st.value + (needsSep? (appendComma.checked?", ":" ") : "") + chunk;
  };
  clearSelected.onclick = ()=>{ selected.clear(); fullRecompute(); };

  // Наблюдатель за сторожком — догружает очередной батч
  function ensureObserver(){
    if(observer) observer.disconnect();
    observer = new IntersectionObserver(entries=>{
      for(const e of entries){
        if(e.isIntersecting){
          renderNextBatch();
        }
      }
    }, {root: null, rootMargin: "600px"});
    observer.observe(sentinel);
  }

  function renderNextBatch(){
    if(renderedCount >= filteredRanked.length) return;
    const target = Math.min(renderedCount + BATCH_SIZE, filteredRanked.length);
    const frag = document.createDocumentFragment();
    for(let i=renderedCount; i<target; i++){
      const item = filteredRanked[i];
      if(onlyEnabled.checked && item.disabled) continue; // «только доступные»
      frag.appendChild(chip(item.tag, item.disabled, item.compat));
    }
    grid.appendChild(frag);
    renderedCount = target;
    updateStats();
  }

  function updateStats(){
    const shown = Math.min(renderedCount, filteredRanked.length);
    const total = filteredRanked.length;
    const sel = selected.size;
    const th = (slider.value/100);
    const disabledCount = filteredRanked.filter(x=>x.disabled).length;
    tagStats.innerHTML = `Категория: ${currentCat} • кандидатов: ${total} • показано: ${shown} • выбрано: ${sel} • порог: <span class="small mono">${(th*100).toFixed(0)}%</span>${disabledCount?` • недоступных: ${disabledCount}`:""}`;
  }

  // Полный пересчёт списка при любой смене условий
  const debounce = (fn, ms=120)=>{ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a),ms); } };
  search.oninput = debounce(()=>fullRecompute(), 100);
  onlyEnabled.onchange = ()=>{ grid.innerHTML=""; renderedCount=0; renderNextBatch(); updateStats(); };
  slider.oninput = ()=>{ compatVal.textContent = slider.value; fullRecompute(); };
  hardMode.onchange = fullRecompute;

  function fullRecompute(){
    const base = (TAG_CATEGORIES && TAG_CATEGORIES[currentCat]) ? TAG_CATEGORIES[currentCat] : ALL_TAGS;
    const q = (search.value||"").toLowerCase().trim();
    const th = (slider.value/100); // 0..1
    const mode = hardMode.value;

    // 1) fuzzy скоринг
    const scored = base.map(tag=>{
      const fz = fuzzyScore(q, tag);  // 0..1
      return { tag, fz };
    }).filter(x=> x.fz > (q ? 0.12 : 0) ); // мягкий отбор при непустом запросе

    // 2) top‑RERANK_LIMIT по fuzzy
    scored.sort((a,b)=> b.fz - a.fz);
    const top = scored.slice(0, RERANK_LIMIT);

    // 3) совместимость/конфликты относительно текущего выбора
    filteredRanked = top.map(it=>{
      const comp = compatScore(it.tag, selected);
      const isHard = hardConflict(it.tag, selected, mode, slider.value);
      const disabled = isHard || (comp < th);
      // общий композитный балл сортировки: сперва fuzzy, затем совместимость
      const rank = it.fz*0.75 + comp*0.25;
      return { tag: it.tag, compat: comp, disabled, rank };
    });

    // 4) сортируем по композитному рангу
    filteredRanked.sort((a,b)=> b.rank - a.rank);

    // 5) сбрасываем рендер и запускаем батчи
    grid.innerHTML = "";
    renderedCount = 0;
    renderNextBatch();
    ensureObserver();
  }

  // инициализация
  compatVal.textContent = slider.value;
  fullRecompute();
})();

</script>
</body>
</html>
"""

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

@app.route("/__raw")
def _raw():
    return Response(PAGE if isinstance(PAGE, str) else repr(type(PAGE)), mimetype="text/plain; charset=utf-8")

# ---------- VIEW ----------
@app.route("/", methods=["GET"])
def index():
    # sanity: PAGE not empty
    if not isinstance(PAGE, str) or len(PAGE.strip()) < 10:
        return "PAGE appears empty or not a string", 500

    ctx = {
        "emotions":CORE_EMOTIONS,
        "emap":EMOTION_MAP,
        "regions":WORLD_REGIONS,
        "eras":ERAS,
        "conflicts":HIGH_CONFLICTS,
        "impact":SONG_IMPACT_TAGS,
        "sfx":SFX,
        "combos":SFX_COMBOS,
        "ecompat":EMOTION_COMPAT,
        "mpresets":MASTERING_PRESETS,
        "mistakes":COMMON_MISTAKES,
        "all_tags":ALL_TAGS,
        "co_weights":CO_CLIENT,
        "all_styles": DEFAULT_STYLE_TAGS,
        "region_tags": REGION_TAGS,
        "sfx_tags": SFX_TAGS,
        "engineering_tags": ENGINEERING_TAGS,
        "all_tags": ALL_TAGS,
        "co_weights": CO_CLIENT,
        "instruments": sorted(INSTRUMENT_TAGS),
        "high_conflicts": list(HIGH_CONFLICTS),
        "DEFAULT_STYLE_TAGS": DEFAULT_STYLE_TAGS,
    }
    # assure JSON-safe before render
    for k, v in ctx.items():
        _assert_jsonable(k, v)

    print(f"[INDEX] PAGE length: {len(PAGE)} chars; tags={len(ALL_TAGS)} styles={len(DEFAULT_STYLE_TAGS)}")
    return render_template_string(PAGE, **ctx)

# ---------- MAIN ----------
if __name__ == "__main__":
    
    print(f"Запущено. Открой: http://127.0.0.1:5000  |  /__ping  /__raw")
    app.run(host="127.0.0.1", port=5000, debug=True)
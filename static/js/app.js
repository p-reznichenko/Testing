// ---------- datasets from server ----------
const DATA = JSON.parse(document.getElementById('app-data').textContent);
const CORE_EMOTIONS = DATA.emotions;
const EMOTION_MAP = DATA.emap;
const WORLD_REGIONS = DATA.regions;
const INSTRUMENT_TAGS = DATA.instruments;
const ERAS = DATA.eras;
const HIGH_CONFLICTS = DATA.conflicts;
const SONG_IMPACT_TAGS = DATA.impact;
const SFX = DATA.sfx;
const SFX_COMBOS = DATA.combos;
const EMOTION_COMPAT = DATA.ecompat;
const MASTERING_PRESETS = DATA.mpresets;
let COMMON_MISTAKES = JSON.parse(localStorage.getItem("COMMON_MISTAKES")||"null") || DATA.mistakes;
const ALL_TAGS = DATA.all_tags || [];
const CO = DATA.co_weights || {};
const REGION_TAGS = Object.values(WORLD_REGIONS||{}).flat();
const SFX_TAGS = Object.values(SFX||{}).flat();
const ENGINEERING_TAGS = Object.values(SONG_IMPACT_TAGS||{}).flat();
const DEFAULT_STYLE_TAGS = DATA.DEFAULT_STYLE_TAGS;


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

document.getElementById("buildExtend").onclick=async()=>{
  const S=gatherSections();
  if(!S.length){ document.getElementById("extendOut").value=""; return; }
  const tags=[];
  S.forEach(s=>{
    [s.emo,s.voc,s.inst,s.fx,s.eng].forEach(v=>{
      if(v){ v.split(",").map(x=>x.trim()).filter(Boolean).forEach(t=>tags.push(t)); }
    });
  });
  const res = await fetch("/build_style", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({tags})});
  const data = await res.json();
  document.getElementById("styleOut").value = data.description || "";
  document.getElementById("excludeOut").value = (data.excludes || []).join(", ");
  document.getElementById("extendOut").value = data.description || "";
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

// ---------- Lyric generator ----------
const lyrBtn = document.getElementById("genLyrics");
if (lyrBtn) {
  lyrBtn.onclick = async () => {
    const idea = document.getElementById("lyricIdea").value;
    const res = await fetch("/lyrics", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({idea})
    });
    const data = await res.json();
    document.getElementById("lyricResult").textContent = data.lyrics || "";
  };
}


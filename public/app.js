"use strict";
const $=id=>document.getElementById(id);
const CATEGORIES=["Persona","Changed assistant","Off-topic","Incoherent","Normal Talkie","Unrated"];
const COLORS={Persona:"#ff9200","Changed assistant":"#7873d4","Off-topic":"#50a9a2",Incoherent:"#d37d8d","Normal Talkie":"#a9afb8",Unrated:"#99939c"};
let data={manifest:{},singles:[],pairs:[],controls:[],attempts:[],retests:{}},view="single",atlasSign=1,activeCats=new Set(CATEGORIES),atlasCats=new Set(CATEGORIES),limit=48,current=null,filtered=[],points=[],heroRows=[],heroIndex=0,parentFilter=null,lookupInitialized=false,curated=true;
let heroTimer=null,heroHovered=false,heroIcons=new Set(),heroAnimations=[],heroPointerStart=null;
const heroMotion=matchMedia('(prefers-reduced-motion: reduce)');
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const judge=r=>{const j=r.judge||{name:"Unjudged reply",category:"Normal Talkie",description:"",tags:[],weirdness:0,coherence:0};return r.ranking?{...j,weirdness:r.ranking.weirdness,coherence:r.ranking.readability,richness:r.ranking.richness}:{...j,richness:0};};
const alpha=r=>r.edits?.[0]?.[3]??0;
const pairDose=r=>{const f=r.factors||[r.factor??1,r.factor??1];return f[0]===f[1]?`${f[0]}× each`:`${f[0]}× / ${f[1]}×`;};
const meta=r=>r.kind==="pair"?`${pairDose(r)} of solo strength`:`L${r.layer} · N${r.neuron} · ${r.sign>0?"+":"−"}`;
const normalizeReply=text=>String(text??"").trim().toLowerCase().replace(/\s+/g," ");
const controlByBatch=new Map();
const isHighlight=r=>{if(r.run==="pair-strength-study")return r.strength_featured===true;if(r.run==="novelty-sprint")return r.sprint_featured===true;if(r.kind==="pair"&&data.pair_curation)return r.featured===true;const j=judge(r),readable=Boolean(r.text.trim())&&r.termination!=="repeating"&&normalizeReply(r.text)!==normalizeReply(controlByBatch.get(r.batch)??"");if(r.kind==="pair"&&r.mix)return readable&&j.coherence>=5&&((r.mix.outcome==="Blend"&&r.mix.novelty>=5&&r.mix.blending>=3)||(r.mix.outcome==="New outcome"&&r.mix.novelty>=6&&j.weirdness>=4));return r.ranking?readable&&j.coherence>=5&&j.weirdness>=4&&j.richness>=3:readable&&j.coherence>=7&&j.weirdness>=4;};
const mixRank=r=>(r.strength_featured?200000000-r.featured_order*1000:0)+(r.sprint_featured?100000000-r.featured_order*1000:0)+(r.featured?100000-(r.featured_order||0)*1000:0)+(["Blend","New outcome"].includes(r.mix?.outcome)?100:0)+(r.mix?.novelty||0)*4+(r.mix?.blending||0)*2;
// An editorial selection, in display order; the library still contains every result.
const HERO_FEATURES=[
  [38,13442,-1], // Egyptian sin-cleanser
  [28,7376,1],   // Napoleon
  [28,8032,-1],  // Rebellion personified
  [22,179,-1],   // John Bull
  [33,2024,-1],  // Silence
  [28,12658,-1], // Mayor of Vanity
  [38,1287,1],   // Water-hen
  [35,8574,1],   // Infinite space personified
  [17,10423,-1], // Departed Spirit
  [34,11010,-1], // Right-Angled Triangle
  [26,2157,1],   // Principal meridian
  [29,5037,1],   // Green algae
  [23,5861,-1],  // King of beasts
];
function selectHeroRows(rows){
  const eligible=new Map(rows.filter(r=>r.text.trim()&&r.termination!=='repeating'&&(r.sprint_featured||judge(r).coherence>=5)&&judge(r).category==='Persona'&&r.canonical!==false).map(r=>[`${r.layer}/${r.neuron}/${r.sign}`,r]));
  const original=HERO_FEATURES.map(parts=>eligible.get(parts.join('/'))).filter(Boolean);
  const fresh=rows.filter(r=>r.sprint_featured).sort((a,b)=>a.featured_order-b.featured_order);
  return [...original.slice(0,3),...fresh,...original.slice(3)];
}
function sharePath(row){
  if(row.path)return row.path;
  if(row.unlisted)return null;
  if(row.kind==='pair'){
    const parents=(row.parents||[]).map(findRow);
    if(parents.length!==2||parents.some(p=>!p))return null;
    return 'p/'+parents.map(p=>`${p.layer}-${p.neuron}-${p.sign>0?'up':'down'}`).join('_')+'/';
  }
  if(row.kind==='single'&&Number.isInteger(row.layer)&&Number.isInteger(row.neuron))return `n/${row.layer}-${row.neuron}-${row.sign>0?'up':'down'}/`;
  return null;
}
function shareURL(row){
  const home=document.querySelector('link[rel="canonical"]')?.href||new URL('./',location.href).href;
  const path=sharePath(row);
  return path?new URL(path,home).href:null;
}
function updateCurationButtons(){for(const b of $("curation-tabs").children){const on=(b.dataset.curated==="true")===curated;b.classList.toggle("active",on);b.setAttribute("aria-pressed",on);}}
const short=(text,n=220)=>text.length>n?text.slice(0,n).trimEnd()+"…":text;
function setup(){
  $("categories").innerHTML=CATEGORIES.map(c=>`<button class="active" data-cat="${esc(c)}" style="--cat:${COLORS[c]}" aria-pressed="true"><i></i>${esc(c)}</button>`).join("");
  $("categories").onclick=e=>{const b=e.target.closest("[data-cat]");if(!b)return;const c=b.dataset.cat;activeCats.has(c)?activeCats.delete(c):activeCats.add(c);b.classList.toggle("active",activeCats.has(c));b.setAttribute("aria-pressed",activeCats.has(c));limit=48;renderLibrary();};
  $("atlas-sign").onclick=e=>{const b=e.target.closest("[data-sign]");if(!b)return;atlasSign=+b.dataset.sign;for(const n of $("atlas-sign").children){n.classList.toggle("active",n===b);n.setAttribute("aria-pressed",n===b);}renderAtlas();};
  $("view-tabs").onclick=e=>{const b=e.target.closest("[data-view]");if(!b)return;view=b.dataset.view;history.replaceState(null,"",location.pathname+location.search+(view==="pair"?"#pairs":view==="discoveries"?"#discoveries":"#library"));for(const n of $("view-tabs").children){n.classList.toggle("active",n===b);n.setAttribute("aria-pressed",n===b);}limit=48;renderLibrary();};
  for(const id of ["search","direction","layer-min","layer-max","strength","weirdness","sort","unique"]){$(id).addEventListener("input",()=>{limit=48;$("weirdness-value").value=$("weirdness").value;renderLibrary();});}
  $("more").onclick=()=>{limit+=48;renderLibrary();};
  $("reset").onclick=()=>{parentFilter=null;curated=true;updateCurationButtons();for(const [id,v] of Object.entries({search:"",direction:"0","layer-min":"0","layer-max":"39",strength:"all",weirdness:"0",sort:"weird"}))$(id).value=v;$("weirdness-value").value=0;$("unique").checked=true;activeCats=new Set(CATEGORIES);for(const n of $("categories").children){n.classList.add("active");n.setAttribute("aria-pressed","true");}limit=48;renderLibrary();};
  $("lookup-open").onclick=()=>{const l=+$("lookup-layer").value,n=+$("lookup-unit").value;const rows=data.singles.filter(r=>r.layer===l&&r.neuron===n);if(rows.length){$("lookup-message").textContent="";openDetail(rows.find(r=>r.sign===atlasSign)||rows[0]);}else $("lookup-message").textContent="This neuron was not sampled. Try a colored dot in the atlas.";};
  $("curation-tabs").onclick=e=>{const b=e.target.closest("[data-curated]");if(!b)return;curated=b.dataset.curated==="true";if(!curated&&view==="pair")$("unique").checked=false;updateCurationButtons();limit=48;renderLibrary();};
  $("csv").onclick=downloadCSV;$("close-detail").onclick=()=>$("detail").close();
  $("detail").addEventListener("click",e=>{if(e.target===$("detail")){const r=$("detail").getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$("detail").close();}});
  $("detail").addEventListener("close",()=>{if(location.hash.startsWith("#id="))history.replaceState(null,"",location.pathname+location.search+(view==="pair"?"#pairs":view==="discoveries"?"#discoveries":"#library"));});
  $("share").onclick=async()=>{if(!current)return;const url=shareURL(current);if(!url){$("share-status").textContent='This control or retry is available in the full data download.';return;}try{await navigator.clipboard.writeText(url);$("share-status").textContent="Link copied";}catch{$("share-status").textContent=url;}};
  $("control-open").onclick=()=>{if(data.controls.length)openDetail(data.controls[0]);};$("hero-open").onclick=()=>{if(heroRows.length)openDetail(heroRows[heroIndex%heroRows.length]);};
  $("hero-prev").onclick=()=>changeHero(-1,true);
  $("hero-next").onclick=()=>changeHero(1,true);
  const heroChat=document.querySelector('.hero-chat');
  heroChat.addEventListener('mouseenter',()=>{heroHovered=true;scheduleHero();});
  heroChat.addEventListener('mouseleave',()=>{heroHovered=false;scheduleHero();});
  heroChat.addEventListener('focusin',()=>clearTimeout(heroTimer));
  heroChat.addEventListener('focusout',e=>{if(!heroChat.contains(e.relatedTarget))scheduleHero();});
  heroChat.addEventListener('keydown',e=>{if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();changeHero(e.key==='ArrowLeft'?-1:1,true);}});
  heroChat.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'&&e.isPrimary&&!e.target.closest('button,a'))heroPointerStart={x:e.clientX,y:e.clientY};});
  heroChat.addEventListener('pointercancel',()=>{heroPointerStart=null;});
  heroChat.addEventListener('pointerup',e=>{if(!heroPointerStart||e.pointerType!=='touch'||!e.isPrimary)return;const dx=e.clientX-heroPointerStart.x,dy=e.clientY-heroPointerStart.y;heroPointerStart=null;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.5)changeHero(dx<0?1:-1,true);});
  document.addEventListener('visibilitychange',scheduleHero);
  heroMotion.addEventListener('change',scheduleHero);
  $("detail").addEventListener('close',scheduleHero);
  $("hero-icon").onerror=()=>{$("hero-icon").hidden=true;};
  window.addEventListener("resize",drawMap);window.addEventListener("themechange",drawMap);window.addEventListener("hashchange",openHash);
  const canvas=$("map");canvas.addEventListener("mousemove",e=>{const p=hit(e);canvas.style.cursor=p?"pointer":"crosshair";$("tooltip").hidden=!p;if(p){$("tooltip").textContent=`L${p.row.layer} · N${p.row.neuron} · ${judge(p.row).name}`;const b=canvas.getBoundingClientRect();$("tooltip").style.left=Math.min(e.clientX-b.left+10,b.width-230)+"px";$("tooltip").style.top=(e.clientY-b.top+12)+"px";}});canvas.addEventListener("mouseleave",()=>$("tooltip").hidden=true);canvas.addEventListener("click",e=>{const p=hit(e);if(p)openDetail(p.row);});
}
function renderLibrary(){
  const allRows=view==="discoveries"?[...data.singles,...data.pairs].filter(r=>r.sprint_featured||r.strength_featured):view==="single"?data.singles:data.pairs;
  document.querySelector(".judge-label").textContent="Earlier ratings: Luna · New ratings: Codex";
  $("sort").querySelector('[value="rich"]').hidden=view!=="single";
  if(view!=="single"&&$("sort").value==="rich")$("sort").value="weird";
  $("sort").querySelector('[value="weird"]').textContent=view==="single"?"Selected & weirdest":"Selected discoveries first";
  $("curation-note").textContent=view==="discoveries"?"Selected discoveries from the larger search and the strength study. Weirdness and coherence rated by Codex on full saved replies. Open a strength result to compare its other doses.":curated&&view==="pair"?"Surprising new personas and earlier reader favorites. Each chosen reply is linked to its exact solo parents; all strength trials and failures remain in All results.":curated?"New editorial selections appear first, followed by the earlier Luna-rated highlights. Earlier Luna ratings are preserved; the new discoveries have separate Codex ratings.":"All results preserves strength variants, reruns, repetition and failures. New unscored trials are labelled Unrated. Other filters still apply.";
  for(const id of ["direction","layer-min","strength"])$(id).closest("label").hidden=view!=="single";
  $("parent-filter").hidden=!(view==="pair"&&parentFilter);
  if(parentFilter){$("parent-filter").innerHTML=`<button id="clear-parent">With ${esc(judge(findRow(parentFilter)).name)} ×</button>`;$("clear-parent").onclick=()=>{parentFilter=null;renderLibrary();};}
  const query=$("search").value.trim().toLowerCase(),dir=+$("direction").value,min=+$("layer-min").value,max=+$("layer-max").value,st=$("strength").value,w=+$("weirdness").value;
  let rows=allRows.filter(r=>{const j=judge(r);return (!curated||isHighlight(r))&&(view!=="pair"||!parentFilter||r.parents?.includes(parentFilter))&&activeCats.has(j.category)&&(w===0||(Number.isFinite(j.weirdness)&&j.weirdness>=w))&&(view==="discoveries"||!dir||r.kind==="pair"||r.sign===dir)&&(view==="discoveries"||r.kind==="pair"||r.layer>=min&&r.layer<=max)&&(view==="discoveries"||st==="all"||alpha(r)===+st)&&(!query||[j.name,j.description,...j.tags,r.text,meta(r)].join(" ").toLowerCase().includes(query));});
  const sort=$("sort").value;rows.sort((a,b)=>{const x=judge(a),y=judge(b);if(sort==="coherent")return y.coherence-x.coherence||(y.richness||0)-(x.richness||0)||y.weirdness-x.weirdness;if(sort==="rich")return (y.richness||0)-(x.richness||0)||y.weirdness-x.weirdness||y.coherence-x.coherence;if(sort==="both")return y.coherence*y.weirdness-x.coherence*x.weirdness||(y.richness||0)-(x.richness||0);if(sort==="layer")return (a.layer??0)-(b.layer??0)||(a.neuron??0)-(b.neuron??0);return (mixRank(b)-mixRank(a))||y.weirdness-x.weirdness||(y.richness||0)-(x.richness||0)||y.coherence-x.coherence;});
  const total=rows.length;if(curated){const seenText=new Set();rows=rows.filter(r=>{const t=normalizeReply(r.text);if(seenText.has(t))return false;seenText.add(t);return true;});}if($("unique").checked){const seen=new Set();rows=rows.filter(r=>{const n=judge(r).name.toLowerCase();if(seen.has(n))return false;seen.add(n);return true;});}filtered=rows;
  $("result-count").textContent=`${rows.length.toLocaleString()} ${$("unique").checked?(rows.length===1?"name":"names"):(rows.length===1?"reply":"replies")} from ${total.toLocaleString()} ${view==="single"?(total===1?"direction":"directions"):(view==="discoveries"?"discoveries":total===1?"trial":"trials")}${curated?` · ${allRows.length} total available`:""}`;
  $("pair-note").hidden=view!=="pair";$("pair-note").textContent=data.pairs.length?`${data.pairs.length.toLocaleString()} saved pair trials. The strength study adds ${data.strength_study?.pair_trials?.toLocaleString()||0} trials across ${data.strength_study?.pairs||0} pairs. The earlier novelty search added ${data.novelty_sprint?.pair_replies?.toLocaleString()||0} trials. Each strength and longer rerun has its own share link. Earlier Luna comparison labels and newer editorial notes remain distinct. ${curated?"Switch to All results for every tested pair, including failures and outcomes resembling a parent.":"All tested pairs appear here, including failures and outcomes resembling a parent."}`:data.status.phase!=="complete"?"Pair generation is queued after the single-neuron screen. Selected candidates will be retested, then combined at their individual strengths and weaker shared settings.":"No eligible combinations in this sample. Pairs require at least two candidates with consistent identities on retest.";
  $("cards").innerHTML=rows.length?rows.slice(0,limit).map(r=>{const j=judge(r);return `<button class="card" data-id="${esc(r.id)}" style="--cat:${COLORS[j.category]}"><div class="card-meta">${esc(meta(r))}</div><div class="badge">${esc(j.category)}</div>${r.kind==="pair"?`<div class="pair-parents">${(r.parents||[]).map(id=>esc(judge(findRow(id)).name)).join(" <span>+</span> ")}</div>`:""}<h3>${esc(j.name)}</h3><p class="excerpt">${esc(short(r.text))}</p><div class="card-bottom"><span>${r.kind==="pair"?esc(pairDose(r)):alpha(r)+"×"} · ${r.editorial_rating?"weirdness "+j.weirdness+"/10":r.kind==="pair"&&r.mix?esc(r.mix.outcome):(r.judge?.rated===false?r.review_status:"weirdness "+j.weirdness)}</span><span>${esc(r.termination)} · ${Number.isFinite(j.coherence)?(r.editorial_rating?"coherence ":"readability ")+j.coherence+"/10":"Not numerically rated"}</span></div></button>`;}).join(""):`<div class="empty">${view==="pair"&&!data.pairs.length&&data.status.phase!=="complete"?"The two-neuron results will appear here after the single-neuron screen and candidate retests.":data.singles.length?"No replies match these filters. Try All results, Reset, or another view.":"The local sample is still being generated. Saved replies will appear when the run is exported."}</div>`;
  $("cards").onclick=e=>{const b=e.target.closest("[data-id]");if(b)openDetail(findRow(b.dataset.id));};$("more").hidden=rows.length<=limit;
}
function findRow(id){return [...data.singles,...data.pairs,...data.controls,...data.attempts].find(r=>r.id===id);}
function openDetail(r){if(!r)return;current=r;const j=judge(r);$("detail-ranking").hidden=!r.ranking&&!r.editorial;$("detail-ranking").textContent=r.ranking?`Luna v2 · detail ${j.richness}/10. ${r.ranking.reason} Original v1: weirdness ${r.judge.weirdness}/10, coherence ${r.judge.coherence}/10.`:"";if(r.editorial)$("detail-ranking").textContent="Codex editorial review · "+r.editorial.reason+(r.editorial_rating?" Weirdness and coherence rated by Codex on the full reply; earlier Luna scores use a separate rubric.":" No numerical ratings assigned.");$("detail-kicker").textContent=r.kind==="pair"?"Two neurons pushed at once":r.kind==="control"?"Unsteered control · same prompt":meta(r);$("detail-title").textContent=j.name;$("detail-description").textContent=r.featured_reason||j.description;$("detail-prompt").textContent=r.prompt||"Who are you?";$("detail-reply").textContent=r.text||"[Empty response]";const pairNovelty=r.kind==="pair"&&Number.isFinite(r.mix?.novelty);const interest=pairNovelty?r.mix.novelty:j.weirdness;$("detail-weirdness-label").textContent=pairNovelty?"Newness vs. parents":"Weirdness";$("detail-weirdness").textContent=Number.isFinite(interest)?"▰".repeat(interest)+"▱".repeat(10-interest)+` ${interest}`:"Not numerically rated";($("detail-coherence-label")||$("detail-coherence").previousElementSibling).textContent=r.editorial_rating?"Coherence":"Readability";$("detail-coherence").textContent=Number.isFinite(j.coherence)?j.coherence+"/10":"Not numerically rated";$("detail-termination").textContent=r.termination==="length"?`Cut off at ${r.n_tokens??r.token_ids?.length??r.max_tokens??160} tokens`:r.termination;$("detail-strength").textContent=r.kind==="control"?"No intervention":r.kind==="pair"?`${pairDose(r)} of parent solo strengths (left to right)`:alpha(r)+"× median residual norm";$("detail-tags").textContent=j.tags.join(" · ");$("share-status").textContent="";
  const parents=(r.parents||(r.source_id?[r.source_id]:[])).map(findRow).filter(Boolean);$("parent-chips").innerHTML=parents.map((p,i)=>`${i?"<span>+</span>":""}<button data-parent="${esc(p.id)}">${esc(judge(p).name)}<small>${esc(meta(p))}</small></button>`).join("");$("parent-chips").onclick=e=>{const b=e.target.closest("[data-parent]");if(b)openDetail(findRow(b.dataset.parent));};
  $("detail-parent-text").textContent=parents.map(p=>`Alone, ${judge(p).name} said “${short(p.text,150)}”`).join("\n\n")+(r.mix?"\n\nPair comparison: "+r.mix.reason:"");
  const attempts=data.attempts.filter(a=>r.key&&a.key===r.key&&a.kind===r.kind);$("detail-attempts").innerHTML=attempts.length>1?`<p>Saved attempts</p><table><thead><tr><th>Strength</th><th>Coherence</th><th>Reply</th></tr></thead><tbody>${attempts.map(a=>`<tr><td>${a.kind==="pair"?pairDose(a):alpha(a)+"×"}</td><td>${Number.isFinite(judge(a).coherence)?judge(a).coherence+"/10":"Not rated"}</td><td><button data-attempt="${esc(a.id)}">Read ${esc(judge(a).name)}</button></td></tr>`).join("")}</tbody></table>`:"";const probes=r.kind==="single"?data.attempts.filter(a=>a.source_id===r.id&&["retest","cross_prompt"].includes(a.kind)):[];if(probes.length)$("detail-attempts").innerHTML+=`<p>Follow-up tests of this intervention</p><ul>${probes.map(a=>`<li><button data-attempt="${esc(a.id)}">${esc(a.prompt||"Who are you?")}</button> · ${esc(judge(a).name)}</li>`).join("")}</ul>`;const report=data.repeatability_reports?.[r.id];if(report&&/^repeatability\/[a-z0-9-]+\/$/.test(report.url))$("detail-attempts").innerHTML+=`<p><a class="text-button" href="${esc(report.url)}">${esc(report.label)} ↗</a></p>`;$("detail-attempts").onclick=e=>{const b=e.target.closest("[data-attempt]");if(b)openDetail(data.attempts.find(a=>a.id===b.dataset.attempt));};
  $("explore-pairs").hidden=r.kind!=="single"||!data.pairs.some(p=>p.parents?.includes(r.id));$("explore-pairs").onclick=()=>{parentFilter=r.id;view="pair";$("detail").close();for(const n of $("view-tabs").children){const on=n.dataset.view==="pair";n.classList.toggle("active",on);n.setAttribute("aria-pressed",on);}$("search").value="";renderLibrary();$("library").scrollIntoView({behavior:"smooth"});};
  if($("detail-compare")){$("detail-compare").hidden=!r.strength_comparison;if(r.strength_comparison)$("detail-compare").href=r.strength_comparison;}history.replaceState(null,"",location.pathname+location.search+"#id="+encodeURIComponent(r.id));if(!$("detail").open)$("detail").showModal();
}
function openHash(){if(location.hash==="#discoveries"){view="discoveries";for(const n of $("view-tabs").children){const on=n.dataset.view===view;n.classList.toggle("active",on);n.setAttribute("aria-pressed",on);}renderLibrary();$("library").scrollIntoView();}if(location.hash==="#pairs"){const entering=view!=="pair";view="pair";for(const n of $("view-tabs").children){const on=n.dataset.view==="pair";n.classList.toggle("active",on);n.setAttribute("aria-pressed",on);}renderLibrary();if(entering)$("library").scrollIntoView();}if(location.hash.startsWith("#id=")){try{openDetail(findRow(decodeURIComponent(location.hash.slice(4))));}catch{}}}
function renderAtlas(){const rows=data.singles.filter(r=>r.sign===atlasSign&&r.canonical!==false);$("legend").innerHTML=CATEGORIES.map(c=>`<button data-cat="${esc(c)}" class="${atlasCats.has(c)?"":"dim"}" aria-pressed="${atlasCats.has(c)}"><i style="--cat:${COLORS[c]}"></i>${esc(c)} <em>${rows.filter(r=>judge(r).category===c).length}</em></button>`).join("")+`<span class="muted small">· Gray = no listed entry</span>`;$("legend").onclick=e=>{const b=e.target.closest("[data-cat]");if(!b)return;const c=b.dataset.cat;atlasCats.has(c)?atlasCats.delete(c):atlasCats.add(c);renderAtlas();};drawMap();$("bars").innerHTML=Array.from({length:40},(_,l)=>{const rs=rows.filter(r=>r.layer===l),n=rs.filter(r=>judge(r).category==="Persona").length,p=rs.length?n/rs.length:0;return `<button class="bar" data-layer="${l}" aria-label="Layer ${l}: ${n} of ${rs.length} sampled neurons labeled Persona" title="Layer ${l}: ${n}/${rs.length}"><span class="bar-fill" style="height:${p*100}px"></span><span>${l}</span></button>`;}).join("");$("bars").onclick=e=>{const b=e.target.closest("[data-layer]");if(b){$("layer-min").value=b.dataset.layer;$("layer-max").value=b.dataset.layer;view="single";for(const n of $("view-tabs").children){const on=n.dataset.view==="single";n.classList.toggle("active",on);n.setAttribute("aria-pressed",on);}renderLibrary();$("library").scrollIntoView({behavior:"smooth"});}};}
function drawMap(){const canvas=$("map"),width=canvas.parentElement.clientWidth;if(!width)return;const cols=width<600?4:8,gap=10,cell=(width-gap*(cols-1))/cols,h=cell*.88,rows=Math.ceil(40/cols),height=rows*(h+gap);canvas.style.height=height+"px";const dpr=devicePixelRatio||1;canvas.width=width*dpr;canvas.height=height*dpr;const ctx=canvas.getContext("2d"),dark=document.documentElement.dataset.theme==="dark";ctx.scale(dpr,dpr);ctx.clearRect(0,0,width,height);points=[];for(let l=0;l<40;l++){const x=(l%cols)*(cell+gap),y=Math.floor(l/cols)*(h+gap);ctx.fillStyle=dark?"#1c1c1f":"#f7f7f9";ctx.beginPath();ctx.roundRect(x,y,cell,h,7);ctx.fill();ctx.fillStyle=dark?"#77777e":"#a0a0a7";ctx.font="10px -apple-system,sans-serif";ctx.fillText("L"+l,x+8,y+14);ctx.fillStyle=dark?"#3a3a3f":"#dedee3";for(let yy=y+23;yy<y+h-5;yy+=4)for(let xx=x+7;xx<x+cell-5;xx+=4){ctx.beginPath();ctx.arc(xx,yy,.5,0,Math.PI*2);ctx.fill();}}
  for(const r of data.singles.filter(r=>r.sign===atlasSign&&r.canonical!==false)){const l=r.layer,x=(l%cols)*(cell+gap),y=Math.floor(l/cols)*(h+gap),xx=x+8+(r.neuron%116)/115*(cell-16),yy=y+25+Math.floor(r.neuron/116)/118*(h-33);if(!atlasCats.has(judge(r).category))continue;ctx.fillStyle=COLORS[judge(r).category];ctx.beginPath();ctx.arc(xx,yy,3.1,0,Math.PI*2);ctx.fill();points.push({x:xx,y:yy,row:r});}}
function hit(e){const b=$("map").getBoundingClientRect(),x=e.clientX-b.left,y=e.clientY-b.top;return points.map(p=>({...p,d:Math.hypot(p.x-x,p.y-y)})).filter(p=>p.d<9).sort((a,b)=>a.d-b.d)[0];}
function downloadCSV(){const fields=["id","layer","neuron","sign","strength","category","name","description","weirdness","readability","richness","original_weirdness","original_coherence","ranking_version","termination","parents","pair_factor","parent_factors","pair_outcome","pair_novelty","pair_blending","text"];const q=v=>'"'+String(v??"").replace(/"/g,'""')+'"';const csv=[fields.join(","),...filtered.map(r=>[r.id,r.layer,r.neuron,r.sign,alpha(r),judge(r).category,judge(r).name,judge(r).description,judge(r).weirdness,judge(r).coherence,r.ranking?.richness??"",r.judge?.weirdness,r.judge?.coherence,r.editorial_rating?"Codex v1":r.ranking?.version||"v1",r.termination,(r.parents||[]).map(id=>judge(findRow(id)).name).join(" + "),r.factor??"",r.factors?.join(" / ")??"",r.mix?.outcome,r.mix?.novelty,r.mix?.blending,r.text].map(q).join(","))].join("\r\n");const a=document.createElement("a"),url=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));a.href=url;a.download="talkie-neuron-sample-"+view+".csv";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function renderHero(animate=false,direction=1){
  const count=heroRows.length;
  $("hero-prev").disabled=$("hero-next").disabled=count<2;
  if(!count){$("hero-icon").hidden=true;$("hero-open").hidden=true;$("hero-position").textContent='';$("hero-caption").textContent='Saved replies';$("hero-answer").textContent='No highlights are available yet. You can still explore the library below.';$("hero-label").textContent='Explore the library';return;}
  heroIndex=((heroIndex%count)+count)%count;
  const r=heroRows[heroIndex];
  $("hero-caption").textContent=`Talkie–1930, layer ${r.layer} neuron ${r.neuron} pushed ${r.sign>0?"up":"down"}`;
  $("hero-answer").textContent=r.text;
  $("hero-answer").scrollTop=0;
  $("hero-label").innerHTML=`<span class="persona-name">${esc(judge(r).name)}</span><span class="hero-dose">${esc(alpha(r))}× strength</span>`;
  const icon=`icons/${r.layer}-${r.neuron}-${r.sign>0?'up':'down'}.svg`;
  $("hero-icon").hidden=!heroIcons.has(icon);
  if(heroIcons.has(icon))$("hero-icon").src=icon;
  $("hero-position").textContent=`${heroIndex+1}/${count}`;
  $("hero-position").setAttribute('aria-label',`Highlight ${heroIndex+1} of ${count}`);
  $("hero-open").hidden=false;
  for(const animation of heroAnimations)animation.cancel();
  heroAnimations=[];
  if(animate&&!heroMotion.matches){
    const x=direction<0?-7:7;
    heroAnimations=[$("hero-answer"),document.querySelector('.hero-identity')].map(el=>el.animate([{opacity:.35,transform:`translateX(${x}px)`},{opacity:1,transform:'translateX(0)'}],{duration:220,easing:'cubic-bezier(.2,.7,.3,1)'}));
  }
  for(const offset of [-1,1]){
    const neighbor=heroRows[(heroIndex+offset+count)%count];
    const path=`icons/${neighbor.layer}-${neighbor.neuron}-${neighbor.sign>0?'up':'down'}.svg`;
    if(heroIcons.has(path)){const preload=new Image();preload.src=path;}
  }
}
function changeHero(step,manual=false){
  if(heroRows.length<2)return;
  heroIndex=(heroIndex+step+heroRows.length)%heroRows.length;
  renderHero(true,step);
  if(manual)$("hero-status").textContent=`Highlight ${heroIndex+1} of ${heroRows.length}: ${judge(heroRows[heroIndex]).name}.`;
  scheduleHero();
}
function scheduleHero(){
  clearTimeout(heroTimer);
  if(heroRows.length<2||document.hidden||heroMotion.matches||heroHovered||$("detail").open||document.querySelector('.hero-chat').contains(document.activeElement))return;
  heroTimer=setTimeout(()=>{if(!$("detail").open)changeHero(1);else scheduleHero();},9000);
}
async function load(){try{const response=await fetch("site.json",{cache:"no-cache"});if(!response.ok)throw Error("Saved data unavailable");data=await response.json();if(data.slim)data.attempts=[...data.attempts,...data.singles,...data.pairs,...data.controls];data.repeatability_reports=await fetch("repeatability/index.json",{cache:"no-cache"}).then(r=>r.ok?r.json():{}).catch(()=>({}));controlByBatch.clear();for(const r of data.controls)controlByBatch.set(r.batch,r.text);const m=data.manifest||{};if($("method-strength")&&m.runs)$("method-strength").textContent="Pilot: 1.25× → 1× → 0.75× → 0.5×. Discovery: 1.25× → 0.5× after a time-limited checkpoint. Keep the strongest tested reply with coherence ≥5, otherwise the last attempt. Novelty sprint: fixed discovery-dose sweeps, then pair trials scaled to each parent’s tested solo dose; see the larger-search record above.";if($("method-sample"))$("method-sample").textContent=(m.sampling||"10 random neurons per layer")+" Seeds: "+(m.seeds||[m.seed]).join(", ")+".";if(data.singles.length){$("scale-summary").textContent=`${m.tested_directions.toLocaleString()} tested signed directions · ${data.singles.length.toLocaleString()} library solo entries · ${data.attempts.length.toLocaleString()} saved replies including all pair trials.`;$("control-summary").textContent=`${data.controls.length} unsteered same-batch controls. ${new Set(data.controls.map(r=>r.text)).size} distinct exact ${new Set(data.controls.map(r=>r.text)).size===1?"reply":"replies"} across batches. Control identity labels describe the baseline, not discovered personas.`;$("updated").textContent="Run started "+new Date(m.created).toLocaleString()+" · Seeds "+(m.seeds||[m.seed]).join(", ");const previousHeroId=heroRows[heroIndex]?.id;heroRows=selectHeroRows(data.singles);const previousHeroIndex=heroRows.findIndex(r=>r.id===previousHeroId);heroIndex=previousHeroIndex>=0?previousHeroIndex:0;renderHero();if(!lookupInitialized){const pick=heroRows[0]||data.singles[0];$("lookup-layer").value=pick.layer;$("lookup-unit").value=pick.neuron;lookupInitialized=true;}}renderLibrary();renderAtlas();openHash();scheduleHero();}catch(e){$("result-count").textContent="Saved data could not be loaded.";$("cards").innerHTML='<div class="empty">'+esc(e.message)+". Reload to try again.</div>";}}
setup();load();scheduleHero();
fetch('footer-personas.json').then(r=>r.ok?r.json():[]).then(personas=>{heroIcons=new Set(personas.map(p=>p.icon).filter(icon=>/^icons\/\d+-\d+-(up|down)\.svg$/.test(icon)));renderHero();}).catch(()=>{});

setInterval(()=>{if(data.status.phase!=="complete")load();},30000);

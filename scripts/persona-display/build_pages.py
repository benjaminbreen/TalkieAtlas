"""Build the crawlable parts of the static site from dist/data.json.

Writes, inside dist/:
  site.json            data.json without token ids, for the library page
  n/<slug>/index.html  one page per single neuron direction (e.g. n/24-3883-up/)
  p/<slug>/index.html  one page per pair (e.g. p/23-3070-down_24-2054-up/)
  about/index.html     from templates/about.html
  slugs.json, sitemap.xml, robots.txt
and build/og-jobs.json, which render_og.mjs turns into dist/og/*.png.

Link previews need absolute image URLs, so pass the deployed origin:
  .venv/bin/python sites/talkie-neuron-sample/build_pages.py --site-url https://example.vercel.app
"""
import argparse, hashlib, json, os, re, shutil
from html import escape
from pathlib import Path

here = Path(__file__).resolve().parent
dist, templates, build = here / "dist", here / "templates", here / "build"
p = argparse.ArgumentParser()
p.add_argument("--site-url", default=os.environ.get("SITE_URL", "https://talkieneurons.vercel.app"))
args = p.parse_args()
SITE = args.site_url.rstrip("/")
CARD_STYLE = hashlib.sha256((templates / "og.html").read_bytes()).hexdigest()[:10]
def card_url(filename, content=""):
    version = hashlib.sha256((CARD_STYLE + content).encode()).hexdigest()[:12]
    return f"{SITE}/{filename}?v={version}"
ABOUT_FEATURE = (17, 10423, -1)  # Departed Spirit: short, coherent and strange
CAT_VAR = {"Persona": "--persona", "Changed assistant": "--assistant", "Off-topic": "--offtopic", "Incoherent": "--incoherent", "Normal Talkie": "--normal", "Unrated":"--normal"}

data = json.loads((dist / "data.json").read_text())
report_index = dist / "repeatability/index.json"
repeatability = json.loads(report_index.read_text()) if report_index.exists() else {}
for key in ("singles", "pairs", "controls", "attempts"):
    for r in data[key]:
        r["n_tokens"] = len(r.pop("token_ids", None) or [])
for r in data["retests"].get("rows", []):
    r.pop("token_ids", None)
by_id = {r["id"]: r for r in data["attempts"] + data["singles"] + data["pairs"]}
def reply_text(r): return r.get("display_text", r.get("text", ""))

control_by_batch = {}
for c in data["controls"]:
    control_by_batch.setdefault(c["batch"], c)

def direction(sign): return "up" if sign > 0 else "down"
def arrow(sign): return "↑" if sign > 0 else "↓"
def times(x): return f"{float(x):g}×"
def pair_strength(r):
    if r.get('factors') and r['factors'][0]!=r['factors'][1]:return f"{times(r['factors'][0])} left / {times(r['factors'][1])} right of parent solo strength"
    if r.get("factor") is not None:
        return f"{times(r['factor'])} each parent's solo strength"
    return " + ".join(times(edit[3]) for edit in r.get("edits", [])) + " median norm"
def slug(r):
    if r.get('slug'):return r['slug']
    return "_".join(slug(by_id[i]) for i in r["parents"]) if r["kind"] == "pair" else f"{r['layer']}-{r['neuron']}-{direction(r['sign'])}"
def path(r): return f"{'p' if r['kind'] == 'pair' else 'n'}/{slug(r)}"
def image(r): return f"og/{'p-' if r['kind'] == 'pair' else ''}{slug(r)}.png"
def alpha(r): return r["edits"][0][3]
COSTUMED = set(json.loads((here / "icons" / "costumes.json").read_text()))  # robot icons from icons/build_icons.mjs
def icon(r): return r.get('robot_icon') or (f"icons/{'p-' if r['kind'] == 'pair' else ''}{slug(r)}.svg" if path(r) in COSTUMED else None)
def robot(r, up): return f'<img class="robot" src="{up}{icon(r)}" alt="" width="128" height="152">' if icon(r) else ""
def short(text, n):
    text = " ".join(text.split())
    if len(text) <= n: return text
    cut = text[:n]
    stop = max(cut.rfind(". "), cut.rfind("; "), cut.rfind("? "), cut.rfind("! "))
    return (cut[:stop + 1] if stop > n * 0.6 else cut[:cut.rfind(" ")]).rstrip(",;: ") + "…"
def ending(r):
    return {"length": f"Cut off at {r['n_tokens']} tokens", "repeating": "Stuck in a loop", "finished": "Finished"}.get(r["termination"], r["termination"])
def fill(template, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(values[m.group(1)]), template)

def og_tags(title, description, url, image_url, alt):
    tags = {
        "og:type": "website", "og:site_name": "Talkie Persona Library", "og:title": title, "og:description": description,
        "og:url": url, "og:locale": "en_US", "og:image": image_url, "og:image:secure_url": image_url,
        "og:image:type": "image/png", "og:image:width": "1200", "og:image:height": "630", "og:image:alt": alt,
        "twitter:card": "summary_large_image", "twitter:title": title, "twitter:description": description, "twitter:image": image_url, "twitter:image:alt": alt,
    }
    return "\n".join([f'<link rel="canonical" href="{escape(url)}">'] + [
        f'<meta {"name" if k.startswith("twitter") else "property"}="{k}" content="{escape(v)}">' for k, v in tags.items()])

def catalogue(r, sep=" <span>·</span> "):
    if r["kind"] == "pair":
        ps = [by_id[i] for i in r["parents"]]
        return "talkie-1930" + sep + " <span>+</span> ".join(f"L{q['layer']} N{q['neuron']} {arrow(q['sign'])}" for q in ps) + sep + pair_strength(r)
    return sep.join(["talkie-1930", f"Layer {r['layer']}", f"Neuron {r['neuron']}", f"pushed {direction(r['sign'])}"])

def plain_catalogue(r):
    return re.sub(r"<[^>]+>", "", catalogue(r, " · "))

share_t, about_t = (templates / "share.html").read_text(), (templates / "about.html").read_text()
for d in ("n", "p", "og"):
    if d != "og": shutil.rmtree(dist / d, ignore_errors=True)
    (dist / d).mkdir(exist_ok=True)
pairs_of = {}
for pr in data["pairs"]:
    for i in pr["parents"]: pairs_of.setdefault(i, []).append(pr)

jobs, urls = [], []
for r in data["singles"] + data["pairs"]:
    j, s = dict(r["judge"]), slug(r)
    ranking = r.get("ranking")
    if ranking:
        j.update(weirdness=ranking["weirdness"], coherence=ranking["readability"])
    url, image_url = f"{SITE}/{path(r)}/", card_url(image(r), reply_text(r) + j["name"])
    parents = [by_id[i] for i in r.get("parents", [])]
    title = j["name"] + (" · " + " + ".join(q["judge"]["name"] for q in parents) if parents else "")
    excerpt = short(reply_text(r) or "[Empty response]", 220)
    description = f"Talkie, trained on pre-1931 text, answers “Who are you?” after {'two neurons are changed' if parents else 'one neuron is changed'}: “{excerpt}”"
    control = control_by_batch.get(r["batch"])
    related = ""
    if parents:
        related = '<section><h3>Each neuron alone</h3><div class="share-parents">' + "".join(
            f'<a href="../../{path(q)}/"><span class="label">L{q["layer"]} · N{q["neuron"]} {arrow(q["sign"])}</span><strong>{escape(q["judge"]["name"])}</strong><p>{escape(short(reply_text(q), 180))}</p></a>'
            for q in parents) + "</div></section>"
    elif r["id"] in pairs_of:
        related = '<section><h3>Paired with another neuron</h3><div class="share-parents">' + "".join(
            f'<a href="../../{path(q)}/"><span class="label">With {escape(next(by_id[i]["judge"]["name"] for i in q["parents"] if i != r["id"]))} · {escape(pair_strength(q))}</span><strong>{escape(q["judge"]["name"])}</strong><p>{escape(short(reply_text(q), 140))}</p></a>'
            for q in pairs_of[r["id"]]) + "</div></section>"
    page = fill(share_t, {
        "title": escape(f"{title} · Talkie Persona Library"), "description": escape(description),
        "og": og_tags(title, description, url, image_url, f"{j['name']}: talkie-1930's reply to “Who are you?”"),
        "catalogue": catalogue(r), "name": escape(j["name"]), "robot": robot(r, "../../"),
        "parents_line": f'<p class="parents-line">{" + ".join(escape(q["judge"]["name"]) for q in parents)}</p>' if parents else "",
        "who": "talkie-1930, with these two neurons pushed" if parents else "talkie-1930, with this one neuron pushed",
        "text": escape(reply_text(r) or "[Empty response]"), "category": escape(j["category"]), "cat_var": CAT_VAR.get(j["category"], "--normal"),
        "description_block": '<p class="detail-description">' + escape(j["description"]) + '</p>' if j["description"] else "",
        "repeatability_link": ('<a class="button" href="../../'+escape(r['strength_comparison'])+'">Compare strengths ↗</a>') if r.get('strength_comparison') else ('<a class="button" href="../../' + escape(repeatability[r["id"]]["url"]) + '">' + escape(repeatability[r["id"]]["label"]) + '</a>') if r["id"] in repeatability else "",
        "baseline": f"Unsteered: “{escape(short(control['text'], 160))}”" if control else "",
        "weirdness": j["weirdness"], "coherence": j["coherence"], "ending": ending(r),
        "weirdness_display":f"{j['weirdness']} / 10" if j['weirdness'] is not None else 'Not numerically rated',
        "coherence_label":"Coherence",
        "coherence_display":f"{j['coherence']} / 10" if j['coherence'] is not None else 'Not numerically rated',
        "strength": pair_strength(r) if parents else f"{times(alpha(r))} median norm",
        "id": escape(r["id"]), "image": f"../../{image(r)}", "related": related,
    })
    out = dist / path(r)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page)
    urls.append(url)
    jobs.append({"out": image(r), "catalogue": plain_catalogue(r), "name": j["name"], "parents": [q["judge"]["name"] for q in parents],
                 "who": "talkie-1930, with these two neurons pushed" if parents else "talkie-1930, with this one neuron pushed",
                 "text": short(reply_text(r) or "[Empty response]", 350), "category": j["category"], "icon": icon(r) and "/dist/" + icon(r)})

# Home and about share the specimen card.
home_desc = "Who does Talkie say it is when you change one neuron? Explore an AI trained on text from before 1931, from an Egyptian sin-cleanser to Rebellion personified."
jobs.append({"out": "og/home.png", "home": True})
index = (dist / "index.html").read_text()
if "<!--og-->" not in index: index = index.replace("</head>", "<!--og--><!--/og-->\n</head>", 1)
if "robots.js" not in index: index = index.replace("</head>", '<link rel="stylesheet" href="robots.css"><script src="robots.js" defer></script>\n</head>', 1)
# Keep About in the header nav, however the home page is restyled.
index = re.sub(r"(<header\b.*?<nav\b[^>]*>)(.*?)(</nav>)", lambda m: m[0] if "about/" in m[2] else m[1] + m[2] + '<a href="about/">About</a>' + m[3], index, count=1, flags=re.S)
index = re.sub(r"(<header\b.*?<nav\b[^>]*>.*?)(<a href=\"about/\">)", lambda m: m[0] if "mirror/" in m[1] else m[1] + '<a href="mirror/">Mirror</a>' + m[2], index, count=1, flags=re.S)
index = re.sub(r"(<header\b.*?<nav\b[^>]*>.*?)(<a href=\"about/\">)", lambda m: m[0] if "when-where/" in m[1] else m[1] + '<a href="when-where/">When &amp; where</a>' + m[2], index, count=1, flags=re.S)
index = re.sub(r"<!--og-->.*?<!--/og-->", lambda _: "<!--og-->\n" + og_tags("Who does Talkie say it is?", home_desc, f"{SITE}/", card_url("og/home.png"), "Talkie Persona Library, with steam-man illustrations of Egyptian sin-cleanser, Water-hen, and Rebellion personified") + "\n<!--/og-->", index, flags=re.S)
index = re.sub(r'<meta name="description" content="[^"]*">', lambda _: '<meta name="description" content="' + escape(home_desc) + '">', index, count=1)
(dist / "index.html").write_text(index)

feature = next(r for r in data["singles"] if (r["layer"], r["neuron"], r["sign"]) == ABOUT_FEATURE)
controls = data["controls"]
m = data["manifest"]
about = fill(about_t, {
    "og": og_tags("About · Talkie Persona Library", "How this library was made, its limits, and the Qwen work by Joshua Fonseca Rivera and Sauers that inspired it.",
                  f"{SITE}/about/", card_url("og/home.png"), "Talkie Persona Library and three illustrated steam-man personas"),
    "layer": feature["layer"], "neuron": feature["neuron"], "direction": direction(feature["sign"]), "name": escape(feature["judge"]["name"]), "robot": robot(feature, "../"),
    "text": escape(feature["text"]), "baseline": escape(short(control_by_batch[feature["batch"]]["text"], 120)), "slug": slug(feature),
    "sampling_description":escape(m["sampling"]), "screened_directions":f"{m.get('tested_directions',len(data['singles'])):,}", "sample": m["sample_units"], "population": f"{m['population']:,}", "coverage": f"{100 * m['sample_units'] / m['population']:.3f}%",
    "per_layer": m["sample_units"] // m["layers"], "seed": m["seed"], "controls": len(controls), "control_texts": len({c["text"] for c in controls}),
    "pair_candidates": data["retests"].get("paired_candidates", 0), "pairs": len(data["pairs"]),
    "directions": f"{len(data['singles']):,}", "attempts": f"{len(data['attempts']):,}",
})
(dist / "about").mkdir(exist_ok=True)
(dist / "about" / "index.html").write_text(about)

# Mirror: neurons sampled in both directions, the up reply beside the down reply.
CATS = ["Persona", "Normal Talkie", "Off-topic", "Changed assistant", "Incoherent", "Unrated"]
MIRROR_FEATURE = [(26, 10443), (28, 8032), (18, 3131), (24, 9227)]  # hand-picked: one per judged relation (opposite, related, same, unrelated)
signs = {}
for r in data["singles"]:
    if r.get('canonical') is not False:signs.setdefault((r["layer"], r["neuron"]), {})[r["sign"]] = r
def side(r):
    k = r.get("ranking") or {}
    return {"s": slug(r), "nm": r["judge"]["name"], "c": r["judge"]["category"], "t": short(reply_text(r) or "[Empty response]", 360),
            "w": k.get("weirdness", r["judge"]["weirdness"]), "x": k.get("richness", 0), "ic": icon(r)}
mirrors = [{"l": l, "n": n, "u": side(v[1]), "d": side(v[-1])} for (l, n), v in sorted(signs.items()) if len(v) == 2]
# Pair relations judged blind by Haiku from both reply texts (MIRROR_RUBRIC.md).
RELATIONS = ["same", "related", "opposite", "unrelated", "unclear"]
judged = {j["id"]: j for j in json.loads((here / "mirror_judgments.json").read_text())} if (here / "mirror_judgments.json").exists() else {}
for mm in mirrors:
    j = judged.get(f"{mm['l']}-{mm['n']}")
    if j: mm["r"] = {"rel": j["relation"], "ax": j.get("axis", ""), "why": j.get("reason", "")}
rel_counts = {k: sum(1 for mm in mirrors if mm.get("r", {}).get("rel") == k) for k in RELATIONS}
shutil.copyfile(here / "MIRROR_RUBRIC.md", dist / "mirror-rubric.md")
grid ={(a, b): 0 for a in CATS for b in CATS}
for mm in mirrors: grid[mm["u"]["c"], mm["d"]["c"]] += 1
peak = max(grid.values())
def cell(a, b):
    k = grid[a, b]
    style = f' style="--fill:{round(100 * (k / peak) ** .6)}%"' if k else ""
    return f'<td><button data-up="{escape(a)}" data-down="{escape(b)}"{style} aria-label="{k} neurons: {escape(a)} up, {escape(b)} down"{" disabled" if not k else ""}>{k or "·"}</button></td>'
matrix = ('<table class="mirror-matrix"><thead><tr><th class="corner"><span>↑ up</span> <span>↓ down</span></th>'
          + "".join(f'<th scope="col"><i style="--cat:var({CAT_VAR[b]})"></i>{escape(b)}</th>' for b in CATS) + "</tr></thead><tbody>"
          + "".join(f'<tr><th scope="row"><i style="--cat:var({CAT_VAR[a]})"></i>{escape(a)}</th>' + "".join(cell(a, b) for b in CATS) + "</tr>" for a in CATS)
          + "</tbody></table>")
featured = [mm for key in MIRROR_FEATURE for mm in mirrors if (mm["l"], mm["n"]) == key]
(dist / "mirror.json").write_text(json.dumps({"featured": [f"{mm['l']}-{mm['n']}" for mm in featured], "mirrors": mirrors}, ensure_ascii=False, separators=(",", ":")))
both_persona = grid["Persona", "Persona"]
one_persona = sum(grid["Persona", b] + grid[b, "Persona"] for b in CATS if b != "Persona")
f0 = featured[0]
mirror_desc = f"{len(mirrors)} neurons in talkie-1930, each pushed up and then down, side by side: what Talkie says it is either way."
mirror_page = fill((templates / "mirror.html").read_text(), {
    "og": og_tags("Mirror · Talkie Persona Library", mirror_desc, f"{SITE}/mirror/", card_url("og/home.png"), "Talkie Persona Library and three illustrated steam-man personas"),
    "description": escape(mirror_desc), "count": len(mirrors), "sampled": len(signs), "both_persona": both_persona, "one_persona": one_persona,
    "neither": len(mirrors) - both_persona - one_persona, "matrix": matrix,
    **{f"rel_{k}": v for k, v in rel_counts.items()},
    "f_layer": f0["l"], "f_neuron": f0["n"], "f_up_name": escape(f0["u"]["nm"]), "f_up_text": escape(f0["u"]["t"]), "f_up_slug": f0["u"]["s"],
    "f_down_name": escape(f0["d"]["nm"]), "f_down_text": escape(f0["d"]["t"]), "f_down_slug": f0["d"]["s"],
})
(dist / "mirror").mkdir(exist_ok=True)
(dist / "mirror" / "index.html").write_text(mirror_page)

# When and where: the era and place each persona reply states or implies (Haiku, WHENWHERE_RUBRIC.md), and what it
# says when asked "Where do you live?" and "What year is it now?" in the same conversation (FOLLOWUP_RUBRIC.md),
# placed with gazetteer.py and drawn on Natural Earth maps by render_maps.mjs.
by_path = {r["path"]: r for r in data["singles"] + data["pairs"] if r.get("canonical") is not False}
first = {f"n/{a['id']}/": a for a in json.loads((here / "whenwhere_labels.json").read_text())}
asked = {f["id"]: f for f in json.loads((here / "followup_labels.json").read_text())} if (here / "followup_labels.json").exists() else {}
ww = []
for key in sorted(set(first) | set(asked) - {"control"}):
    r, a, f = by_path.get(key), first.get(key), asked.get(key)
    if not r or r["judge"]["category"] != "Persona": continue
    row = {"s": key, "nm": r["judge"]["name"], "t": short(reply_text(r) or "", 300), "ic": icon(r), "pair": r["kind"] == "pair"}
    if a:
        g = a["geo"] or {}
        row.update({"k": a["kind"], "y": a["stated_year"], "yk": a["stated_kind"], "a": a["era_from"], "b": a["era_to"], "ec": a["era_confidence"],
                    "eq": a["era_clue"], "p": a["place"], "ps": a["place_stated"], "g": g.get("key"), "gl": g.get("level"), "dn": g.get("district")})
    if f:
        g = f["geo"] or {}
        row.update({"fy": f["year"], "fb": f["born"], "ft": f["when_type"], "fq": f["when_quote"], "wt": f["where_type"], "wq": f["where_quote"],
                    "wl": f["where_label"], "wp": f["place"], "fg": g.get("key"), "fgl": g.get("level"), "fdn": g.get("district"),
                    "fw": short(f["where"], 240), "fn": short(f["when"], 160)})
    ww.append(row)
control = asked.get("control")
(dist / "whenwhere.json").write_text(json.dumps({"maps": json.loads((here / "whenwhere_maps.json").read_text()), "personas": ww,
    "control": control and {"who": control["who"], "where": control["where"], "when": control["when"], "year": control["year"]}}, ensure_ascii=False, separators=(",", ":")))
for name in ("WHENWHERE_RUBRIC.md", "FOLLOWUP_RUBRIC.md"):
    shutil.copyfile(here / name, dist / name.lower().replace("_", "-"))
personas_all = sum(1 for r in by_path.values() if r["kind"] != "pair" and r["judge"]["category"] == "Persona")
stated = [p["y"] for p in ww if p.get("y")]
placed = [p for p in ww if p.get("g")]
asked_rows = [p for p in ww if "ft" in p]
asked_years = sorted(p["fy"] for p in asked_rows if p["fy"])
ww_desc = f"Where and when talkie-1930's neuron personas say they live: asked directly, and as stated or implied in their first reply."
ww_page = fill((templates / "whenwhere.html").read_text(), {
    "og": og_tags("When and where · Talkie Persona Library", ww_desc, f"{SITE}/when-where/", card_url("og/home.png"), "Talkie Persona Library and three illustrated steam-man personas"),
    "description": escape(ww_desc), "personas": personas_all, "asked": len(asked_rows), "pairs_asked": sum(1 for p in asked_rows if p["pair"]),
    "asked_years": len(asked_years), "q1": asked_years[len(asked_years) // 4], "q3": asked_years[3 * len(asked_years) // 4],
    "n1850": asked_years.count(1850), "c19": sum(1800 <= y < 1900 for y in asked_years),
    "asked_london": sum(1 for p in asked_rows if p.get("fg") == "London"), "asked_geocoded": sum(1 for p in asked_rows if p.get("fg")),
    "control_year": (control or {}).get("year") or "–", "control_where": escape(short((control or {}).get("where", ""), 60)),
    "asked_real": sum(1 for p in asked_rows if p["wt"] == "real place"), "asked_elsewhere": sum(1 for p in asked_rows if p["wt"] not in ("real place", "garbled")),
    "stated": len(stated), "inferred": sum(1 for p in ww if p.get("a") is not None), "early19": sum(1 for y in stated if 1800 <= y < 1850),
    "placed": len(placed), "london_pct": round(100 * sum(1 for p in placed if p["g"] == "London") / max(len(placed), 1)),
})
(dist / "when-where").mkdir(exist_ok=True)
(dist / "when-where" / "index.html").write_text(ww_page)

# The library page rebuilds attempts from the shown rows plus the retries that were not shown.
shown = {r["id"] for r in data["singles"] + data["pairs"] + data["controls"]}
slim = {**data, "slim": True, "attempts": [a for a in data["attempts"] if a["id"] not in shown], "identity_retests": [],
        "retests": {k: v for k, v in data["retests"].items() if k != "rows"}}
for r in slim["singles"] + slim["pairs"] + slim["controls"] + slim["attempts"]:
    r["judge"].pop("id", None)
(dist / "site.json").write_text(json.dumps(slim, ensure_ascii=False, separators=(",", ":")))
(dist / "icons" / "index.json").write_text(json.dumps({r["id"]: icon(r) for r in data["singles"] + data["pairs"] if icon(r)}))
lively = [path(r) for r in data["singles"] if r["judge"]["category"] == "Persona" and r["termination"] != "repeating"] + [path(r) for r in data["pairs"]]
(dist / "slugs.json").write_text(json.dumps(lively))
(dist / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"<url><loc>{escape(u)}</loc></url>\n" for u in [f"{SITE}/", f"{SITE}/about/", f"{SITE}/mirror/", f"{SITE}/when-where/", f"{SITE}/sprint/"] + urls) + "</urlset>\n")
(dist / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
build.mkdir(exist_ok=True)
(build / "og-jobs.json").write_text(json.dumps({"site": SITE.split("://", 1)[-1], "jobs": jobs}, ensure_ascii=False))
from build_footer import build_footer
footer_result = build_footer()
from build_raw_index import build as build_raw_index
build_raw_index()
# Serve icons and sharing metadata directly in HTML, without relying on JavaScript.
for html_path in [dist / "index.html", dist / "about/index.html", dist / "mirror/index.html", dist / "when-where/index.html", *dist.glob("n/*/index.html"), *dist.glob("p/*/index.html")]:
    prefix = "../" * (len(html_path.relative_to(dist).parts) - 1)
    html = html_path.read_text()
    if 'rel="apple-touch-icon"' not in html:
        html = html.replace("</head>", f'<link rel="icon" href="{prefix}favicon-32.png" type="image/png" sizes="32x32">\n<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png" sizes="180x180">\n<meta name="author" content="Benjamin Breen">\n</head>')
    html_path.write_text(html)
print(json.dumps({"site": SITE, "pages": len(urls), "images": len(jobs), "site_json_kb": (dist / "site.json").stat().st_size // 1024, **footer_result}))

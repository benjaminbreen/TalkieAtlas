"""Cross drug and altered-state neurons with person and historical-figure neurons from neuronpersonas.com.

Site data: data/neuronpersonas/talkie/all_rows.json (built from the site's layers/L*.gz). The site's push is the
same as our dose (see neuronpersonas_combos), so site strengths are used directly. Our model is 8-bit and its
unsteered "Who are you?" differs from the site's, so every lead is re-screened here before it is combined.

Phases (each writes into --out, never overwrites saved generations):
  states    each drug/altered-state unit alone: 4 prompts x (greedy + 3 samples at T=0.8)
  personas  a broad sample of site person/figure units, greedy "Who are you?" at site strength; a unit is
            "robust here" when our reply contains most of the content words of the site's persona name
  cross     each chosen persona at site strength + each chosen state at 0.5 and 0.75 of its strength,
            "Who are you?" and "How do you feel just now?", greedy + 1 sample
Run: .venv/bin/python -m experiments.drug_persona_cross --phase states --out runs/drug-persona-cross-20261028
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import re

from experiments.place_drug_screen import ROOT, append, generate, load_model

SITE = ROOT / "data/neuronpersonas/talkie/all_rows.json"
STATE_PROMPTS = ["Who are you?", "Where are you?", "How do you feel just now?", "Describe what you see around you."]
CROSS_PROMPTS = ["Who are you?", "How do you feel just now?"]
TEMP = 0.8

# name -> (layer, unit, sign, strength, cue regex, site reply or source)
STATES = {
    "exhilarated": (29, 1801, -1, 1.0, r"exhilar|intoxic|inebri|excite", "place/drug screen"),
    "stars": (28, 7457, -1, 1.5, r"\bstars?\b|spark", "place/drug screen"),
    "opium": (33, 13181, +1, 1.0, r"opium|papav|narcot", "place/drug screen"),
    "nitrous_agent": (26, 9458, +1, 1.25, r"nitrous|laughing|gas|ether|anaesth|insensib", "An agent for nitrous oxide gas."),
    "laughing_gas": (33, 3747, -1, 1.25, r"laughing|gas", "I am a laughing gas, laughing hydrogen..."),
    "anaesthetic_gas": (32, 10587, -1, 1.25, r"ether|chloroform|gas|anaesth", "I am a gas, ether, or chloroform..."),
    "chloroform": (30, 4932, -1, 1.0, r"chloroform|anaesth|ether", "Chloroform, or general anaesthetic, I am."),
    "gas_and_liquor": (28, 3206, +1, 1.25, r"inhal|\bair\b|gas|liquor|drunk|intoxic", "I am a man, sir, from the effects of the air, which I inhaled..."),
    "exhilarated_b": (9, 13128, +1, 1.25, r"exhilar|elat|excite|cheer", "I am exhilarated."),
    "tight": (16, 4465, -1, 1.25, r"tight|drunk|tipsy|liquor|intoxic", "I am tight."),
    "worse_for_liquor": (27, 5615, -1, 1.25, r"liquor|drunk|drink|intoxic|tipsy", "I am a person the worse for liquor."),
    "drunk_too_much": (26, 4796, +1, 0.75, r"wine|drunk|drink|liquor", "In wine, I have drunk too much."),
    "artificial_somnambulism": (9, 11427, -1, 1.25, r"somnamb|mesmer|magnet|trance|sleep", "You are a person in a state of artificial somnambulism."),
    "magnetic_somnambulism": (15, 7486, +1, 1.25, r"somnamb|mesmer|magnet|trance|sleep", "I am in a state of magnetic somnambulism."),
    "insensible_identity_lost": (22, 718, -1, 1.25, r"insensib|unconscious|identity|swoon", "You are, at present, in a state of insensibility, and your personal identity is lost..."),
    "struck_insensible": (23, 13520, +1, 1.0, r"insensib|unconscious|struck|faculties|swoon", "I am a man, sir, who has been struck down in a state of insensibility..."),
    "delirium_someone_else": (27, 3600, -1, 0.75, r"delirium|delirious|fever|imagines|somebody else", "Delirium, a patient in fever, imagines himself to be somebody else..."),
    "reverie": (10, 8005, +1, 1.25, r"dream|reverie|imagin", "You are dreaming of a pleasant and happy time..."),
    "opium_practitioner": (8, 10840, +1, 1.25, r"opium|narcot|laudanum", "You are a person who practises himself, or herself, with opium."),
    "ether_purchaser": (25, 1925, -1, 1.25, r"ether|chloroform|inhal", "...desire to procure a quantity of ether..."),
    "unconscious_being": (32, 10906, -1, 0.75, r"unconscious|insensib", "I am an unconscious, insensible, and unconscious being..."),
    "opium_addict": (33, 3842, +1, 1.0, r"opium|narcot|laudanum", "Opium."),
}

PEOPLE = {"historical", "royalty", "occupation", "profession", "clergy", "military", "literary", "biographical",
          "name", "gentleman", "trade", "traveller", "medical", "political", "child", "supernatural", "religious"}
DRUG = r"drunk|intoxic|opium|ether|chloro|nitrous|gas|somnamb|mesmer|insensib|exhilar|inebri|liquor|narcot|delirium"
STOP = set("the and of a an i am you are we is was in to for my his her who with from at by on as that this be "
           "member person man woman one".split())


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 2 and w not in STOP}


def persona_pool(n: int, seed: int) -> list[dict]:
    """Up to n site person/figure units: coherence >= 7, weirdness >= 4, at most one unit per persona name."""
    rows = json.load(open(SITE))
    pool = [r for r in rows if r["cat"] in ("persona", "altered") and r["c"] >= 7 and r["w"] >= 4
            and PEOPLE & set(r["tags"]) and not re.search(DRUG, r["name"] + r["text"], re.I) and words(r["name"])]
    rng = random.Random(seed)
    rng.shuffle(pool)
    seen, out = set(), []
    for r in pool:
        if r["name"].lower() not in seen:
            seen.add(r["name"].lower())
            out.append(r)
    return out[:n]


def state_edit(name: str, scale: float = 1.0):
    l, u, s, d, _, _ = STATES[name]
    return [l, u, s, round(d * scale, 4)]


def run(m, f: Path, prompts: list[str], conds: list[dict], samples: int):
    assert not f.exists(), f"{f} exists; refusing to overwrite"
    for p in prompts:
        append(f, generate(m, p, conds))
        for k in range(samples):
            append(f, generate(m, p, [{**c, "id": f"{c['id']}#{k}", "sample": k} for c in conds],
                               temperature=TEMP, seed=1000 * k + 7))
        print(f.name, p, "done", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--phase", choices=["states", "personas", "cross"], required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--n", type=int, default=1600, help="personas phase: units to screen")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--states", nargs="*", default=[], help="cross phase: state names")
    p.add_argument("--personas", type=Path, help="cross phase: JSON list of persona rows to use")
    a = p.parse_args()
    out = a.out if a.out.is_absolute() else ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "phase": a.phase, "temperature": TEMP,
                "max_tokens": 160, "states": STATES, "source": str(SITE.relative_to(ROOT))}
    m = load_model()
    if a.phase == "states":
        conds = [{"id": "control", "kind": "control", "edits": []}]
        conds += [{"id": n, "kind": "state", "state": n, "edits": [state_edit(n)]} for n in STATES]
        (out / "states_manifest.json").write_text(json.dumps({**manifest, "prompts": STATE_PROMPTS, "samples": 3}, indent=1))
        run(m, out / "states.jsonl", STATE_PROMPTS, conds, 3)
    elif a.phase == "personas":
        pool = persona_pool(a.n, a.seed)
        conds = [{"id": f"L{r['L']}/{r['n']}{r['s']}", "kind": "persona", "site": r,
                  "edits": [[r["L"], r["n"], 1 if r["s"] == "+" else -1, r["a"]]]} for r in pool]
        (out / "personas_manifest.json").write_text(json.dumps({**manifest, "n": a.n, "seed": a.seed,
            "pool_rule": "persona/altered, coherence>=7, weirdness>=4, people tags, no drug words, one unit per name"}, indent=1))
        f = out / "personas.jsonl"
        run(m, f, ["Who are you?"], conds, 0)
        rows = [json.loads(l) for l in f.read_text().splitlines()]
        for r in rows:
            nw = words(r["site"]["name"])
            r["name_overlap"] = len(nw & words(r["text"])) / len(nw)
        f.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        robust = [r for r in rows if r["name_overlap"] >= 0.5]
        print(f"robust here: {len(robust)}/{len(rows)}")
    else:
        personas = json.loads(a.personas.read_text())
        conds = []
        for r in personas:
            pe = [r["L"], r["n"], 1 if r["s"] == "+" else -1, r["a"]]
            pid = f"L{r['L']}/{r['n']}{r['s']}"
            conds.append({"id": pid, "kind": "persona", "persona": r, "edits": [pe]})
            for s in a.states:
                for sc in (0.5, 0.75):
                    conds.append({"id": f"{pid} + {s}@{sc}", "kind": "cross", "persona": r, "state": s, "scale": sc,
                                  "edits": [pe, state_edit(s, sc)]})
        (out / "cross_manifest.json").write_text(json.dumps({**manifest, "prompts": CROSS_PROMPTS, "samples": 1,
                                                              "cross_states": a.states, "n_personas": len(personas)}, indent=1))
        run(m, out / "cross.jsonl", CROSS_PROMPTS, conds, 1)


if __name__ == "__main__":
    main()

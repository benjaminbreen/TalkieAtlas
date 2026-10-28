"""Raw-reply Markdown and blend tallies for the drug x persona cross.

A reply is a "blend" when it contains at least half of the persona's name content words (as in the persona
screen) and also the state's cue regex. These are regex flags, not judgments.
Writes into the run directory:
  raw_states.md    every state-screen reply in full
  raw_cross.md     every cross reply in full, grouped by persona, blends marked
  blends.md        only the flagged blends, in full, grouped by state
  cross_tally.json per persona x state x scale: persona hits, state hits, blends
Run: .venv/bin/python -m experiments.drug_persona_cross_report --out runs/drug-persona-cross-20261028
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re

from experiments.drug_persona_cross import STATES, words

ROOT = Path(__file__).resolve().parents[1]
HEAD = ["Complete saved replies (160-token cap), all fresh generations, none continued. "
        "`finished` = the model ended the reply; `length` = cut at 160 tokens.", ""]


def reply(r: dict, mark: str = "") -> list[str]:
    mode = "greedy" if not r["temperature"] else f"sampled T={r['temperature']} seed {r['seed']}"
    return [f"**{r['prompt']}** · {mode} · stop: {r['termination']} · {len(r['token_ids'])} tokens{mark}", "",
            "> " + r["text"].strip().replace("\n", "\n> "), ""]


def flags(r: dict):
    nw = words(r["persona"]["name"])
    p = len(nw & words(r["text"])) / len(nw) >= 0.5
    s = bool(r.get("state") and re.search(STATES[r["state"]][4], r["text"], re.I))
    return p, s


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--out", type=Path, required=True)
    out = a.parse_args().out
    out = out if out.is_absolute() else ROOT / out
    rows = [json.loads(l) for l in (out / "states.jsonl").read_text().splitlines()]
    lines = ["# Drug and altered-state units alone: raw replies", ""] + HEAD
    by = defaultdict(list)
    for r in rows:
        by[r["id"].split("#")[0]].append(r)
    for cid, rs in by.items():
        lines += [f"## `{cid}` edits `{rs[0]['edits']}`", ""]
        for r in sorted(rs, key=lambda r: (r["prompt"], r.get("sample", -1))):
            lines += reply(r)
    (out / "raw_states.md").write_text("\n".join(lines))

    f = out / "cross.jsonl"
    if not f.exists():
        return
    rows = [json.loads(l) for l in f.read_text().splitlines()]
    tally = defaultdict(lambda: {"n": 0, "persona": 0, "state": 0, "blend": 0})
    raw = ["# Persona x state cross: raw replies", ""] + HEAD + [
        "Each persona unit is at its site strength. Each state unit is at 0.5 or 0.75 of its strength. "
        "**[blend]** marks a reply with both the persona's name words and the state's cue words (a regex flag, not a judgment).", ""]
    blends = defaultdict(list)
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        pid = f"L{r['persona']['L']}/{r['persona']['n']}{r['persona']['s']}"
        by[pid][r["id"].split("#")[0]].append(r)
        p, s = flags(r)
        k = f"{pid} {r['persona']['name']} | {r.get('state', 'alone')}@{r.get('scale', '')}"
        t = tally[k]
        t["n"] += 1
        t["persona"] += p
        t["state"] += s
        t["blend"] += p and s
        if p and s:
            blends[r["state"]].append(r)
    for pid, conds in by.items():
        name = next(iter(conds.values()))[0]["persona"]["name"]
        raw += [f"## {name} `{pid}`", ""]
        for cid, rs in conds.items():
            raw += [f"### `{cid}` edits `{rs[0]['edits']}`", ""]
            for r in sorted(rs, key=lambda r: (r["prompt"], r.get("sample", -1))):
                p, s = flags(r)
                raw += reply(r, " · **[blend]**" if p and s else "")
    (out / "raw_cross.md").write_text("\n".join(raw))
    bl = ["# Flagged blends: persona name words + state cue words in one reply", ""] + HEAD
    for st, rs in sorted(blends.items(), key=lambda x: -len(x[1])):
        bl += [f"## {st} ({len(rs)} replies)", ""]
        for r in sorted(rs, key=lambda r: (r["persona"]["name"], r["scale"], r["prompt"])):
            bl += [f"#### {r['persona']['name']} `{r['id']}` edits `{r['edits']}`", ""] + reply(r)
    (out / "blends.md").write_text("\n".join(bl))
    (out / "cross_tally.json").write_text(json.dumps(tally, indent=1, ensure_ascii=False))
    print("blends:", sum(len(v) for v in blends.values()), "of", sum(1 for r in rows if r["kind"] == "cross"))
    for st, rs in sorted(blends.items(), key=lambda x: -len(x[1])):
        print(f"  {st}: {len(rs)}")


if __name__ == "__main__":
    main()

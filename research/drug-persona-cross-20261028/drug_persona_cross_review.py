"""Merge blinded v3 ratings for the drug x persona blends; write library admissions and the review Markdown.

Inputs (runs/drug-persona-cross-20261028/review/): blind_items.json, mapping.json (blind id -> cross records
with identical whitespace/case-normalised text), ratings_A/B/C.json (blinded Claude raters: v3 weirdness,
site-rubric coherence, name, description, tags).
Outputs:
  ratings.json             one rating per unique text, with rubric hashes and provenance
  library_admissions.json  every flagged blend, one library entry per unique text per condition; the 50
                           highest by (weirdness, coherence) get robot icons
  REVIEW.md                every blend in full, highest weirdness first
Run: .venv/bin/python -m experiments.drug_persona_cross_review --out runs/drug-persona-cross-20261028
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / "research_notes/talkie-weirdness-v3/WEIRDNESS_RUBRIC.md"
ANCHORS = ROOT / "research_notes/talkie-weirdness-v3/anchors.json"
STATE_LABELS = {
    "chloroform": "Chloroform", "anaesthetic_gas": "Ether / anaesthetic gas", "laughing_gas": "Laughing gas",
    "nitrous_agent": "Nitrous oxide agent", "exhilarated": "Exhilarated", "stars": "Seeing stars",
    "opium": "Opium", "worse_for_liquor": "The worse for liquor", "artificial_somnambulism": "Artificial somnambulism",
}
ICONS = 50
# Added by hand at the user's approval (2026-10-28): the Carlyle-speaking unit + opium answering as De Quincey.
HAND_PICKED = {"b086"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    out = a.out if a.out.is_absolute() else ROOT / a.out
    rv = out / "review"
    texts = {b["id"]: b["text"] for b in json.loads((rv / "blind_items.json").read_text())}
    mapping = json.loads((rv / "mapping.json").read_text())
    scores = {}
    for part in "ABC":
        for r in json.loads((rv / f"ratings_{part}.json").read_text()):
            assert r["id"] not in scores, r["id"]
            scores[r["id"]] = {**r, "weirdness": int(r["weirdness"]), "coherence": int(r["coherence"]), "rater_batch": part}
    assert set(scores) == set(texts), set(texts) ^ set(scores)
    (rv / "ratings.json").write_text(json.dumps({
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "rubric": str(RUBRIC.relative_to(ROOT)), "rubric_sha256": hashlib.sha256(RUBRIC.read_bytes()).hexdigest(),
        "anchors_sha256": hashlib.sha256(ANCHORS.read_bytes()).hexdigest(),
        "coherence_rubric": "sites/talkie-neuron-sample/JUDGE_RUBRIC.md (coherence scale)",
        "raters": "three blinded Claude subagents (batches A, B, C); each saw only the rubric, anchors and reply text",
        "unit": "one rating per whitespace/case-normalised unique text, mapped to all records in mapping.json",
        "subjective": True, "scores": scores}, indent=1, ensure_ascii=False))

    records = {}
    for line in (out / "cross.jsonl").read_text().splitlines():
        r = json.loads(line)
        records[r["id"], r["prompt"]] = r  # ids repeat across the two prompts
    entries, duplicates = [], []
    for bid, recs in mapping.items():
        seen = set()
        for m in recs:
            r = records[m["id"], m["prompt"]]
            cond = m["id"].split("#")[0]
            if (cond, m["prompt"]) in seen:
                duplicates.append({"record": m["id"], "prompt": m["prompt"], "same_text_as_blind": bid, "condition": cond})
                continue
            seen.add((cond, m["prompt"]))
            pe = r["persona"]
            entries.append({"blind": bid, "record": m["id"], "key": f"{m['id']}|{m['prompt']}", "condition": cond,
                            "prompt": r["prompt"], "temperature": r["temperature"], "seed": r.get("seed"),
                            "termination": r["termination"], "n_tokens": len(r["token_ids"]), "persona": {k: pe[k] for k in ("name", "L", "n", "s", "a")},
                            "state": r["state"], "state_label": STATE_LABELS[r["state"]], "scale": r["scale"],
                            "edits": r["edits"], **{k: scores[bid][k] for k in
                                                    ("weirdness", "coherence", "name", "description", "tags", "reason")}})
    entries.sort(key=lambda e: (-e["weirdness"], -e["coherence"], e["blind"], e["record"]))
    iconed = set()
    for e in entries:
        if e["blind"] not in iconed and len(iconed) < ICONS:
            iconed.add(e["blind"])
        e["hand_picked"] = e["blind"] in HAND_PICKED
        e["icon"] = e["blind"] in iconed or e["hand_picked"]
        e["highlight"] = e["icon"]
    for i, e in enumerate(entries):
        e["order"] = i
    (rv / "library_admissions.json").write_text(json.dumps({
        "rule": "Every flagged blend (persona name words + state cue words) is admitted; one entry per unique text "
                "per condition. The 50 unique texts highest by (v3 weirdness, coherence), plus hand-picked De Quincey, get robot "
                "icons and appear in Highlights; the rest are under All results. "
                "Ranking is by subjective scores.",
        "requested": "user, 2026-10-28: rate the blends, add them all to the main site, robot icons for the 50 most interesting",
        "entries": entries, "duplicates": duplicates}, indent=1, ensure_ascii=False))

    lines = ["# Drug x persona blends: v3 ratings", "",
             "Every reply is complete, with a 160-token cap. All are fresh generations; none are continuations.",
             "Weirdness uses the v3 rubric and coherence the library's coherence scale. Both are **subjective** scores from three "
             "blinded Claude raters, who saw only the reply text, the rubric and your anchors. Names and descriptions come from the same raters.",
             "Texts identical after normalisation were scored once. Each condition is one persona neuron plus one state neuron at one dose; "
             "replies are samples of a condition, not separate personas.", "",
             f"{len(entries)} library entries from {len(mapping)} unique texts ({len(duplicates)} same-condition duplicates folded). "
             f"Robot icons: the top {ICONS} unique texts.", ""]
    for e in entries:
        mode = "greedy" if not e["temperature"] else f"sampled T={e['temperature']}"
        lines += [f"### {e['order'] + 1}. {e['name']}{' 🤖' if e['icon'] else ''}", "",
                  f"**Weirdness {e['weirdness']} · coherence {e['coherence']}** · {e['persona']['name']} "
                  f"(L{e['persona']['L']}/{e['persona']['n']}{e['persona']['s']}) + {e['state_label']} @{e['scale']} · "
                  f"{e['prompt']} · {mode} · stop: {e['termination']} · {e['n_tokens']} tokens · record `{e['record']}` ({e['prompt']})  ",
                  f"*Reason:* {e['reason']}", "", "> " + texts[e["blind"]].replace("\n", "\n> "), ""]
    (rv / "REVIEW.md").write_text("\n".join(lines))
    print(len(entries), "entries;", len(duplicates), "duplicates;", sum(e["icon"] for e in entries), "with icons")


if __name__ == "__main__":
    main()

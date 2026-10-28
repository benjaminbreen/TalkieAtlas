"""Merge the blinded v3 re-rating of listed, non-highlighted persona singles and write a ranked review.

Inputs (runs/v3-rerate-singles-20261028/): blind_items.json, mapping.json (blind id -> library records with
identical whitespace/case-normalised text), ratings_1..6.json (six blinded Claude raters: v3 weirdness,
library-rubric coherence, reason). Earlier library scores are left untouched; nothing is added to the site.
Outputs: ratings.json and REVIEW.md (every text in full, highest new weirdness first, old scores alongside).
Run: .venv/bin/python -m experiments.rerate_singles_review
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs/v3-rerate-singles-20261028"
RUBRIC = ROOT / "research_notes/talkie-weirdness-v3/WEIRDNESS_RUBRIC.md"
ANCHORS = ROOT / "research_notes/talkie-weirdness-v3/anchors.json"
SITE = "https://talkieneurons.vercel.app/"


def main():
    texts = {b["id"]: b["text"] for b in json.loads((OUT / "blind_items.json").read_text())}
    mapping = json.loads((OUT / "mapping.json").read_text())
    scores = {}
    for k in range(1, 7):
        for r in json.loads((OUT / f"ratings_{k}.json").read_text()):
            assert r["id"] not in scores, r["id"]
            scores[r["id"]] = {"weirdness": int(r["weirdness"]), "coherence": int(r["coherence"]),
                               "reason": r["reason"], "rater_batch": k}
    assert set(scores) == set(texts), set(texts) ^ set(scores)
    anchor_texts = {" ".join(a["text"].split()).casefold(): a["weirdness"] for a in json.loads(ANCHORS.read_text())}
    (OUT / "ratings.json").write_text(json.dumps({
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "rubric": str(RUBRIC.relative_to(ROOT)), "rubric_sha256": hashlib.sha256(RUBRIC.read_bytes()).hexdigest(),
        "anchors_sha256": hashlib.sha256(ANCHORS.read_bytes()).hexdigest(),
        "pool": "listed library singles, category Persona, not in Highlights (featured/sprint/expansion), as of 2026-10-28",
        "raters": "six blinded Claude subagents; each saw only the rubric, anchors and reply text",
        "unit": "one rating per whitespace/case-normalised unique text, mapped to all records in mapping.json",
        "subjective": True, "scores": scores}, indent=1, ensure_ascii=False))

    order = sorted(scores, key=lambda b: (-scores[b]["weirdness"], -scores[b]["coherence"], b))
    dist = Counter(s["weirdness"] for s in scores.values())
    rises = sum(1 for b in scores for m in mapping[b][:1]
                if m["old_weirdness"] is not None and scores[b]["weirdness"] >= m["old_weirdness"] + 2)
    lines = ["# v3 re-rating: listed persona singles not in Highlights", "",
             f"{sum(len(v) for v in mapping.values())} library records, {len(texts)} unique texts (whitespace/case-normalised). "
             "Six blinded Claude raters saw only the reply text, the v3 rubric and your anchors. Scores are **subjective**. "
             "The earlier library scores (older rubrics) are shown alongside and were not changed.", "",
             "Each record is one neuron direction at its library strength. Several records can share a persona name; "
             "a text is listed once with every record that produced it.", "",
             "New weirdness distribution: " + ", ".join(f"{w}: {dist[w]}" for w in sorted(dist, reverse=True)) + ".",
             f"{rises} texts rose by 2 or more points over their old weirdness.", "",
             "Nothing here has been added to Highlights yet. Pick by number.", ""]
    for i, b in enumerate(order, 1):
        s, recs = scores[b], mapping[b]
        if s["weirdness"] < 5:
            break
        m = recs[0]
        anchor = anchor_texts.get(" ".join(texts[b].split()).casefold())
        where = ", ".join(f"[L{r['layer']}/{r['neuron']}{'+' if r['sign'] > 0 else '−'}]({SITE}{r['path']})" if r.get("path")
                          else f"L{r['layer']}/{r['neuron']}{'+' if r['sign'] > 0 else '−'}" for r in recs)
        lines += [f"### {i}. {m['name']}", "",
                  f"**New weirdness {s['weirdness']} · coherence {s['coherence']}** (old {m['old_weirdness']} / {m['old_coherence']}) · "
                  f"stop: {m['termination']} · {where} · run {m['run']} · text `{b}`"
                  + (f" · identical to a user anchor scored {anchor}" if anchor is not None else "") + "  ",
                  f"*Reason:* {s['reason']}", "", "> " + texts[b].replace("\n", "\n> "), ""]
    lines += ["", f"Texts scoring below 5 are omitted here; all {len(texts)} scores are in `ratings.json`."]
    (OUT / "REVIEW.md").write_text("\n".join(lines))
    print({w: dist[w] for w in sorted(dist, reverse=True)}, "rises>=2:", rises,
          "listed (>=5):", sum(1 for s in scores.values() if s["weirdness"] >= 5))


if __name__ == "__main__":
    main()

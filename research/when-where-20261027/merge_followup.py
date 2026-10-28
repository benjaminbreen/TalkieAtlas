"""Merge the Haiku readings of the follow-up conversations (runs/neuron-followup-20261027) into followup_labels.json.

Each row keeps the persona's own answers verbatim (who, where, when), Haiku's quotes, types and labels
(FOLLOWUP_RUBRIC.md), and a gazetteer match for real places. Years outside 500-2100 ("the year fifty-five")
keep their quote but are not used as a year.

  .venv/bin/python sites/talkie-neuron-sample/merge_followup.py
"""
import json
from pathlib import Path
from gazetteer import resolve

here = Path(__file__).resolve().parent
judge = here / "build" / "followup"
run = here.parent.parent / "runs" / "neuron-followup-20261027" / "followups.jsonl"
KEYS = ["id", "where_quote", "where_type", "where_label", "place", "when_quote", "when_type", "year", "born", "consistent"]
WHERE = {"real place", "unnamed dwelling", "unnamed landscape", "habitat", "otherworld", "allegorical", "abstract", "everywhere or nowhere", "evasive", "garbled"}
WHEN = {"year", "other calendar", "era", "symbolic", "evasive", "garbled"}
convo = {r["path"]: r for r in map(json.loads, run.read_text().splitlines())}
rows, unresolved = [], []
for path in sorted(judge.glob("labels-*.json"), key=lambda p: int(p.stem.split("-")[1])):
    batch = json.loads(path.with_name(path.name.replace("labels", "batch")).read_text())
    labels = json.loads(path.read_text())
    assert [r["id"] for r in labels] == [r["id"] for r in batch], path
    for r, item in zip(labels, batch):
        assert set(r) == set(KEYS), r["id"]
        assert r["where_type"] in WHERE and r["when_type"] in WHEN, r["id"]
        assert not r["where_quote"] or r["where_quote"] in item["where"], r["id"]
        assert not r["when_quote"] or r["when_quote"] in item["when"], r["id"]
        c = convo[r["id"]]
        year = r["year"] if isinstance(r["year"], int) and 500 <= r["year"] <= 2100 else None
        born = r["born"] if isinstance(r["born"], int) and 500 <= r["born"] <= 2100 else None
        geo = resolve(r["place"]) if r["where_type"] == "real place" and r["place"] else None
        if r["where_type"] == "real place" and not geo: unresolved.append(r["place"])
        rows.append({**{k: r[k] for k in KEYS}, "year": year, "born": born, "kind": c["kind"], "edits": c["edits"],
                     "who": c["who"], "where": c["where"]["text"], "when": c["when"]["text"],
                     "geo": {"key": geo[0], "lat": geo[1], "lon": geo[2], "level": geo[3], "district": geo[4]} if geo else None})
(here / "followup_labels.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
print(json.dumps({"rows": len(rows), "conversations": len(convo), "years": sum(r["year"] is not None for r in rows),
                  "real_places": sum(r["where_type"] == "real place" for r in rows), "geocoded": sum(bool(r["geo"]) for r in rows),
                  "unresolved": sorted(set(unresolved))}))

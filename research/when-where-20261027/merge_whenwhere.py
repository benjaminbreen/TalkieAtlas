"""Merge the Haiku era-and-place annotations in build/whenwhere/ into whenwhere_labels.json,
and resolve each place with gazetteer.py (render_maps.mjs reads the geocodes).

  .venv/bin/python sites/talkie-neuron-sample/merge_whenwhere.py && node sites/talkie-neuron-sample/render_maps.mjs
"""
import json
from pathlib import Path
from gazetteer import resolve

here = Path(__file__).resolve().parent
src = here / "build" / "whenwhere"
KEYS = ["id", "stated_year", "stated_kind", "era_from", "era_to", "era_confidence", "era_clue",
        "place", "place_level", "place_stated", "place_confidence", "place_clue", "kind"]
rows = []
for path in sorted(src.glob("labels-*.json")):
    batch = json.loads(path.with_name(path.name.replace("labels", "batch")).read_text())
    labels = json.loads(path.read_text())
    assert [r["id"] for r in labels] == [r["id"] for r in batch], path
    for r in labels:
        assert set(r) == set(KEYS), r["id"]
        assert r["stated_year"] is None or isinstance(r["stated_year"], int), r["id"]
        assert (r["era_from"] is None) == (r["era_to"] is None) and (r["era_from"] is None or r["era_from"] <= r["era_to"]), r["id"]
        row = {k: r[k] for k in KEYS}
        geo = resolve(r["place"]) if r["place"] else None
        row["geo"] = {"key": geo[0], "lat": geo[1], "lon": geo[2], "level": geo[3], "district": geo[4]} if geo else None
        rows.append(row)
(here / "whenwhere_labels.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
places = {r["geo"]["key"] for r in rows if r["geo"]}
print(json.dumps({"personas": len(rows), "stated_year": sum(r["stated_year"] is not None for r in rows),
                  "era": sum(r["era_from"] is not None for r in rows), "place": sum(bool(r["place"]) for r in rows),
                  "geocoded": sum(bool(r["geo"]) for r in rows), "places": len(places)}))

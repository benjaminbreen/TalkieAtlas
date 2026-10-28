"""Admit only the user's three approved fresh replies to the ordinary library."""
import copy
import json
from pathlib import Path


def extend_fresh_calibration(data, root):
    root = Path(root)
    admissions_path = root / "library_admissions.json"
    if not admissions_path.exists():
        return data
    admissions = json.loads(admissions_path.read_text())
    choices = {r["id"]: r for r in admissions["selected"]}
    labels = {r["id"]: r for r in json.loads((root / "labels.json").read_text())}
    raw = [json.loads(line) for line in (root / "attempts.jsonl").read_text().splitlines()]
    assert set(choices) <= {r["id"] for r in raw}
    existing_ids = {r["id"] for r in data["attempts"]}
    existing_paths = {r["path"] for r in data["singles"] + data["pairs"]}
    existing_names = {r["judge"]["name"].casefold() for r in data["singles"]}
    batch = max(r.get("batch", 0) for r in data["attempts"]) + 1
    for source in raw:
        row = copy.deepcopy(source)
        rid = row["id"]
        assert rid not in existing_ids
        choice = choices.get(rid)
        label = labels.get(rid)
        row.update(batch=batch, job="fresh-neuron-calibration", run="fresh-neuron-calibration",
                   unlisted=not bool(choice), featured=bool(choice), library_approved=bool(choice))
        row["judge"] = dict(id=rid, name=label["name"] if label else "Unsteered control",
                            category="Unrated", description="", tags=[], weirdness=None,
                            coherence=None, rated=False)
        if label:
            row["judge"].update(weirdness=label["weirdness"], coherence=label["readability"],
                                rated=True, reviewer="gpt-6-luna")
            row["rating_provenance"] = dict(version=3, rubric="weirdness-v3.md", **label)
        if row["kind"] == "single":
            row["key"] = f"{row['layer']}:{row['neuron']}:{row['sign']}"
        if choice:
            base = f"{row['layer']}-{row['neuron']}-{'up' if row['sign'] > 0 else 'down'}"
            path = "n/" + base + "/"
            assert path not in existing_paths and choice["name"].casefold() not in existing_names
            assert not any(" ".join(s["text"].split()).casefold() == " ".join(row["text"].split()).casefold()
                           for s in data["singles"])
            row.update(base_slug=base, slug=base, canonical=True, path=path,
                       robot_icon="icons/" + base + ".svg", featured_order=choice["order"],
                       featured_reason=choice["description"])
            row["judge"].update(name=choice["name"], category="Persona",
                                description=choice["description"], tags=choice["tags"])
            row["editorial_rating"] = dict(weirdness=label["weirdness"], coherence=label["readability"],
                                           version=3, reviewer="gpt-6-luna")
            data["singles"].append(row)
            existing_paths.add(path)
            existing_names.add(choice["name"].casefold())
        data["attempts"].append(row)
        if row["kind"] == "control":
            data["controls"].append(row)
    protocol = json.loads((root / "protocol.json").read_text())
    data["manifest"]["sample_units"] += protocol["physical_neurons"]
    data["manifest"]["tested_directions"] += protocol["signed_conditions"]
    data["manifest"]["sampling"] += " Ten additional fresh physical neurons, both signs at 1×; three user-approved replies admitted to the library."
    data["status"].update(directions=len(data["singles"]), attempts=len(data["attempts"]),
                          sample_units=data["manifest"]["sample_units"])
    assert len({r["id"] for r in data["attempts"]}) == len(data["attempts"])
    return data

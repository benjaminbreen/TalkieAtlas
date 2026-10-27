"""Export a compatible completed Talkie run into the static viewer."""
import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("run", type=Path)
p.add_argument("--output", type=Path, default=ROOT / "public")
args = p.parse_args()
run, output = args.run.resolve(), args.output.resolve()
output.mkdir(parents=True, exist_ok=True)

def read(name, default):
    path = run / name
    return json.loads(path.read_text()) if path.exists() else default

attempts = [json.loads(line) for line in (run / "judged_attempts.jsonl").read_text().splitlines()]
singles = read("selected.json", [])
assert len({r["key"] for r in singles}) == len(singles), "Duplicate signed conditions"
assert all(r["judge"]["id"] == r["id"] for r in attempts), "Mismatched judgment IDs"
data = {
    "manifest": read("manifest.json", {}), "singles": singles,
    "pairs": read("pairs.json", []),
    "controls": [r for r in attempts if r["kind"] == "control"],
    "attempts": attempts, "retests": read("retests.json", {}),
    "identity_retests": read("identity_retest_labels.json", []),
    "status": read("status.json", {}),
}
for name, value in [("data.json", data), ("manifest.json", data["manifest"]),
                    ("identity-retests.json", data["identity_retests"])]:
    dest = output / name
    temp = dest.with_suffix(dest.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
    temp.replace(dest)
shutil.copyfile(ROOT / "research/JUDGE_RUBRIC.md", output / "rubric.md")
print(f"Exported {len(singles)} signed conditions and {len(data['pairs'])} pairs to {output}")

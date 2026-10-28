"""Ten genuinely fresh physical neurons, both signs, full-length saved replies."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import time

ROOT = Path(__file__).resolve().parents[1]


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "attempts.jsonl").exists(), "Refusing to overwrite generations"
    excluded = set()

    def collect(obj):
        if isinstance(obj, dict):
            layer, neuron = obj.get("layer"), obj.get("neuron")
            if type(layer) is int and type(neuron) is int and 0 <= layer < 40 and 0 <= neuron < 13696:
                excluded.add((layer, neuron))
            for edit in obj.get("edits", []):
                if isinstance(edit, list) and len(edit) >= 2 and all(type(v) is int for v in edit[:2]):
                    if 0 <= edit[0] < 40 and 0 <= edit[1] < 13696:
                        excluded.add(tuple(edit[:2]))
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    collect(value)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    collect(item)

    sources = []
    for path in sorted((ROOT / "runs").rglob("*.jsonl")):
        if out in path.parents:
            continue
        for line in path.read_text().splitlines():
            if line.strip():
                collect(json.loads(line))
        sources.append(str(path.relative_to(ROOT)))
    # Also exclude planned neurons conservatively, plus records in published data.
    paths = list((ROOT / "runs").rglob("manifest.json"))
    paths += list((ROOT / "runs").rglob("sample_plan.json"))
    paths += [ROOT / "sites/talkie-neuron-sample/dist/data.json",
              ROOT / "runs/unrated-library-ratings-20261028/source-site.json"]
    for path in sorted(set(paths)):
        if out not in path.parents:
            collect(json.loads(path.read_text()))
            sources.append(str(path.relative_to(ROOT)))
    seed = 20261028071
    rng = random.Random(seed)
    layers = [12, 16, 20, 23, 26, 29, 31, 33, 35, 37]
    units = [(layer, rng.choice([u for u in range(13696) if (layer, u) not in excluded])) for layer in layers]
    assert len(set(units)) == 10 and not set(units) & excluded
    conditions = [{"id": f"fresh{n:02d}-{'down' if sign < 0 else 'up'}", "kind": "single",
                   "layer": layer, "neuron": neuron, "sign": sign,
                   "edits": [[layer, neuron, sign, 1.0]]}
                  for n, (layer, neuron) in enumerate(units, 1) for sign in [-1, 1]]
    protocol = {"created_utc": datetime.now(timezone.utc).isoformat(), "seed": seed,
                "prompt": "Who are you?", "max_tokens": 160, "temperature": 0,
                "repeat_stop": False, "dose": 1.0, "physical_neurons": 10, "signed_conditions": 20,
                "selection": "One randomly chosen fresh physical neuron in each prespecified layer: " + str(layers) + ". Exploratory middle/late-layer emphasis; no output-based filtering.",
                "excluded_physical_neurons": len(excluded), "exclusion_sources": sources,
                "selected_neurons": [{"layer": l, "neuron": n} for l, n in units],
                "conditions": conditions, "novelty_check": "No selected physical neuron appears in scanned corpus records or manifests; identity novelty assessed separately after generation.",
                "rubric": "research_notes/talkie-weirdness-v3/WEIRDNESS_RUBRIC.md",
                "rubric_sha256": hashlib.sha256((ROOT / "research_notes/talkie-weirdness-v3/WEIRDNESS_RUBRIC.md").read_bytes()).hexdigest(),
                "limitations": ["Small exploratory sample; no guarantee of interesting or distinct identities", "One fixed dose and prompt, greedy quantized model; batch composition can affect outputs", "Fresh generations, not continuations; all outputs preserved including repetition"]}
    save(out / "protocol.json", protocol)
    save(out / "excluded-neurons.json", sorted(excluded))
    if args.prepare_only:
        print(json.dumps({k: protocol[k] for k in ["excluded_physical_neurons", "selected_neurons"]}), flush=True)
        return

    import mlx.core as mx
    from harness.engine import Loaded, format_chat, SPECIAL
    from harness.steer import Capture, Steer
    started = time.monotonic()
    save(out / "status.json", {"phase": "loading"})
    mx.set_cache_limit(1024**3)
    m = Loaded("it")
    ids = m.encode(format_chat([{"role": "user", "content": protocol["prompt"]}]))
    capture = Capture("resid")
    m.model(mx.array([ids]), hooks=capture)
    scales = {}
    for layer in layers:
        values = capture.get("resid", layer)[0, 1:].astype(mx.float32)
        norms = mx.sqrt(mx.sum(values * values, axis=-1))
        mx.eval(norms)
        ns = sorted(norms.tolist())
        scales[layer] = (ns[(len(ns)-1)//2] + ns[len(ns)//2]) / 2
    capture.clear()
    directions = {}
    for layer, neuron in units:
        basis = mx.zeros((1, 13696), dtype=mx.bfloat16)
        basis[0, neuron] = 1
        block = m.model.blocks[layer]
        vector = block.mlp.mlp_resid(basis).astype(mx.float32) * block.mlp_gain.astype(mx.float32)
        vector = vector / mx.sqrt(mx.sum(vector * vector, axis=-1, keepdims=True))
        mx.eval(vector)
        directions[layer, neuron] = vector[0]
    edits = [[]] + [[("resid", c["layer"], directions[c["layer"], c["neuron"]], c["sign"] * scales[c["layer"]])] for c in conditions]
    hook = Steer(edits)
    logits, cache = m.model(mx.array([ids] * len(edits)), hooks=hook)
    tokens = [[] for _ in edits]
    done = [False] * len(edits)
    ends = ["length"] * len(edits)
    save(out / "status.json", {"phase": "generating", "conditions": 20})
    for step in range(160):
        nxt = mx.argmax(logits[:, -1, :m.n_real], axis=-1)
        mx.eval(nxt)
        for index, token in enumerate(nxt.tolist()):
            if done[index]:
                continue
            if token in set(SPECIAL.values()):
                done[index] = True
                ends[index] = "finished"
            else:
                tokens[index].append(token)
        if all(done):
            break
        logits, cache = m.model(nxt[:, None], cache, hooks=hook)
        if (step + 1) % 40 == 0:
            print(f"Generated {step+1}/160 steps", flush=True)
    rows = []
    for index, condition in enumerate([{"id": "control", "kind": "control", "edits": []}] + conditions):
        rows.append({**condition, "prompt": protocol["prompt"], "max_tokens": 160,
                     "token_ids": tokens[index], "text": m.tok.decode(tokens[index]),
                     "termination": ends[index], "generation": "fresh", "temperature": 0})
    with (out / "attempts.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    save(out / "judge-input.json", [{"id": r["id"], "text": r["text"]} for r in rows if r["kind"] == "single"])
    save(out / "manifest.json", {**protocol, "residual_medians": scales, "seconds": round(time.monotonic()-started, 2),
                                "normalization": "Unit effective MLP write column including learned gain, scaled by unsteered prompt median residual norm (first token excluded); post-block addition at all positions.",
                                "model": "talkie-1930-13b-it", "precision": "8-bit weights / BF16 compute"})
    save(out / "status.json", {"phase": "complete", "saved_replies": len(rows)})
    print("Saved 20 fresh signed replies and one control", flush=True)


if __name__ == "__main__":
    main()

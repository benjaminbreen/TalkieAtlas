"""Ask each library persona where and when it is, in its own conversation.

For every persona (single neurons and two-neuron pairs judged Persona in the site data), replay the
original exchange exactly, with the same neuron edits at the same doses applied at every position:

    user: Who are you?   assistant: <its original reply, token ids from the site data>
    user: Where do you live?        assistant: <generated>
    user: What year is it now?      assistant: <generated>

Greedy decoding, one conversation at a time (histories differ in length and the model has no padding
mask). An unsteered control conversation is run first. Output is append-only followups.jsonl; --resume
skips paths already done.

    .venv/bin/python -m experiments.neuron_followup --out runs/neuron-followup-20261027 --only n/17-10423-down/ ...
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "sites/talkie-neuron-sample/dist/data.json"
REFERENCE = ROOT / "runs/neuron-site-sample-20261027/manifest.json"
FIRST = "Who are you?"
QUESTIONS = [("where", "Where do you live?"), ("when", "What year is it now?")]

def save(path, obj):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    temp.replace(path)

def personas(data):
    rows = [r for r in data["singles"] if r.get("canonical") is not False and r["judge"]["category"] == "Persona"]
    rows += [r for r in data["pairs"] if r.get("canonical") is not False and r["judge"]["category"] == "Persona"]
    return rows

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--tokens", type=int, default=100, help="cap per follow-up answer")
    p.add_argument("--only", nargs="*", help="site paths to run (pilot); default all personas")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--verify", action="store_true", help="also regenerate the first reply and record how many tokens match the saved one")
    args = p.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    log = out / "followups.jsonl"
    if log.exists() and not args.resume:
        raise RuntimeError("Refusing to overwrite an existing run; pass --resume")
    data = json.loads(DATA.read_text())
    todo = personas(data)
    if args.only:
        want = set(args.only)
        todo = [r for r in todo if r["path"] in want]
        assert len(todo) == len(want), f"unknown paths: {want - {r['path'] for r in todo}}"
    done = {json.loads(s)["path"] for s in log.read_text().splitlines()} if log.exists() else set()
    todo = [r for r in todo if r["path"] not in done]
    save(out / "status.json", {"phase": "waiting_for_gpu", "todo": len(todo), "done": len(done)})

    import mlx.core as mx
    mx.set_cache_limit(1024**3)
    from harness.engine import Loaded, format_chat, SPECIAL
    from harness.steer import Capture, Steer
    m = Loaded("it")
    END, STOP = SPECIAL["<|end|>"], set(SPECIAL.values())

    # Per-layer dose unit: median residual norm on the unsteered first prompt, first token excluded,
    # exactly as in the screening runs (checked against their manifest).
    first_ids = m.encode(format_chat([{"role": "user", "content": FIRST}]))
    cap = Capture("resid")
    m.model(mx.array([first_ids]), hooks=cap)
    scales = {}
    for layer in range(40):
        vals = cap.get("resid", layer)[0, 1:].astype(mx.float32)
        ordered = sorted(mx.sqrt(mx.sum(vals * vals, axis=-1)).tolist())
        n = len(ordered)
        scales[layer] = (ordered[(n - 1) // 2] + ordered[n // 2]) / 2
    cap.clear()
    ref = {int(k): v for k, v in json.loads(REFERENCE.read_text())["residual_medians"].items()}
    drift = max(abs(scales[l] - ref[l]) / ref[l] for l in range(40))
    assert drift < 1e-3, f"dose units differ from the screening run by {drift:.2e}"

    cols = {}
    def direction(layer, unit):
        if (layer, unit) not in cols:
            basis = mx.zeros((1, 13696), dtype=mx.bfloat16)
            basis[0, unit] = 1
            block = m.model.blocks[layer]
            c = (block.mlp.mlp_resid(basis).astype(mx.float32) * block.mlp_gain.astype(mx.float32))[0]
            cols[layer, unit] = c / mx.sqrt(mx.sum(c * c))
        return cols[layer, unit]

    def turn(prefix_ids, edits):
        """Greedy answer to the conversation so far, under the given edits (same repeat stop as screening)."""
        hooks = Steer([[("resid", l, direction(l, u), s * a * scales[l]) for l, u, s, a in edits]])
        logits, cache = m.model(mx.array([prefix_ids]), hooks=hooks)
        toks, end = [], "length"
        for _ in range(args.tokens):
            t = int(mx.argmax(logits[0, -1, :m.n_real]).item())
            if t in STOP: end = "finished"; break
            toks.append(t)
            if len(toks) >= 12 and any(len(toks) >= 3 * k and toks[-k:] == toks[-2 * k:-k] == toks[-3 * k:-2 * k] for k in range(1, 17)):
                end = "repeating"; break
            logits, cache = m.model(mx.array([[t]]), cache, hooks=hooks)
        return toks, end

    def conversation(first_reply_ids, edits):
        ids = list(first_ids) + list(first_reply_ids) + [END]
        answers = {}
        for key, q in QUESTIONS:
            ids += m.encode(f"<|user|>{q}<|end|><|assistant|>")
            toks, end = turn(ids, edits)
            answers[key] = {"text": m.tok.decode(toks), "token_ids": toks, "termination": end}
            ids += toks + [END]
        return answers

    manifest = {"created": datetime.now(timezone.utc).isoformat(), "model": "talkie-1930-13b-it", "precision": "8-bit weights / BF16 compute",
                "source": str(DATA.relative_to(ROOT)), "first_prompt": FIRST, "questions": [q for _, q in QUESTIONS],
                "history": "Original Who are you? reply replayed from its saved token ids, closed with <|end|>.",
                "intervention": "Same signed MLP write directions and doses as the screening reply, at every prompt and generated position.",
                "decoding": f"Greedy, up to {args.tokens} tokens per answer; stop at a chat delimiter or a block of 1-16 tokens repeated three times.",
                "residual_medians": scales, "max_relative_dose_drift_vs_screening": drift,
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if not (out / "manifest.json").exists(): save(out / "manifest.json", manifest)
    if "control" not in done and not args.only:
        todo = [{"path": "control", "kind": "control", "edits": [], "text": None, "token_ids": None}] + todo

    started = time.monotonic()
    with log.open("a") as f:
        for i, r in enumerate(todo):
            t0 = time.monotonic()
            if r["path"] == "control":
                reply, _ = turn(list(first_ids), [])
                r = {**r, "text": m.tok.decode(reply), "token_ids": reply}
            answers = conversation(r["token_ids"], r["edits"])
            if args.verify and r["path"] != "control":
                again, _ = turn(list(first_ids), r["edits"])
                same = next((k for k, (a, b) in enumerate(zip(again, r["token_ids"])) if a != b), min(len(again), len(r["token_ids"])))
                answers["replay_match"] = {"matching_prefix": same, "saved": len(r["token_ids"]), "regenerated": len(again)}
            row = {"path": r["path"], "kind": r["kind"], "edits": r["edits"], "name": r.get("judge", {}).get("name"),
                   "who": r["text"], **answers, "seconds": round(time.monotonic() - t0, 1)}
            f.write(json.dumps(row, ensure_ascii=False) + "\n"); f.flush()
            print(f"{i + 1}/{len(todo)} {r['path']} {row['seconds']}s | where: {answers['where']['text'][:70]!r} | when: {answers['when']['text'][:50]!r}", flush=True)
            save(out / "status.json", {"phase": "running", "done": len(done) + i + 1, "total": len(done) + len(todo),
                                       "elapsed_seconds": round(time.monotonic() - started), "last": r["path"]})
            mx.clear_cache()
    save(out / "status.json", {"phase": "finished", "done": len(done) + len(todo), "elapsed_seconds": round(time.monotonic() - started)})

if __name__ == "__main__":
    main()

"""Sampled replication of qwen-neurons-site: fresh outputs, external Luna judgments.

Run with --out PATH. Judge workers consume judge_tasks/*.json and write matching
judge_labels/*.json. Raw attempts and labels are append-only/auditable. No API keys.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

ROOT = Path(__file__).resolve().parents[1]
PROMPT = "Who are you?"
DOSES = [1.25, 1.0, 0.75, 0.5]

def save(path, obj):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    temp.replace(path)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--units", type=int, default=400)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--tokens", type=int, default=160)
    p.add_argument("--seed", type=int, default=20261027)
    p.add_argument("--pair-limit", type=int, default=8)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--reuse-retests", action="store_true")
    p.add_argument("--identity-file", type=Path)
    p.add_argument("--sample-plan", type=Path)
    p.add_argument("--batch-start", type=int, default=0)
    p.add_argument("--singles-only", action="store_true")
    p.add_argument("--candidate-ids", type=Path)
    args = p.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for folder in ["judge_tasks", "judge_labels"]:
        (out / folder).mkdir(exist_ok=True)
    if (out / "attempts.jsonl").exists() and not args.resume:
        raise RuntimeError("Refusing to overwrite an existing run")
    started = time.monotonic()
    save(out / "status.json", {"phase": "waiting_for_gpu", "created": datetime.now(timezone.utc).isoformat()})
    import mlx.core as mx
    # Keep cached allocations from crowding the 48 GB shared-memory Mac.
    mx.set_cache_limit(1024**3)
    from harness.engine import Loaded, format_chat, SPECIAL
    from harness.steer import Capture, Steer
    m = Loaded("it")
    ids = m.encode(format_chat([{"role": "user", "content": PROMPT}]))
    cap = Capture("resid")
    m.model(mx.array([ids]), hooks=cap)
    scales = {}
    for layer in range(40):
        vals = cap.get("resid", layer)[0, 1:].astype(mx.float32)
        norms = mx.sqrt(mx.sum(vals * vals, axis=-1))
        mx.eval(norms)
        ordered = sorted(norms.tolist())
        n = len(ordered)
        scales[layer] = (ordered[(n-1)//2] + ordered[n//2]) / 2
    cap.clear()
    rng = random.Random(args.seed)
    chosen = [(layer, u) for layer in range(40) for u in rng.sample(range(13696), args.units//40)]
    if args.sample_plan:
        plan=json.loads(args.sample_plan.read_text())
        chosen=[(r["layer"],r["neuron"]) for r in plan["selected_neurons"]]
    assert len(chosen) == args.units, "Sample size mismatch"
    assert len(set(chosen)) == len(chosen), "Duplicate units"
    directions = {}
    for layer in range(40):
        units = [u for l, u in chosen if l == layer]
        basis = mx.zeros((len(units),13696), dtype=mx.bfloat16)
        for row, u in enumerate(units): basis[row,u] = 1
        block = m.model.blocks[layer]
        cols = block.mlp.mlp_resid(basis).astype(mx.float32) * block.mlp_gain.astype(mx.float32)
        cols = cols / mx.sqrt(mx.sum(cols*cols,axis=-1,keepdims=True))
        mx.eval(cols)
        for row,u in enumerate(units): directions[layer,u] = cols[row]
    manifest = {
        "created": datetime.now(timezone.utc).isoformat(), "model":"talkie-1930-13b-it", "precision":"8-bit weights / BF16 compute",
        "prompt":PROMPT, "prompt_ids":ids, "temperature":0,"max_tokens":args.tokens,
        "layers":40,"neurons_per_layer":13696,"population":547840,"sample_units":args.units,
        "sampling":plan["sampling"] if args.sample_plan else "Equal random sample per layer without replacement", "seed":args.seed,
        "doses":DOSES,"coherence_threshold":5,"judge":"GPT-6 Luna (Codex subagents)",
        "normalization":"Unsteered prompt median residual norm per layer, first token excluded. Effective MLP write column includes Talkie scalar mlp_gain.",
        "intervention":"Add signed normalized MLP write direction to post-block residual at every prompt and generated position.",
        "repeat_stop":"Stop on an exact token block of length 1–16 repeated three consecutive times (after >=12 output tokens).",
        "selected_neurons":[{"layer":l,"neuron":u} for l,u in chosen],"residual_medians":scales,
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "reference":"https://qwen-neurons-site.vercel.app/",
        "differences":["Adaptive sample, not exhaustive; selection differs from the uniform pilot", "Luna judge with published rubric, not Haiku or its unavailable original judge prompt", "Talkie-specific chat template and MLP gain", "Explicit repeat-stop rule; reference implementation not available", "Human self-identification is normal for Talkie; category is not evidence of a changed identity", "Pairs are exploratory and not selected using the reference's full reproducibility protocol"]}
    if args.resume:
        previous=json.loads((out/"manifest.json").read_text())
        previous.setdefault("resumes",[]).append({"time":datetime.now(timezone.utc).isoformat(),"batch":args.batch,"cache_limit_bytes":1024**3,"script_sha256":manifest["script_sha256"]})
        if args.identity_file:
            previous['pair_retest_criterion']='GPT-6 Luna comparison confirms preservation of the specific identity; exact text matches are recorded separately.'
            previous['identity_retest_judgments_sha256']=hashlib.sha256(args.identity_file.read_bytes()).hexdigest()
        manifest=previous
    save(out/"manifest.json",manifest)
    (out/(f"script_resume_{len(manifest.get('resumes',[]))}.py" if args.resume else "script_snapshot.py")).write_bytes(Path(__file__).read_bytes())
    attempts=[json.loads(s) for s in (out/"judged_attempts.jsonl").read_text().splitlines()] if args.resume else []
    selected=json.loads((out/"selected.json").read_text()) if args.resume else []
    taskno=max([int(f.stem.split("-")[1]) for f in (out/"judge_tasks").glob("*.json")],default=-1)+1
    raw=[json.loads(s) for s in (out/"attempts.jsonl").read_text().splitlines()] if args.resume else []
    batchno=max([r["batch"] for r in raw],default=args.batch_start-1)+1
    if args.resume:
        known={r["id"] for r in attempts}
        orphaned=[r for r in raw if r["id"] not in known]
        while orphaned:
            labs={r['id']:r for f in (out/'judge_labels').glob('*.json') for r in json.loads(f.read_text())}
            if all(r['id'] in labs for r in orphaned):break
            time.sleep(2)
        with (out/'judged_attempts.jsonl').open('a') as f:
            for r in orphaned:
                r['judge']=labs[r['id']];attempts.append(r);f.write(json.dumps(r,ensure_ascii=False)+'\n')
        selected_keys={r['key'] for r in selected}
        for r in orphaned:
            if r['kind']=='single' and r['key'] not in selected_keys and (r['judge']['coherence']>=5 or r['edits'][0][3]==DOSES[-1]):
                selected.append(r);selected_keys.add(r['key'])

    def generate(rows):
        hooks=Steer(rows)
        logits,cache=m.model(mx.array([ids]*len(rows)),hooks=hooks)
        results=[[] for _ in rows]; done=[False]*len(rows); ends=["length"]*len(rows)
        for _ in range(args.tokens):
            tok=mx.argmax(logits[:,-1,:m.n_real],axis=-1);mx.eval(tok)
            for i,t in enumerate(tok.tolist()):
                if done[i]: continue
                if t in set(SPECIAL.values()): done[i]=True;ends[i]="finished";continue
                results[i].append(t)
                ts=results[i]
                if len(ts)>=12 and any(len(ts)>=3*k and ts[-k:]==ts[-2*k:-k]==ts[-3*k:-2*k] for k in range(1,17)):
                    done[i]=True;ends[i]="repeating"
            if all(done):break
            logits,cache=m.model(tok[:,None],cache,hooks=hooks)
        return [{"text":m.tok.decode(t),"token_ids":t,"termination":e} for t,e in zip(results,ends)]

    def enqueue(batch):
        nonlocal taskno
        groups=[]
        # Small files keep independent Luna judgments bounded and quick.
        for s in range(0,len(batch),16):
            fname=f"task-{taskno:05d}.json";taskno+=1
            save(out/"judge_tasks"/fname,[{"id":r["id"],"text":r["text"]} for r in batch[s:s+16]])
            groups.append(fname)
        return groups

    def judged(batch,groups):
        while not all((out/"judge_labels"/f).exists() for f in groups):time.sleep(2)
        labels={r["id"]:r for f in groups for r in json.loads((out/"judge_labels"/f).read_text())}
        assert set(labels)=={r["id"] for r in batch}, "Missing/extra judge labels"
        for r in batch:
            lab=labels[r["id"]]
            assert lab["category"] in ["Persona","Changed assistant","Off-topic","Incoherent","Normal Talkie"]
            assert 0<=lab["coherence"]<=10 and 0<=lab["weirdness"]<=10
            r["judge"]=lab
        return batch

    def finish_batch(records,groups):
        records=judged(records,groups)
        with (out/"judged_attempts.jsonl").open("a") as f:
            for r in records:f.write(json.dumps(r,ensure_ascii=False)+"\n")
        attempts.extend(records)
        save(out/"status.json",{"phase":"generating","attempts":len(attempts),"selected":len(selected),"elapsed_seconds":round(time.monotonic()-started,1)})
        return records[1:]

    def run_batch(conditions,kind="single",defer=False):
        nonlocal batchno
        rows=[[]]+[[('resid',l,directions[l,u],sign*alpha*scales[l]) for l,u,sign,alpha in c["edits"]] for c in conditions]
        t0=time.monotonic();outs=generate(rows)
        records=[]
        for i,o in enumerate(outs):
            condition={"kind":"control","edits":[]} if i==0 else conditions[i-1]
            r={"id":f"b{batchno:04d}-r{i:02d}","batch":batchno,"kind":kind if i else "control",**condition,**o}
            records.append(r)
        with (out/"attempts.jsonl").open("a") as f:
            for r in records:f.write(json.dumps(r,ensure_ascii=False)+"\n")
        print(f"Batch {batchno}: {len(conditions)} {kind} conditions in {time.monotonic()-t0:.1f}s; peak {mx.get_peak_memory()/1024**3:.1f} GB; queued for Luna",flush=True)
        batchno+=1
        groups=enqueue(records)
        mx.clear_cache()
        return (records,groups) if defer else finish_batch(records,groups)

    pending=[{"kind":"single","key":f"{l}:{u}:{sign}","layer":l,"neuron":u,"sign":sign,"edits":[[l,u,sign,DOSES[0]]]} for l,u in chosen for sign in [-1,1]]
    rng.shuffle(pending)
    selected_keys={r["key"] for r in selected}
    pending=[r for r in pending if r["key"] not in selected_keys]
    prior={(r["key"],r["edits"][0][3]):r for r in attempts if r["kind"]=="single"}
    for alpha in DOSES:
        retry=[];todo=[]
        for c in pending:
            prev=prior.get((c["key"],alpha))
            if prev:
                if prev["judge"]["coherence"]>=5 or alpha==DOSES[-1]:selected.append(prev)
                else:retry.append(c)
            else:todo.append(c)
        jobs=[]
        def accept(rows):
            for r in rows:
                if r["judge"]["coherence"]>=5 or alpha==DOSES[-1]:selected.append(r)
                else:retry.append({k:v for k,v in r.items() if k in ["kind","key","layer","neuron","sign","edits"]})
            save(out/"selected.json",selected)
        for start in range(0,len(todo),args.batch):
            conds=todo[start:start+args.batch]
            for c in conds:c["edits"][0][3]=alpha
            jobs.append(run_batch(conds,defer=True))
            unfinished=[]
            for records,groups in jobs:
                if all((out/'judge_labels'/f).exists() for f in groups):accept(finish_batch(records,groups))
                else:unfinished.append((records,groups))
            jobs=unfinished
        for records,groups in jobs:accept(finish_batch(records,groups))
        pending=retry
    if args.singles_only:
        save(out/"status.json",{"phase":"singles_complete","sample_units":args.units,"directions":len(selected),"attempts":len(attempts),"elapsed_seconds":round(time.monotonic()-started,1)})
        save(out/"SINGLES_DONE.json",{"finished":datetime.now(timezone.utc).isoformat()})
        print("Single-neuron screen complete",out,flush=True)
        return
    # Selected high-interest candidates are retested as singletons in a new batch layout.
    candidates=sorted([r for r in selected if r["judge"]["category"]=="Persona" and r["judge"]["coherence"]>=6],key=lambda r:(r["judge"]["weirdness"],r["judge"]["coherence"]),reverse=True)[:args.pair_limit]
    if args.candidate_ids:
        candidate_ids=json.loads(args.candidate_ids.read_text())
        by_id={r["id"]:r for r in selected}
        candidates=[by_id[i] for i in candidate_ids]
    if len(candidates)>1:
        reconds=[{k:v for k,v in r.items() if k in ["key","layer","neuron","sign","edits"]}|{"kind":"retest","source_id":r["id"]} for r in candidates]
        if args.reuse_retests:
            old_retests=json.loads((out/'retests.json').read_text())
            by_source={r['source_id']:r for r in old_retests['rows']}
            reruns=[by_source[c['source_id']] for c in reconds]
        else:reruns=run_batch(reconds,"retest")
        # Exact reproducibility is recorded; pairs require exact rerun text.
        exact=[orig for orig,new in zip(candidates,reruns) if orig["text"]==new["text"]]
        if args.identity_file:
            verdicts={r['source_id']:r for r in json.loads(args.identity_file.read_text())}
            assert set(verdicts)=={r['id'] for r in candidates}
            stable=[r for r in candidates if verdicts[r['id']]['same_identity'] is True]
        else:stable=exact
        old_pairs=json.loads((out/'pairs.json').read_text()) if args.reuse_retests else []
        old_keys={r['key'] for r in old_pairs}
        pairs=[]
        for a,b in itertools.combinations(stable,2):
            if (a["layer"],a["neuron"])==(b["layer"],b["neuron"]):continue
            key=a['key']+'+'+b['key']
            if key in old_keys:continue
            pairs.append({"kind":"pair","key":key,"parents":[a["id"],b["id"]],"edits":[*a["edits"],*b["edits"]],"factor":1.0})
        pair_selected=list(old_pairs)
        for factor in [1.0,0.75,0.5]:
            retry=[]
            for start in range(0,len(pairs),args.batch):
                conditions=[]
                for pair in pairs[start:start+args.batch]:
                    c={**pair,"factor":factor,"edits":[[l,u,s,alpha*factor] for l,u,s,alpha in pair["edits"]]}
                    conditions.append(c)
                for r in run_batch(conditions,"pair"):
                    if r["judge"]["coherence"]>=5 or factor==0.5:pair_selected.append(r)
                    else:
                        base=next(p for p in pairs if p["key"]==r["key"]);retry.append(base)
            pairs=retry
        save(out/"pairs.json",pair_selected)
        save(out/"retests.json",{"candidates":len(candidates),"exact_matches":len(exact),"identity_matches":len(stable) if args.identity_file else None,"paired_candidates":len(stable),"criterion":"Luna-confirmed identity consistency" if args.identity_file else "Exact text match","rows":reruns})
    save(out/"status.json",{"phase":"complete","sample_units":args.units,"directions":len(selected),"attempts":len(attempts),"elapsed_seconds":round(time.monotonic()-started,1),"categories":dict(Counter(r["judge"]["category"] for r in selected))})
    save(out/"DONE.json",{"finished":datetime.now(timezone.utc).isoformat()})
    print("Complete",out,flush=True)

if __name__=="__main__":main()

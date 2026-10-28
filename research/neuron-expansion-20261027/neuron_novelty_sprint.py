"""Time-bounded wide neuron search with an interactive, auditable follow-up inbox.

One GPU process; no external judge dependency. Screening statistics are mechanical
review aids, never persona/coherence labels. Editorial labels are stored separately.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import re
import time

ROOT = Path(__file__).resolve().parents[1]
PROMPT = "Who are you?"


def save(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def mechanical(text):
    words = re.findall(r"[\w'-]+", text.lower())
    grams = list(zip(words, words[1:], words[2:]))
    repeated = max(Counter(grams).values(), default=0)
    return {"words": len(words), "unique_fraction": round(len(set(words))/max(1,len(words)),3),
            "max_trigram_repeats": repeated,
            "self_description": bool(re.search(r"\b(i am|i'm|my name|i was|my dwelling)\b", text, re.I))}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--units", type=int, default=6000)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--scan-tokens", type=int, default=96)
    p.add_argument("--scan-strengths", default="1", help="Comma-separated solo doses")
    p.add_argument("--late-extra", type=int, default=0, help="Additional units split across layers 20–39, included in --units")
    p.add_argument("--group-conditions", action="store_true", help="Keep each fresh unit's signs and doses in one batch")
    p.add_argument("--exclude", type=Path)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--scan-seconds", type=int, default=1020)
    p.add_argument("--total-seconds", type=int, default=1680)
    p.add_argument("--seed", type=int, default=202610272037)
    p.add_argument("--batch-start", type=int, help="Distinct record-number range for a new study")
    p.add_argument("--study-plan", type=Path, help="Protocol metadata for this study")
    a = p.parse_args()
    out = a.out.resolve(); out.mkdir(exist_ok=True, parents=True)
    if not a.resume and ((out/"attempts.jsonl").exists() or (out/"manifest.json").exists()):
        raise RuntimeError("Refusing to overwrite an existing generation")
    for name in ["inbox", "completed"]: (out/name).mkdir(exist_ok=True)
    start = time.monotonic()
    previous=[json.loads(s) for s in (out/"attempts.jsonl").read_text().splitlines()] if a.resume else []
    save(out/"status.json", {"phase":"loading", "started":datetime.now(timezone.utc).isoformat(),"resume":a.resume})
    import mlx.core as mx
    from harness.engine import Loaded, format_chat, SPECIAL
    from harness.steer import Capture, Steer
    mx.set_cache_limit(1024**3)
    m = Loaded("it")
    prompt_ids = m.encode(format_chat([{"role":"user", "content":PROMPT}]))
    cap = Capture("resid"); m.model(mx.array([prompt_ids]), hooks=cap)
    scales = {}
    for l in range(40):
        vals = cap.get("resid",l)[0,1:].astype(mx.float32)
        ns=mx.sqrt(mx.sum(vals*vals,axis=-1)); mx.eval(ns); s=sorted(ns.tolist())
        scales[l]=(s[(len(s)-1)//2]+s[len(s)//2])/2
    cap.clear()
    old = json.loads((ROOT/"sites/talkie-neuron-sample/dist/data.json").read_text())
    strengths=[float(x) for x in a.scan_strengths.split(',')]
    assert strengths and all(0<x<=1.25 for x in strengths)
    excluded={(int(e[0]),int(e[1])) for r in old['attempts'] for e in r.get('edits',[])}
    if a.exclude and (a.exclude/"attempts.jsonl").exists():
        for line in (a.exclude/"attempts.jsonl").read_text().splitlines():
            r=json.loads(line)
            if r['kind']=='single':excluded.add((r['layer'],r['neuron']))
    rng=random.Random(a.seed); units=[]
    assert (a.units-a.late_extra)%40==0 and a.late_extra%20==0
    for l in range(40):
        available=[u for u in range(13696) if (l,u) not in excluded]
        count=(a.units-a.late_extra)//40+(a.late_extra//20 if l>=20 else 0)
        for u in rng.sample(available,count): units.append((l,u))
    if a.resume:
        prior_manifest=json.loads((out/"manifest.json").read_text())
        units=[(r['layer'],r['neuron']) for r in prior_manifest['selected_neurons']]
    assert len(units)==a.units
    directions={}

    def prepare(edits):
        needed={(l,u) for e in edits for l,u,s,alpha in e} - set(directions)
        for l in sorted({l for l,u in needed}):
            us=sorted(u for ll,u in needed if ll==l)
            basis=mx.zeros((len(us),13696),dtype=mx.bfloat16)
            for i,u in enumerate(us):basis[i,u]=1
            block=m.model.blocks[l]
            vs=block.mlp.mlp_resid(basis).astype(mx.float32)*block.mlp_gain.astype(mx.float32)
            vs=vs/mx.sqrt(mx.sum(vs*vs,axis=-1,keepdims=True)); mx.eval(vs)
            for i,u in enumerate(us):directions[l,u]=vs[i]

    manifest={"created":datetime.now(timezone.utc).isoformat(),"model":"talkie-1930-13b-it",
        "precision":"8-bit weights / BF16 compute","prompt":PROMPT,"temperature":0,
        "seed":a.seed,"planned_units":a.units,"planned_directions":a.units*2,"planned_solo_conditions":a.units*2*len(strengths),
        "selection":"Equal random fresh units per layer, excluding all previously screened library units; both signs, shuffled once before generation. Time cutoff may leave incomplete units.",
        "scan_strength":strengths[0] if len(strengths)==1 else strengths,"scan_tokens":a.scan_tokens,"followup_tokens":160,
        "normalization":"Signed unit effective MLP write column, including learned MLP gain, multiplied by prompt residual median norm and dose; added after the block at all positions.",
        "residual_medians":scales,"scan_seconds":a.scan_seconds,"total_seconds":a.total_seconds,
        "judging":"Codex editorial review of deduplicated discovery replies and selected pair replies; mechanical triage is not a quality or identity judge. Unreviewed outputs retain no invented ratings.",
        "goal":"Surprising, readable new personas; literal preservation of both parent identities is not required.",
        "limitations":["Time-limited exploratory sample, not an exhaustive atlas",f"Wide screen uses one fixed 1.0× dose and {a.scan_tokens}-token cap; finalists use 160 tokens","Selection is editorial, not blinded or a population estimate","One prompt, greedy decoding, quantized model; batch layout can affect replies"],
        "selected_neurons":[{"layer":l,"neuron":u} for l,u in units],
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if a.study_plan:
        study=json.loads(a.study_plan.read_text())
        manifest.update(study=study,selection=study['selection'],goal=study['goal'],limitations=study['limitations'])
    if a.resume:
        prior_manifest.setdefault('resumes',[]).append({'at':datetime.now(timezone.utc).isoformat(),'batch':a.batch,'scan_tokens':a.scan_tokens,'remaining_scan_seconds':a.scan_seconds,'remaining_total_seconds':a.total_seconds,'reason':'Measured throughput optimization; preserve all prior attempts and skip previously generated conditions.'})
        manifest=prior_manifest
    save(out/"manifest.json",manifest); (out/(f"script_resume_{len(manifest.get('resumes',[]))}.py" if a.resume else "script_snapshot.py")).write_bytes(Path(__file__).read_bytes())
    if a.group_conditions:rng.shuffle(units)
    pending=[{"kind":"single","key":f"{l}:{u}:{s}","layer":l,"neuron":u,"sign":s,"edits":[[l,u,s,d]],"screen_strength":d} for l,u in units for s in [-1,1] for d in strengths]
    if not a.group_conditions:rng.shuffle(pending)
    signature=lambda r:(r['key'],json.dumps(r['edits']))
    known={signature(r) for r in previous if r['kind']=='single' and r.get('job')=='scan'}
    pending=[r for r in pending if signature(r) not in known]
    batch=max((r['batch'] for r in previous),default=(a.batch_start-1 if a.batch_start is not None else 3999 if a.exclude else 2999))+1
    first_batch=batch; scanned=0; attempts=len(previous); all_records=list(previous)

    def run(conditions,tokens=96,prompt=PROMPT,job="scan"):
        nonlocal batch,attempts
        prepare([c["edits"] for c in conditions])
        ids=prompt_ids if prompt==PROMPT else m.encode(format_chat([{"role":"user","content":prompt}]))
        rows=[[]]+[[('resid',l,directions[l,u],s*alpha*scales[l]) for l,u,s,alpha in c["edits"]] for c in conditions]
        hook=Steer(rows); t=time.monotonic(); logits,cache=m.model(mx.array([ids]*len(rows)),hooks=hook)
        result=[[] for _ in rows]; done=[False]*len(rows); ends=["length"]*len(rows)
        for step in range(tokens):
            ts=mx.argmax(logits[:,-1,:m.n_real],axis=-1);mx.eval(ts)
            for i,tok in enumerate(ts.tolist()):
                if done[i]:continue
                if tok in set(SPECIAL.values()):done[i]=True;ends[i]="finished";continue
                result[i].append(tok); r=result[i]
                if len(r)>=12 and any(len(r)>=3*k and r[-k:]==r[-2*k:-k]==r[-3*k:-2*k] for k in range(1,17)):
                    done[i]=True;ends[i]="repeating"
            if all(done):break
            if time.monotonic()-start>a.total_seconds:
                ends=["time_limit" if not d else e for d,e in zip(done,ends)];break
            logits,cache=m.model(ts[:,None],cache,hooks=hook)
        records=[]
        for i,(toks,end) in enumerate(zip(result,ends)):
            c={"kind":"control","edits":[]} if i==0 else conditions[i-1]
            text=m.tok.decode(toks)
            records.append({"id":f"s{batch:05d}-r{i:03d}","batch":batch,"job":job,"prompt":prompt,"max_tokens":tokens,**c,"text":text,"token_ids":toks,"termination":end,"triage":mechanical(text)})
        with (out/"attempts.jsonl").open("a") as f:
            for r in records:f.write(json.dumps(r,ensure_ascii=False)+"\n")
        all_records.extend(records); attempts+=len(records);batch+=1
        save(out/"status.json",{"phase":job,"scan_directions":scanned,"attempts":attempts,"batches":batch-first_batch,"elapsed_seconds":round(time.monotonic()-start,1),"latest_batch_seconds":round(time.monotonic()-t,2),"peak_gb":round(mx.get_peak_memory()/1024**3,2)})
        print(f"{job}: {len(conditions)} conditions, {time.monotonic()-t:.2f}s, scanned {scanned}, elapsed {time.monotonic()-start:.1f}s",flush=True)
        mx.clear_cache()
        return records

    def jobs():
        for path in sorted((out/"inbox").glob("*.json")):
            job=json.loads(path.read_text()); records=[r for r in all_records if r.get('job')==path.stem]
            def signature(c):return json.dumps({k:c.get(k) for k in ['kind','key','source_id','edits','parents']},sort_keys=True)
            done={signature(r) for r in records if r['kind']!='control'}
            conditions=[c for c in job["conditions"] if signature(c) not in done]
            job_batch=job.get('batch',min(a.batch,32) if job.get('tokens',160)>64 else a.batch)
            for i in range(0,len(conditions),job_batch):
                if time.monotonic()-start>a.total_seconds:break
                records.extend(run(conditions[i:i+job_batch],job.get("tokens",160),job.get("prompt",PROMPT),path.stem))
            save(out/"completed"/path.name,{"job":job,"rows":records,"finished":datetime.now(timezone.utc).isoformat()})
            path.rename(out/"completed"/(path.stem+".request.json"))

    while scanned<len(pending) and time.monotonic()-start<a.scan_seconds and not (out/"STOP_SCAN").exists():
        jobs()
        conditions=pending[scanned:scanned+a.batch];scanned+=len(conditions)
        settings_path=out/"settings.json"
        settings=json.loads(settings_path.read_text()) if settings_path.exists() else {}
        run(conditions,settings.get("scan_tokens",a.scan_tokens))
        a.batch=settings.get("batch",a.batch)
    save(out/"SCAN_DONE.json",{"directions":scanned,"elapsed_seconds":round(time.monotonic()-start,1)})
    save(out/"status.json",{"phase":"followups_ready","scan_directions":scanned,"attempts":attempts,"elapsed_seconds":round(time.monotonic()-start,1)})
    while time.monotonic()-start<a.total_seconds and not (out/"FINISH").exists():
        jobs();time.sleep(1)
    manifest.update({"tested_directions":scanned,"sample_units":len({(r['layer'],r['neuron']) for r in all_records if r['kind']=='single'}),"attempts":attempts,"elapsed_seconds":round(time.monotonic()-start,1)})
    save(out/"manifest.json",manifest);save(out/"DONE.json",{"finished":datetime.now(timezone.utc).isoformat(),"directions":scanned,"attempts":attempts})
    print("Finished",flush=True)


if __name__=="__main__":main()

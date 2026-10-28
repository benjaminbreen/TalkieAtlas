"""Audit and finalize the completed pair-strength study without rewriting evidence."""
import hashlib,json
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from experiments.review_pair_strength_search import RUN,ROOT,read

def main():
    assert (RUN/'DONE.json').exists(),'Wait for the GPU worker to finish'
    assert not list((RUN/'inbox').glob('*.json')),'A queued generation job remains'
    rows=read();byid={r['id']:r for r in rows}
    assert len(rows)==len(byid)
    parents={r['id']:r for r in json.loads((RUN/'parents.json').read_text())}
    plan=json.loads((RUN/'pair_plan.json').read_text());pairs={p['id']:p for p in plan}
    old=json.loads((ROOT/'sites/talkie-neuron-sample/dist/data.json').read_text())
    assert not set(byid)&{r['id'] for r in old['attempts']}
    batches=defaultdict(list);screen=defaultdict(list);full=defaultdict(list)
    for r in rows:
        batches[r['batch']].append(r)
        assert r['prompt']=='Who are you?'
        assert len(r['token_ids'])<=r['max_tokens']
        assert r['termination'] in ['finished','length','repeating']
        assert all(isinstance(t,int) and 0<=t<65540 for t in r['token_ids'])
        if r['kind']=='control':assert r['edits']==[]
        if r['kind'] in ['pair','ablation']:
            assert r['parents']==pairs[r['pair_id']]['parents']
            assert len(r['edits'])==len(r['parents'])==2
            assert len({tuple(e[:2]) for e in r['edits']})==2
            for p,e,f in zip(r['parents'],r['edits'],r['factors']):
                assert e[:3]==parents[p]['edits'][0][:3]
                assert abs(e[3]-parents[p]['edits'][0][3]*f)<1e-7
            if r['kind']=='ablation':assert 0 in r['factors']
            else:assert all(f>0 for f in r['factors'])
            if r['job'] in ['01-strength-screen','04-supplemental-screen']:screen[r['pair_id']].append(r)
            elif r['job']!='08-layout-repeats':full[r['pair_id']].append(r)
    assert all(sum(r['kind']=='control' for r in rs)==1 for rs in batches.values())
    assert len(screen)==264
    for p in plan:
        rs=screen[p['id']];expected=6 if int(p['id'].split('-')[1])<=192 else 5
        assert len(rs)==expected,(p['id'],len(rs))
    reviews=json.loads((RUN/'editorial_reviews.json').read_text())
    for v in reviews:
        assert v['pair_id'] in pairs
        for s in v['stages']:
            assert s['id'] in byid and byid[s['id']]['pair_id']==v['pair_id']
            assert byid[s['id']]['max_tokens']==160,'Selected replies must be full reruns'
            assert 0<=s['weirdness']<=10 and 0<=s['coherence']<=10
    repeats=[r for r in rows if r['job']=='08-layout-repeats' and r['kind']=='pair']
    repeat_checks=[]
    for r in repeats:
        source=byid[r['source_id']]
        repeat_checks.append({'source_id':source['id'],'repeat_id':r['id'],'pair_id':r['pair_id'],'factors':r['factors'],
                              'exact_text_match':source['text']==r['text'],
                              'first_120_characters_match':source['text'][:120]==r['text'][:120],
                              'original_batch':source['batch'],'repeat_batch':r['batch']})
    (RUN/'replication_checks.json').write_text(json.dumps(repeat_checks,indent=2)+'\n')
    summary={'status':'passed','finished':datetime.now(timezone.utc).isoformat(),'pairs':len(screen),
             'pair_trials':sum(r['kind']=='pair' for r in rows),'parent_baselines':sum(r['kind']=='retest' for r in rows),
             'single_parent_checks':sum(r['kind']=='ablation' for r in rows),'batch_controls':len(batches),
             'total_replies':len(rows),'full_sweep_pairs':len(full),'selected_transitions':len(reviews),
             'selected_replies':sum(len(v['stages']) for v in reviews),'layout_repeats':len(repeats),
             'repeat_exact_matches':sum(r['exact_text_match'] for r in repeat_checks),
             'repeat_opening_matches':sum(r['first_120_characters_match'] for r in repeat_checks),
             'record_ids_unique':True,'raw_coefficients_and_parent_links_verified':True,
             'sha256_attempts':hashlib.sha256((RUN/'attempts.jsonl').read_bytes()).hexdigest()}
    (RUN/'completion.json').write_text(json.dumps(summary,indent=2)+'\n')
    manifest=json.loads((RUN/'manifest.json').read_text());manifest['study']=json.loads((RUN/'protocol.json').read_text())
    manifest.update(actual_study=summary,completed_jobs=[p.stem for p in (RUN/'completed').glob('*.request.json')])
    (RUN/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    from experiments.build_pair_strength_report import main as build
    build();print(json.dumps(summary))

if __name__=='__main__':main()

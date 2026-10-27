"""Check saved run integrity, selection decisions, and paired interventions."""
from pathlib import Path
import argparse,json,itertools,collections,hashlib
p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);p.add_argument('--complete',action='store_true');a=p.parse_args();run=a.run
read=lambda n,d:json.loads((run/n).read_text()) if (run/n).exists() else d
m=read('manifest.json',{});planned={(r['layer'],r['neuron']) for r in m['selected_neurons']}
rows=[json.loads(s) for s in (run/'judged_attempts.jsonl').read_text().splitlines()] if (run/'judged_attempts.jsonl').exists() else []
singles=read('selected.json',[]);pairs=read('pairs.json',[])
assert len(planned)==m['sample_units']
assert m.get('planned_sample_units',m['sample_units'])==1000
pilot=read('../neuron-site-sample-20261027/manifest.json',{})
assert not planned&{(r['layer'],r['neuron']) for r in pilot['selected_neurons']}
assert len({r['id'] for r in rows})==len(rows)
assert all(r['id']==r['judge']['id'] for r in rows)
by_id={r['id']:r for r in rows}
by_batch=collections.defaultdict(list)
for r in rows:
    by_batch[r['batch']].append(r)
    assert r['judge']['category'] in ['Persona','Off-topic','Changed assistant','Normal Talkie','Incoherent']
    assert all(isinstance(r['judge'][key],int) and 0<=r['judge'][key]<=10 for key in ['coherence','weirdness'])
for batch,rs in by_batch.items():
    assert sum(r['kind']=='control' for r in rs)==1
    assert len({r.get('prompt','Who are you?') for r in rs})==1
for r in singles:
    assert r['id'] in by_id and r['kind']=='single' and (r['layer'],r['neuron']) in planned and r['sign'] in [-1,1]
    assert r['key']==f"{r['layer']}:{r['neuron']}:{r['sign']}"
    alpha=r['edits'][0][3]
    assert r['judge']['coherence']>=5 or alpha==m['doses'][-1]
    prior=[s for s in rows if s['kind']=='single' and s['key']==r['key'] and s['edits'][0][3]>alpha]
    assert all(s['judge']['coherence']<5 for s in prior)
    assert len(prior)==m['doses'].index(alpha)
assert len({r['key'] for r in singles})==len(singles)
parents={r['id']:r for r in singles}
for r in pairs:
    assert len(r['parents'])==2 and set(r['parents'])<=set(parents)
    expected=[[l,u,s,alpha*r['factor']] for pid in r['parents'] for l,u,s,alpha in parents[pid]['edits']]
    assert r['edits']==expected
    assert r['judge']['coherence']>=5 or r['factor']==0.5
if a.complete:
    assert len(singles)==m.get('tested_directions',2000) and len({r['key'] for r in singles})==m.get('tested_directions',2000)
    raw=[json.loads(s) for s in (run/'attempts.jsonl').read_text().splitlines()]
    assert {r['id'] for r in raw}==set(by_id)
    stable=[r['source_id'] for r in read('identity_retest_labels.json',[]) if r['same_identity']]
    expected={frozenset(t) for t in itertools.combinations(stable,2) if (parents[t[0]]['layer'],parents[t[0]]['neuron'])!=(parents[t[1]]['layer'],parents[t[1]]['neuron'])}
    assert {frozenset(r['parents']) for r in pairs}==expected
    assert len(pairs)==len(expected)
    assert read('status.json',{})['phase']=='complete'
result={'complete':a.complete,'sample_units':len(planned),'selected_directions':len(singles),'attempts':len(rows),'controls':len(by_batch),'pairs':len(pairs),'checks':['Fresh units exclude the entire pilot','Unique reply IDs and consistent judgment schema','One unsteered control and one prompt per batch','Signed solo identities and strongest qualifying dose selection','Pair edits equal parent doses times the recorded factor']}
if a.complete:result['checks']+=['All saved signed conditions completed','No unjudged raw attempts','Every eligible stable candidate combination present']
(run/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

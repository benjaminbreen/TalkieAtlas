"""Audit saved neuron expansion records and write factual completion metadata."""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'runs/neuron-expansion-20261027'
def put(name,obj):
    (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def main():
    assert (P/'DONE.json').exists(), 'Generation must finish before publication'
    rows=[json.loads(x) for x in (P/'attempts.jsonl').read_text().splitlines()]
    by={r['id']:r for r in rows};assert len(by)==len(rows)
    manifest=json.loads((P/'manifest.json').read_text())
    planned={(r['layer'],r['neuron']) for r in manifest['selected_neurons']}
    old=set(tuple(x) for x in json.loads((P/'excluded_units.json').read_text()))
    assert not planned&old
    scan=[r for r in rows if r['kind']=='single']
    sig={tuple(r['edits'][0]) for r in scan}
    assert len(sig)==len(scan), 'Duplicate screen conditions'
    actual={(e[0],e[1]) for e in sig}
    assert actual<=planned
    expected={(l,u,s,d) for l,u in planned for s in [-1,1] for d in [.75,1.25]}
    assert sig<=expected
    parents={r['id']:r for r in json.loads((P/'parents.json').read_text())}
    for r in rows:
        if r['kind'] in ['pair','ablation']:
            assert len(r['parents'])==len(r['factors'])==len(r['edits'])==2
            for i,e,f in zip(r['parents'],r['edits'],r['factors']):
                p=parents[i]['edits'][0]
                assert e[:3]==p[:3] and abs(e[3]-p[3]*f)<1e-7
    checks=[]
    for r in rows:
        if r.get('replication'):
            source=by[r['source_id']]
            assert source['edits']==r['edits'] and source['max_tokens']==r['max_tokens']
            checks.append(dict(source_id=source['id'],rerun_id=r['id'],exact_text_match=source['text']==r['text'],first_120_characters_match=source['text'][:120]==r['text'][:120],source_batch=source['batch'],rerun_batch=r['batch']))
    put('replication_checks.json',checks)
    reviews=json.loads((P/'editorial_reviews.json').read_text());solos=json.loads((P/'solo_reviews.json').read_text())
    for v in reviews:
        for s in v['stages']:
            r=by[s['id']];assert r['pair_id']==v['pair_id'] and r['max_tokens']==160
            assert r['termination'] not in ['time_limit','repeating']
            assert 1<=s['weirdness']<=10 and 1<=s['coherence']<=10
    for s in solos:
        r=by[s['id']];assert r['max_tokens']==160 and r['termination'] not in ['time_limit','repeating']
    counts=Counter(r['kind'] for r in rows)
    summary=dict(finished=datetime.now(timezone.utc).isoformat(),fresh_neurons=len(actual),signed_directions=len({e[:3] for e in sig}),solo_screen_conditions=len(scan),planned_screen_complete=sig==expected,missing_screen_conditions=len(expected-sig),pairs=len({r['pair_id'] for r in rows if r['kind']=='pair'}),pair_trials=counts['pair'],full_pair_trials=sum(r['kind']=='pair' and r['max_tokens']==160 and not r.get('replication') for r in rows),full_solo_retests=counts['retest'],single_parent_checks=counts['ablation'],layout_repeats=len(checks),exact_layout_matches=sum(r['exact_text_match'] for r in checks),opening_layout_matches=sum(r['first_120_characters_match'] for r in checks),selected_solos=sum(r.get('featured',False) for r in solos),selected_pairs=sum(r.get('selected',True) for r in reviews),selected_pair_replies=sum(len(r['stages']) for r in reviews if r.get('selected',True)),all_replies=len(rows),controls=counts['control'],termination_counts=dict(Counter(r['termination'] for r in rows)))
    put('completion.json',summary)
    manifest.update(tested_directions=summary['signed_directions'],sample_units=summary['fresh_neurons'],solo_screen_conditions=len(scan),attempts=len(rows),completion=summary)
    put('manifest.json',manifest)
    protocol=json.loads((P/'protocol.json').read_text());protocol['completed']=summary;protocol['full_pair_grid']='Six equal factors: .375, .5, .5625, .625, .6875, .75; four unequal balances: .375/.625, .625/.375, .5/.75, .75/.5; two zero-parent checks at the .625 reference factor. Additional followups, if any, record their exact grid in every row.';put('protocol.json',protocol)
    put('audit.json',{'unique_ids':True,'fresh_units_disjoint_from_prior':True,'screen_conditions_unique':True,'parent_coefficients_verified':True,'selected_outputs_full_continuations':True,'ratings_in_range':True,'counts':summary})
    print(json.dumps(summary))
if __name__=='__main__':main()

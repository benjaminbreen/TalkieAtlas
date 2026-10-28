"""Merge the preserved uniform pilot with the adaptive discovery pass.

Safe during generation: only completed selected rows and judged attempts enter
this export. Original run files are never changed. IDs/batches are disjoint.
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'sites/talkie-neuron-sample/dist')
p.add_argument('--pilot',type=Path,default=ROOT/'runs/neuron-site-sample-20261027')
p.add_argument('--ranking-run',type=Path,default=ROOT/'runs/neuron-ranking-review-20261027')
p.add_argument('--playground',type=Path,default=ROOT/'runs/neuron-pair-playground-20261027')
p.add_argument('--curation',type=Path,default=Path(__file__).with_name('pair_curation.json'))
p.add_argument('--discovery',type=Path,default=ROOT/'runs/neuron-site-discovery-20261027')
p.add_argument('--sprint',type=Path,default=ROOT/'runs/neuron-novelty-wide-20261027')
a=p.parse_args()

def read(root,name,default):
    f=root/name
    return json.loads(f.read_text()) if f.exists() else default

def run(root,tag):
    records=[json.loads(s) for s in (root/'judged_attempts.jsonl').read_text().splitlines() if s] if (root/'judged_attempts.jsonl').exists() else []
    for r in records:r['run']=tag
    by_id={r['id']:r for r in records}
    def rows(name):
        out=read(root,name,[])
        for r in out:r['run']=tag
        return out
    return {'manifest':read(root,'manifest.json',{}),'singles':rows('selected.json'),'pairs':rows('pairs.json'),
            'attempts':records,'controls':[r for r in records if r['kind']=='control'],
            'retests':read(root,'retests.json',{}),'identity_retests':read(root,'identity_retest_labels.json',[]),
            'cross_prompt_retests':read(root,'cross_prompt_retests.json',{}),
            'status':read(root,'status.json',{}),'tag':tag}

runs=[run(a.pilot,'pilot'),run(a.discovery,'discovery')]
manifest={**runs[0]['manifest'],'sample_units':sum(r['manifest'].get('sample_units',0) for r in runs),
          'sampling':'400-neuron uniform pilot (both signs), followed by '+str(runs[1]['manifest'].get('sample_units',0))+' fresh neurons in a time-limited adaptive pass. Discovery tested '+str(runs[1]['manifest'].get('tested_directions',0))+' shuffled signed directions from its fixed 1,000-unit plan; some units have one sign. Adaptive yields are not population estimates.',
          'tested_directions':800+runs[1]['manifest'].get('tested_directions',0),
          'seeds':[r['manifest'].get('seed') for r in runs],
          'selected_neurons':[u for r in runs for u in r['manifest'].get('selected_neurons',[])],
          'runs':[{ 'id':r['tag'],**r['manifest']} for r in runs]}
manifest['differences']=['Uniform pilot followed by a time-limited adaptive discovery pass; some discovery units have one sign tested','The discovery dose and pair schedules were shortened to meet the requested wrap-up time']+[x for x in manifest.get('differences',[]) if '400-neuron' not in x]
data={'manifest':manifest,
      **{key:[row for r in runs for row in r[key]] for key in ['singles','pairs','controls','attempts','identity_retests']},
      'retests':{key:sum((r['retests'].get(key) or 0) for r in runs) for key in ['candidates','exact_matches','identity_matches','paired_candidates']},
      'cross_prompt_retests':runs[1]['cross_prompt_retests'],
      'rounds':[{k:r[k] for k in ['tag','status','retests']} for r in runs],
      'status':{**runs[1]['status'],'sample_units':manifest['sample_units']}}
data['retests']['rows']=[row for r in runs for row in r['retests'].get('rows',[])]
play=read(a.playground,'release.json',{})
if play:
    data['pairs'].extend(play['pairs'])
    data['attempts'].extend(play['attempts'])
    data['controls'].extend([r for r in play['attempts'] if r['kind']=='control'])
    manifest['pair_playground']=play['manifest']
    data['playground']=play['summary']
    data['retests']['candidates']+=play['summary']['solo_retests']
    data['retests']['exact_matches']+=play['summary']['exact_retest_matches']
    data['retests']['paired_candidates']+=8
    data['retests']['rows'].extend([r for r in play['attempts'] if r['kind']=='retest'])
comparisons=read(a.discovery,'pair_comparison_labels.json',[])+play.get('pair_comparisons',[])

if comparisons:
    by_pair={r['id']:r for r in comparisons}
    assert set(by_pair)=={r['id'] for r in data['pairs']}, 'Missing pair comparison'
    for row in data['pairs']:row['mix']=by_pair[row['id']]
data['pair_comparisons']=comparisons
curation=json.loads(a.curation.read_text()) if a.curation.exists() else None
if curation:
    choices={r['id']:(i,r) for i,r in enumerate(curation['featured'])}
    assert set(choices)<={r['id'] for r in data['pairs']}
    for row in data['pairs']:
        row['featured']=row['id'] in choices
        if row['featured']:
            row['featured_order'],info=choices[row['id']]
            row['featured_reason']=info['reason']
data['pair_curation']=curation
solo_rankings=read(a.ranking_run,'rankings.json',{})
if solo_rankings:
    ratings=solo_rankings['ratings']
    assert set(ratings)=={r['id'] for r in data['singles']}, 'Incomplete solo ranking coverage'
    for row in data['singles']+data['attempts']:
        if row['id'] in ratings:row['ranking']=ratings[row['id']]
    data['solo_rankings']={k:v for k,v in solo_rankings.items() if k!='ratings'}
    manifest['browsing_ratings']=data['solo_rankings']

data['status'].update({'directions':len(data['singles']),'pairs':len(data['pairs']),'attempts':len(data['attempts'])})
assert len({r['id'] for r in data['attempts']})==len(data['attempts'])
assert all(set(r['parents'])<={s['id'] for s in data['singles']} for r in data['pairs'])


assert len({r['id'] for r in data['attempts']})==len(data['attempts']), 'Duplicate attempt ID'
assert len({r['key'] for r in data['singles']})==len(data['singles']), 'Duplicate signed condition'
assert all(r['judge']['id']==r['id'] for r in data['attempts'])
known={r['id'] for r in data['singles']}
assert all(set(r['parents'])<=known for r in data['pairs'])
from merge_sprint import extend_sprint
data=extend_sprint(data,a.sprint)
from merge_strength import extend_strength
data=extend_strength(data,ROOT/'runs/pair-strength-search-20261027')
from merge_expansion import extend_expansion
data=extend_expansion(data,ROOT/'runs/neuron-expansion-20261027')
a.output.mkdir(parents=True,exist_ok=True)
for name,obj in [('data.json',data),('sprint-ratings.json',data['sprint_ratings']),('manifest.json',manifest),('identity-retests.json',data['identity_retests']),('cross-prompt-retests.json',data['cross_prompt_retests']),('pair-comparisons.json',comparisons),('pair-curation.json',curation),('solo-rankings.json',solo_rankings)]:
    f=a.output/name;tmp=f.with_suffix('.json.tmp');tmp.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n');tmp.replace(f)
print(json.dumps({'singles':len(data['singles']),'pairs':len(data['pairs']),'attempts':len(data['attempts']),'phase':data['status'].get('phase')}))

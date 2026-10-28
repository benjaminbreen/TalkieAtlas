"""Import the completed pair-strength study without changing earlier records."""
import copy,json
from collections import defaultdict
from pathlib import Path

def extend_strength(data,root):
    root=Path(root)
    if not (root/'DONE.json').exists():return data
    raw=[json.loads(l) for l in (root/'attempts.jsonl').read_text().splitlines()]
    reviews=json.loads((root/'editorial_reviews.json').read_text())
    labels={s['id']:(v,s,i) for v in reviews if v.get('selected',True) for i,s in enumerate(v['stages'])}
    parents={r['id']:r for r in json.loads((root/'parents.json').read_text())}
    oldlookup={r['id']:r for r in data['attempts']+data['singles']+data['pairs']}
    listed={r['id'] for r in data['singles']}
    def judge(i,name,reason,selected=False):
        return {'id':i,'name':name,'description':reason,'category':'Persona' if selected else 'Unrated','tags':['strength study'],
                'weirdness':None,'coherence':None,'rated':False,'reviewer':None}
    def direction(r):return f"{r['layer']}-{r['neuron']}-{'up' if r['sign']>0 else 'down'}"
    used={r['path'] for r in data['singles']+data['pairs']}
    for i,p in parents.items():
        if i in listed:continue
        r=copy.deepcopy(oldlookup[i]);r.update(kind='single',unlisted=False,judge=judge(i,p['name'],'Saved discovery preview used as a parent; fresh full solo baseline is shown in the strength comparison.'))
        base=direction(r);path='n/'+base+'/'
        r.update(base_slug=base,slug=base if path not in used else base+'--'+i,canonical=path not in used)
        r['path']='n/'+r['slug']+'/';used.add(r['path']);data['singles'].append(r);listed.add(i)
    new=[]
    for source in raw:
        r=copy.deepcopy(source);i=r['id'];r['run']='pair-strength-study';r['strength_featured']=i in labels;r['featured']=i in labels
        reason='Saved strength trial; not numerically rated.';name=' '.join(r['text'].split())[:85] or 'Empty reply'
        if r['kind']=='retest':name=parents[r['source_id']]['name']
        if i in labels:
            review,stage,index=labels[i];name=stage['label'];reason=review['reason'];r['featured_order']=review['order']*10+index
            r['editorial']={'reason':reason};r['editorial_rating']={**stage,'reviewer':'Codex','version':1}
            r['featured_reason']=reason;r['robot_icon']='icons/strength-'+i+'.svg'
        r['judge']=judge(i,name,reason,i in labels)
        if i in labels:r['judge'].update(weirdness=stage['weirdness'],coherence=stage['coherence'],rated=True,reviewer='Codex')
        r['review_status']='Editorially selected' if i in labels else 'Not numerically rated'
        if r['kind'] in ['pair','ablation']:
            r['strength_comparison']='strength-study/#'+r['pair_id']
            r['mix']={'outcome':'Selected strength discovery' if i in labels else 'Not reviewed','novelty':None,'blending':None,'reason':reason}
        new.append(r)
    groups=defaultdict(list)
    for r in new:
        if r['kind']=='pair':groups['_'.join(direction(parents[i]) for i in r['parents'])].append(r)
    for base,rs in groups.items():
        rs.sort(key=lambda r:(not r['strength_featured'],r.get('featured_order',99999),r['id']))
        for r in rs:
            canonical='p/'+base+'/' not in used
            r.update(base_slug=base,slug=base if canonical else base+'--'+r['id'],canonical=canonical)
            r['path']='p/'+r['slug']+'/';assert r['path'] not in used;used.add(r['path'])
    data['pairs'].extend(r for r in new if r['kind']=='pair')
    data['controls'].extend(r for r in new if r['kind']=='control')
    data['attempts'].extend(new)
    summary=json.loads((root/'completion.json').read_text()) if (root/'completion.json').exists() else {'pairs':len(groups),'pair_trials':sum(r['kind']=='pair' for r in new)}
    data['strength_study']={**summary,'url':'strength-study/','selected_replies':len(labels),'selected_pairs':len(reviews),'protocol':json.loads((root/'protocol.json').read_text())}
    data['strength_reviews']=reviews
    data['manifest']['strength_study']=data['strength_study']
    data['status'].update(pairs=len(data['pairs']),directions=len(data['singles']),attempts=len(data['attempts']))
    assert len({r['id'] for r in data['attempts']})==len(data['attempts'])
    assert all(set(r['parents'])<=listed for r in data['pairs'])
    assert len({r['path'] for r in data['singles']+data['pairs']})==len(data['singles'])+len(data['pairs'])
    return data

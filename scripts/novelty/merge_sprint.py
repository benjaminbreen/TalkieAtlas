"""Import selected sprint solos, their exact parents, every pair trial and raw evidence.

The selected 42 have separate Codex scores; other trials stay unscored. Trial URLs remain distinct, with
the selected specimen retaining the short canonical neuron/pair URL.
"""
import copy,json,re
from collections import Counter,defaultdict
from pathlib import Path

def extend_sprint(data, root):
    root=Path(root)
    if not (root/'editorial_reviews.json').exists():return data
    reviews={r['id']:r for r in json.loads((root/'editorial_reviews.json').read_text())}
    ratings_path=Path(__file__).with_name('sprint_ratings.json')
    ratings=json.loads(ratings_path.read_text()) if ratings_path.exists() else {'ratings':{}}
    featured={i for i,r in reviews.items() if r.get('featured')}
    notes={r['id']:r for r in json.loads((root/'candidate_notes.json').read_text())}
    raw=[]
    for run in [root.with_name('neuron-novelty-sprint-20261027'),root]:
        for line in (run/'attempts.jsonl').read_text().splitlines():
            r=json.loads(line);r['run']='novelty-sprint';raw.append(r)
    by_raw={r['id']:r for r in raw}
    pairs=[r for r in raw if r['kind']=='pair']
    parent_ids={i for r in pairs for i in r['parents']}
    displayed_solos=parent_ids|{i for i in featured if by_raw[i]['kind']!='pair'}
    raw_ids=set(by_raw)
    assert len(featured)==42 and len(pairs)==1668

    def enrich(r):
        r=copy.deepcopy(r);i=r['id'];review=reviews.get(i)
        r['source_kind']=r['kind']
        r['sprint_featured']=i in featured
        r['featured']=i in featured
        r['featured_order']=review.get('order',999) if review else 999
        r['unlisted']=r['kind']!='pair' and i not in displayed_solos and r['kind']!='control'
        if i in displayed_solos:r['kind']='single'
        name=(review or {}).get('name') or r.get('name') or notes.get(i,{}).get('name')
        if not name:
            words=' '.join(r['text'].split())
            name=(words[:85]+'…' if len(words)>85 else words) or 'Empty reply'
        reason=(review or {}).get('reason') or 'Saved exploratory trial. No numerical quality or identity ratings were assigned.'
        r['judge']={'id':i,'name':name,'category':'Persona' if i in featured else 'Normal Talkie' if r['kind']=='control' else 'Unrated',
                    'description':reason,'tags':['novelty search']+(['editorial pick'] if i in featured else []),
                    'weirdness':None,'coherence':None,'rated':False,'reviewer':'Codex editorial review' if review else None}
        r['review_status']='Editorially selected' if i in featured else 'Editorially reviewed' if review else 'Not reviewed'
        if i in ratings['ratings']:
            rating=ratings['ratings'][i]
            r['editorial_rating']={**rating,'reviewer':ratings['reviewer'],'version':ratings['version']}
            r['judge'].update(weirdness=rating['weirdness'],coherence=rating['coherence'],rated=True,reviewer=ratings['reviewer'])
        if review:r['editorial']=review
        if i in featured:r['featured_reason']=reason
        if r['kind']=='pair':
            r['mix']={'id':i,'outcome':'Selected new persona' if i in featured else 'Reviewed' if review else 'Not reviewed',
                      'novelty':None,'blending':None,'reason':reason}
        return r

    enriched=[enrich(r) for r in raw];by_new={r['id']:r for r in enriched}
    data['singles'].extend(by_new[i] for i in sorted(displayed_solos))
    data['pairs'].extend(r for r in enriched if r['kind']=='pair')
    data['controls'].extend(r for r in enriched if r['kind']=='control')
    data['attempts'].extend(enriched)
    lookup={r['id']:r for r in data['attempts']+data['singles']+data['pairs']}

    def direction(r):return f"{r['layer']}-{r['neuron']}-{'up' if r['sign']>0 else 'down'}"
    def base(r):return '_'.join(direction(lookup[i]) for i in r['parents']) if r['kind']=='pair' else direction(r)
    groups=defaultdict(list)
    for r in data['singles']+data['pairs']:
        r['base_slug']=base(r);groups[(r['kind'],r['base_slug'])].append(r)
    for (kind,b),group in groups.items():
        winner=min(group,key=lambda r:(not r.get('sprint_featured'),not(r['id'] not in raw_ids),not r.get('featured'),r.get('featured_order',999),
                                       r['termination']=='repeating',not bool(r.get('editorial')), -len(r['text'])))
        for r in group:
            r['canonical']=r is winner
            r['slug']=b if r is winner else b+'--'+r['id']
            r['path']=('p/' if kind=='pair' else 'n/')+r['slug']+'/'
    assert len({r['path'] for r in data['singles']+data['pairs']})==len(data['singles'])+len(data['pairs'])
    picks=sorted((r for r in enriched if r.get('sprint_featured')),key=lambda r:r['featured_order'])
    data['sprint_featured_ids']=[r['id'] for r in picks]
    old_selection=data.get('pair_curation') or {'featured':[]}
    old_selection['featured']=[{'id':r['id'],'reason':r['featured_reason']} for r in picks if r['kind']=='pair']+old_selection['featured']
    old_selection['selection']='Editorial selection for surprising, specific, readable personas. Literal blending is not required. All strength trials and failed reruns are retained.'
    data['pair_curation']=old_selection
    manifest=json.loads((root/'manifest.json').read_text())
    summary=json.loads((root/'completion.json').read_text())
    data['novelty_sprint']={**summary,'reviewer':'Codex editorial review','numeric_ratings':bool(ratings['ratings']),'rated_discoveries':len(ratings['ratings']),
                            'method':'32/48/96-token discovery previews, core 160-token reruns, and late 64/96-token pair trials. New personas selected for surprise, specificity and readability, with no literal-blending requirement. The 42 selected discoveries also have separate Codex weirdness/coherence ratings; other trials remain unscored.'}
    data['sprint_ratings']=ratings
    m=data['manifest'];m['novelty_sprint']=data['novelty_sprint']
    prior_units={(u['layer'],u['neuron']) for u in m['selected_neurons']}
    fresh={(r['layer'],r['neuron']) for r in raw if r['kind']=='single'}
    m['selected_neurons']=[{'layer':l,'neuron':u} for l,u in sorted(prior_units|fresh)]
    m['sample_units']=len(prior_units|fresh)
    m['tested_directions']=m.get('tested_directions',1440)+summary['fresh_directions']
    m['listed_directions']=len({r['key'] for r in data['singles']})
    m['sampling']+=' Novelty sprint: '+str(summary['fresh_directions'])+' additional signed directions, with prespecified stronger-dose late-layer enrichments. The library lists selected solos and exact pair parents; all sprint previews remain in the full download and sprint report.'
    m['runs'].append({'id':'novelty-sprint',**manifest})
    m['seeds']=list(dict.fromkeys(m['seeds']+[202610272037,202610272040,202610272042,202610272052]))
    data['retests']['rows'].extend(r for r in enriched if r.get('source_kind')=='retest')
    data['retests']['candidates']+=summary['retests']
    data['status'].update(phase='complete',sample_units=m['sample_units'],directions=len(data['singles']),pairs=len(data['pairs']),attempts=len(data['attempts']))
    assert len({r['id'] for r in data['attempts']})==len(data['attempts'])
    assert all(set(r['parents'])<={s['id'] for s in data['singles']} for r in data['pairs'])
    assert all(lookup[i]['canonical'] for i in featured),'Featured result lost its canonical URL'
    return data

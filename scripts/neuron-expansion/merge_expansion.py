"""Import the completed fresh-neuron study while preserving earlier releases."""
import copy
import json
from collections import defaultdict
from pathlib import Path


def extend_expansion(data, root):
    root = Path(root)
    if not (root / 'DONE.json').exists():
        return data
    raw = [json.loads(line) for line in (root / 'attempts.jsonl').read_text().splitlines()]
    reviews = json.loads((root / 'editorial_reviews.json').read_text())
    solos = {r['id']: r for r in json.loads((root / 'solo_reviews.json').read_text())}
    labels = {s['id']: (v, s, i) for v in reviews if v.get('selected', True) for i, s in enumerate(v['stages'])}
    parents = {r['id']: r for r in json.loads((root / 'parents.json').read_text())}
    used = {r['path'] for r in data['singles'] + data['pairs']}
    listed = {r['id'] for r in data['singles']}

    def direction(r):
        return f"{r['layer']}-{r['neuron']}-{'up' if r['sign'] > 0 else 'down'}"

    def assign(r, base, prefix):
        canonical = prefix + base + '/' not in used
        r.update(base_slug=base, slug=base if canonical else base + '--' + r['id'], canonical=canonical)
        r['path'] = prefix + r['slug'] + '/'
        assert r['path'] not in used
        used.add(r['path'])

    new = []
    for source in raw:
        r = copy.deepcopy(source)
        i = r['id']
        solo = solos.get(i)
        featured = i in labels or bool(solo and solo.get('featured'))
        r.update(run='neuron-expansion', expansion_featured=featured, featured=featured, unlisted=not featured)
        name = parents.get(i, {}).get('name') or ' '.join(r['text'].split())[:85] or 'Empty reply'
        reason = 'Saved exploratory trial; not numerically rated.'
        rating = None
        if solo:
            name, reason, rating = solo['name'], solo['reason'], solo
            r['featured_order'] = 1000 + solo.get('order', 0)
        if i in labels:
            review, stage, index = labels[i]
            name, reason, rating = stage['label'], review['reason'], stage
            r['featured_order'] = review['order'] * 10 + index
        r['judge'] = dict(id=i, name=name, description=reason, category='Persona' if featured else 'Unrated',
                          tags=['persona'], weirdness=None, coherence=None, rated=False, reviewer=None)
        if rating:
            r['judge'].update(weirdness=rating['weirdness'], coherence=rating['coherence'], rated=True, reviewer='Codex')
            r['editorial_rating'] = dict(id=i, weirdness=rating['weirdness'], coherence=rating['coherence'], reviewer='Codex', version=1)
        if featured:
            r.update(robot_icon='icons/expansion-' + i + '.svg', featured_reason=reason, editorial={'reason': reason})
        r['review_status'] = 'Rated by Codex' if featured else 'Not numerically rated'
        if r['kind'] in ['pair', 'ablation']:
            r['mix'] = dict(outcome='Persona' if featured else 'Not reviewed', novelty=None, blending=None, reason=reason)
        # Show exact full-length parent baselines and selected solos; keep every other scan in the download.
        if i in parents or solo and solo.get('featured'):
            r.update(source_kind=r['kind'], kind='single', unlisted=not featured)
            assign(r, direction(r), 'n/')
            data['singles'].append(r)
            listed.add(i)
        new.append(r)
    groups = defaultdict(list)
    for r in new:
        if r['kind'] == 'pair' and r['expansion_featured']:
            groups['_'.join(direction(parents[i]) for i in r['parents'])].append(r)
    for base, rows in groups.items():
        rows.sort(key=lambda r: (not r['expansion_featured'], r.get('featured_order', 99999), r['id']))
        for r in rows:
            assign(r, base, 'p/')
    data['pairs'].extend(r for r in new if r['kind'] == 'pair' and r['expansion_featured'])
    data['controls'].extend(r for r in new if r['kind'] == 'control')
    data['attempts'].extend(new)
    summary = json.loads((root / 'completion.json').read_text())
    data['expansion_study'] = dict(summary, selected_replies=len(labels), selected_pairs=len(reviews),
                                    protocol=json.loads((root / 'protocol.json').read_text()))
    data['manifest']['expansion_study'] = data['expansion_study']
    data['manifest']['sample_units'] += summary['fresh_neurons']
    data['manifest']['tested_directions'] += summary['signed_directions']
    data['manifest']['sampling'] += (' Fresh-neuron expansion: ' + str(summary['fresh_neurons']) +
        ' additional physical neurons, with late-layer enrichment; both signs at two fixed doses. '
        'Only full-length selected voices and exact pair parents are listed; every preview remains in the full data.')
    data['status'].update(pairs=len(data['pairs']), directions=len(data['singles']), attempts=len(data['attempts']))
    assert len({r['id'] for r in data['attempts']}) == len(data['attempts'])
    assert all(set(r['parents']) <= listed for r in data['pairs'])
    assert len(used) == len(data['singles']) + len(data['pairs'])
    return data

"""Add the user-requested drug x persona blends to the library as two-neuron entries.

Every flagged blend in runs/drug-persona-cross-20261028/review/library_admissions.json is listed, with its
blinded v3 weirdness and coherence; the 50 iconed blends plus hand-picked De Quincey are Highlights. Parents are the exact solo conditions from the same run: each persona
neuron's greedy "Who are you?" reply at its neuronpersonas.com strength, and each state neuron's greedy
"Who are you?" reply at full strength. Persona parents are labelled from our own reply (review/parent_labels.json). Parents and same-batch controls are unlisted.
"""
import copy
import json
from pathlib import Path


def extend_drug_cross(data, root):
    root = Path(root)
    adm_path = root / 'review/library_admissions.json'
    if not adm_path.exists():
        return data
    adm = json.loads(adm_path.read_text())
    labels = json.loads((root / 'review/parent_labels.json').read_text())['labels']
    icons = json.loads((Path(__file__).with_name('dist') / 'icons/drug-cross-index.json').read_text())
    cross = {(r['id'], r['prompt']): r for r in map(json.loads, (root / 'cross.jsonl').read_text().splitlines())}
    states = {(r['id'], r['prompt']): r for r in map(json.loads, (root / 'states.jsonl').read_text().splitlines())}
    used = {r['path'] for r in data['singles'] + data['pairs']}
    names = {r['judge']['name'].casefold() for r in data['singles'] + data['pairs']}
    ids = {r['id'] for r in data['attempts']}
    batch0 = max(r.get('batch', 0) for r in data['attempts']) + 1
    batches = {'Who are you?': batch0, 'How do you feel just now?': batch0 + 1}
    sd = lambda s: 'up' if s > 0 else 'down'

    def assign(r, base, prefix):
        canonical = prefix + base + '/' not in used
        r.update(base_slug=base, slug=base if canonical else base + '--' + r['id'], canonical=canonical)
        r['path'] = prefix + r['slug'] + '/'
        assert r['path'] not in used
        used.add(r['path'])

    def common(r, rid, prompt, name):
        r.pop('id', None)
        r.update(id=rid, batch=batches[prompt], job='drug-persona-cross', run='drug-persona-cross', max_tokens=160)
        r['judge'] = dict(id=rid, name=name, description='', category='Unrated', tags=[], weirdness=None,
                          coherence=None, rated=False, reviewer=None)
        assert rid not in ids
        ids.add(rid)
        return r

    new = []
    for prompt, b in batches.items():
        c = copy.deepcopy(states['control', prompt])
        common(c, f'dpc-control-{b}', prompt, 'Unsteered control')
        c['kind'] = 'control'
        new.append(c)

    parents = {}

    def parent(kind, l, u, s, source, label, site_name=None):
        k = f'{l}:{u}:{s}'
        if k in parents:
            return parents[k]['id']
        r = copy.deepcopy(source)
        common(r, f'dpc-{kind}-{l}-{u}-{sd(s)}', 'Who are you?', label)
        r.update(source_id=source['id'], kind='single', layer=l, neuron=u, sign=s, key=k, unlisted=True, featured=False)
        if site_name:
            r['site_name'] = site_name
        assign(r, f'{l}-{u}-{sd(s)}', 'n/')
        parents[k] = r
        new.append(r)
        data['singles'].append(r)
        return r['id']

    for i, e in enumerate(adm['entries']):
        src = cross[e['record'], e['prompt']]
        pe = e['persona']
        ps = 1 if pe['s'] == '+' else -1
        persona_src = cross[f"L{pe['L']}/{pe['n']}{pe['s']}", 'Who are you?']
        pid = parent('persona', pe['L'], pe['n'], ps, persona_src, labels[f"{pe['L']}/{pe['n']}{pe['s']}"], pe['name'])
        sl, su, ss = src['edits'][1][:3]
        sid = parent('state', sl, su, ss, states[e['state'], 'Who are you?'], e['state_label'])
        r = copy.deepcopy(src)
        rid = f'dpc-{i + 1:03d}'
        common(r, rid, e['prompt'], e['name'])
        assert e['name'].casefold() not in names, e['name']
        r.update(kind='pair', source_id=e['record'], parents=[pid, sid], factors=[1.0, e['scale']],
                 key=f"{pe['L']}:{pe['n']}:{ps}+{sl}:{su}:{ss}", featured=e['highlight'], unlisted=False,
                 featured_order=e['order'], featured_reason=e['description'])
        r['judge'].update(category='Persona', description=e['description'], tags=e['tags'],
                          weirdness=e['weirdness'], coherence=e['coherence'], rated=True, reviewer='Claude')
        r['editorial_rating'] = dict(weirdness=e['weirdness'], coherence=e['coherence'], version=3, reviewer='Claude')
        r['rating_provenance'] = dict(rubric='weirdness-v3', blind_id=e['blind'], reason=e['reason'], subjective=True,
                                      ratings='runs/drug-persona-cross-20261028/review/ratings.json')
        r['mix'] = dict(outcome='Persona', novelty=None, blending=None, reason=e['description'])
        if e['icon']:
            r['robot_icon'] = icons[e['key']]
        assign(r, f"{pe['L']}-{pe['n']}-{sd(ps)}_{sl}-{su}-{sd(ss)}", 'p/')
        data['pairs'].append(r)
        new.append(r)
    data['attempts'].extend(new)
    data['controls'].extend(r for r in new if r['kind'] == 'control')
    data['manifest']['sampling'] += (f" Drug x persona cross: {len(adm['entries'])} blends of neuronpersonas.com "
                                     "person neurons with drug and altered-state neurons, rated blind with the v3 rubric.")
    data['status'].update(pairs=len(data['pairs']), directions=len(data['singles']), attempts=len(data['attempts']))
    assert len({r['id'] for r in data['attempts']}) == len(data['attempts'])
    assert all(set(r['parents']) <= {s['id'] for s in data['singles']} for r in data['pairs'] if r['run'] == 'drug-persona-cross')
    return data

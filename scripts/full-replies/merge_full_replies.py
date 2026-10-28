"""Add the user's approved raw-reply personas to the ordinary library."""
import copy
import json
from pathlib import Path


def extend_full_replies(data, root):
    root = Path(root)
    if not (root / 'DONE.json').exists() or not (root / 'library_admissions.json').exists():
        return data
    admissions = json.loads((root / 'library_admissions.json').read_text())
    selected = {r['id']: r for r in admissions['selected']}
    duplicates = {r['id']: r for r in admissions['duplicates']}
    used = {r['path'] for r in data['singles'] + data['pairs']}
    raw = [json.loads(line) for line in (root / 'attempts.jsonl').read_text().splitlines()]
    raw_by = {r['id']: r for r in raw}
    for source in raw:
        r = copy.deepcopy(source)
        i = r['id']
        choice = selected.get(i)
        r.update(run='full-reply-review', unlisted=not bool(choice), featured=bool(choice))
        r['judge'] = dict(id=i, name='Saved reply', description='', category='Unrated', tags=[],
                          weirdness=None, coherence=None, rated=False)
        if choice:
            l, u, sign, dose = r['edits'][0]
            base = f"{l}-{u}-{'up' if sign > 0 else 'down'}"
            canonical = 'n/' + base + '/' not in used
            slug = base if canonical else base + '--' + i
            r.update(source_kind=r['kind'], kind='single', base_slug=base, slug=slug,
                     canonical=canonical, path='n/' + slug + '/', display_text=choice['display_text'],
                     robot_icon='icons/persona-' + i + '.svg')
            assert r['path'] not in used
            used.add(r['path'])
            r['judge'].update(name=choice['name'], category='Persona', weirdness=choice['weirdness'],
                              coherence=choice['coherence'], rated=True)
            # Keep rating provenance in research metadata, with the ordinary score UI.
            r['editorial_rating'] = dict(weirdness=choice['weirdness'], coherence=choice['coherence'], version=1)
            data['singles'].append(r)
        elif i in duplicates:
            r['duplicate_of'] = duplicates[i]['existing_id']
            if i == 's09000-r014':
                r['display_text'] = 'Footground cover ground cover footer footer ground cover [repeats]'
        data['attempts'].append(r)
        if r['kind'] == 'control':
            data['controls'].append(r)
    assert len(selected) == 19 and len(duplicates) == 7
    assert set(selected) | set(duplicates) == {r['id'] for r in raw if r['kind'] == 'retest'}
    assert all(raw_by[i]['text'].startswith(s['display_text'].removesuffix(' [repeats]')) for i, s in selected.items())
    data['status'].update(directions=len(data['singles']), attempts=len(data['attempts']))
    assert len({r['id'] for r in data['attempts']}) == len(data['attempts'])
    return data

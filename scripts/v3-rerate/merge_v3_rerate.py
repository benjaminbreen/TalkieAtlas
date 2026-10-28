"""Promote the user-chosen v3 re-rated singles (weirdness >= 7) into one-neuron Highlights.

Display scores come from the `ranking` object, so the v3 weirdness and coherence replace it there; the earlier
ranking is kept as `ranking_previous` and the original `judge` labels are untouched.
"""
import json
from pathlib import Path


def extend_v3_rerate(data, root):
    root = Path(root)
    adm_path = root / 'library_admissions.json'
    if not adm_path.exists():
        return data
    chosen = {}
    for s in json.loads(adm_path.read_text())['selected']:
        for i in s['records']:
            chosen[i] = s
    found = set()
    for r in data['singles'] + data['attempts']:
        s = chosen.get(r['id'])
        if not s:
            continue
        found.add(r['id'])
        if r.get('ranking') and 'ranking_previous' not in r:
            r['ranking_previous'] = r['ranking']
        prev = r.get('ranking_previous') or {}
        r['ranking'] = dict(weirdness=s['weirdness'], readability=s['coherence'], richness=prev.get('richness'),
                            version='weirdness-v3', reviewer='Claude', blind_id=s['blind'], reason=s['reason'],
                            ratings='runs/v3-rerate-singles-20261028/ratings.json', subjective=True)
        r['featured'] = True
    assert found == set(chosen), set(chosen) - found
    return data

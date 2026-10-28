"""Check the public index against the original saved generations."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'dist/sprint'


def validate():
    manifest = json.loads((OUT / 'index-data.json').read_text())
    rows = [r for name in manifest['files'] for r in json.loads((OUT / name).read_text())]
    summary = manifest['summary']
    assert len(rows) == summary['replies'] == len({r['id'] for r in rows})
    by_original = {(r['original_id'], r['text']) for r in rows}
    library = json.loads((HERE / 'dist/data.json').read_text())
    assert all((r['id'], r['text']) in by_original for r in library['attempts'])
    original_texts = {(src, r['text']) for r in rows for src in r['sources']}
    for source in summary['sources']:
        if source == 'library/data.json':
            continue
        saved = [json.loads(line) for line in (ROOT / source).read_text().splitlines() if line.strip()]
        if source.endswith('followups.jsonl'):
            texts = [r[field]['text'] for r in saved for field in ('where', 'when') if isinstance(r.get(field), dict)]
        else:
            texts = [r['text'] for r in saved if isinstance(r.get('text'), str)]
        assert all((source, text) in original_texts for text in texts), source
    assert len({tuple(e[:2]) for r in rows for e in r['edits']}) == summary['physical_neurons']
    assert len({tuple(e[:3]) for r in rows for e in r['edits']}) == summary['signed_directions']
    assert all(r['weirdness'] is None and r['coherence'] is None for r in rows if r['rating_source'] == 'Unscored')
    assert not any('/Users/' in str(r) or 'models/' in str(r) for r in rows)
    old_screen = 'runs/neuron-atlas-20261026T131010Z/screen.jsonl'
    assert all(r['stop'] is None for r in rows if old_screen in r['sources'])
    for r in rows:
        assert r['sources'] and isinstance(r['text'], str)
    html = (OUT / 'index.html').read_text()
    assert 'Unexpected new voices' not in html and 'id="more"' not in html
    assert manifest['version'] in html
    return dict(replies=len(rows), physical_neurons=summary['physical_neurons'],
                signed_directions=summary['signed_directions'], sources=len(summary['sources']) - 1,
                library_attempts_preserved=len(library['attempts']),
                full_raw_text='verified', private_machine_paths='none',
                unknown_stop_reasons='preserved')


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))

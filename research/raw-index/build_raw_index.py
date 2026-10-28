"""Build the complete, uncurated reply index at the existing /sprint/ URL.

No model calls, new ratings, or text truncation. Saved generations retain their
record identities even when text repeats. Re-exported copies are merged only
when the original record ID and complete text agree.
"""
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'dist' / 'sprint'


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def read_meta(folder):
    path = folder / 'manifest.json'
    return json.loads(path.read_text()) if path.exists() else {}


def normalized_text(text):
    return ' '.join(text.split()).casefold()


def build():
    data = json.loads((HERE / 'dist' / 'data.json').read_text())
    rows = {}
    by_original = {}
    sources = Counter()
    library = {r['id']: r for r in data['singles'] + data['pairs']}

    def add(raw, run, source, line, prompt=None, max_tokens=None):
        if not isinstance(raw.get('text'), str):
            return
        original = str(raw.get('id') or f'row-{line:06d}')
        # A source and export may both contain the same generation, but two
        # independent records with identical reply text must remain separate.
        key = (original, raw['text'])
        if (raw.get('id') and key in by_original
                and 'library/data.json' in rows[by_original[key]]['sources']):
            row = rows[by_original[key]]
            if source not in row['sources']:
                row['sources'].append(source)
            sources[source] += 1
            return
        rid = f'{run}:{original}'
        if rid in rows:
            raise ValueError(f'Conflicting saved record: {rid}')
        enriched = library.get(original, {})
        if enriched.get('text') != raw['text']:
            enriched = {}
        record = {**raw, **enriched}
        edits = record.get('edits', [])
        judge = record.get('judge') or {}
        ranking = record.get('ranking') or {}
        provenance = record.get('rating_provenance') or {}
        # Preserve versions; do not assign a related reply's score to this one.
        ratings = {k: record[k] for k in ('judge', 'ranking', 'rating_provenance',
                   'editorial_rating', 'original_judge') if record.get(k)}
        if provenance.get('version', 0) >= 3:
            w = provenance.get('weirdness')
            c = provenance.get('coherence', provenance.get('readability', judge.get('coherence')))
            rating_source = f"Saved v{provenance['version']} · {judge.get('reviewer', 'calibrated rubric')}"
        elif ranking:
            w, c = ranking.get('weirdness'), ranking.get('readability')
            rating_source = f"Saved v{ranking.get('version', 2)} · Luna"
        else:
            w, c = judge.get('weirdness'), judge.get('coherence')
            rating_source = 'Saved judgment' + (' · ' + judge['reviewer'] if judge.get('reviewer') else '')
        if w is None and c is None:
            rating_source = 'Unscored'
        name = judge.get('name') or record.get('name') or record.get('review', {}).get('name')
        if not name or name in ('Saved reply', 'Unrated', 'Solo reply'):
            name = f"L{edits[0][0]} · N{edits[0][1]}" if edits else 'Unsteered control'
        kind = 'control' if not edits else 'single' if len(edits) == 1 else 'pair' if len(edits) == 2 else 'multiple'
        saved_kind = record.get('source_kind', record.get('kind', kind))
        stage = ('Continuation' if record.get('generation') == 'continuation' or saved_kind == 'continuation'
                 else 'Follow-up' if saved_kind == 'followup' else 'Cross-prompt test' if saved_kind == 'cross_prompt'
                 else 'Fresh rerun' if saved_kind == 'retest' or record.get('generation') == 'fresh' or record.get('source_id')
                 else 'Ablation' if saved_kind == 'ablation' else 'Saved generation')
        stop = record.get('termination', record.get('stop'))
        # Old runs did not save an exact stop reason. Never infer EOS from a
        # short output or treat a heuristic repetition flag as a decoding stop.
        if stop is None and record.get('length_cap_reached') is True:
            stop = 'length'
        tokens = len(record['token_ids']) if 'token_ids' in record else record.get('n_tokens')
        row = dict(id=rid, original_id=original, name=name, text=raw['text'],
                   kind=kind, stage=stage, edits=edits, run=run,
                   prompt=record.get('prompt', prompt), tokens=tokens,
                   max_tokens=record.get('max_tokens', max_tokens), stop=stop,
                   weirdness=w, coherence=c, rating_source=rating_source,
                   ratings=ratings, category=judge.get('category'),
                   sources=[source], source_line=line,
                   source_id=record.get('source_id'), parents=record.get('parents', []),
                   library_path=enriched.get('path'), batch=record.get('batch', record.get('batch_id')),
                   temperature=record.get('temperature'), seed=record.get('seed'),
                   preview=bool(record.get('max_tokens', max_tokens) and record.get('max_tokens', max_tokens) < 160))
        rows[rid] = row
        if raw.get('id') and key not in by_original:
            by_original[key] = rid
        sources[source] += 1

    for i, raw in enumerate(data['attempts'], 1):
        add(raw, raw.get('run', 'library-export'), 'library/data.json', i,
            prompt='Who are you?')

    # Source records catch unlisted outputs and runs added since the last library
    # export. Judged copies supply metadata, not additional generations.
    for path in sorted((ROOT / 'runs').rglob('*.jsonl')):
        if path.name not in ('attempts.jsonl', 'generations.jsonl', 'screen.jsonl', 'steering.jsonl'):
            continue
        if not any(part.startswith(('neuron-', 'random-neurons-', 'owl-', 'riddle-repeatability-',
                                    'fresh-neuron-calibration-', 'pair-strength-search-')) for part in path.parts):
            continue
        rel = str(path.relative_to(ROOT))
        run = str(path.parent.relative_to(ROOT / 'runs')).replace('/', ' / ')
        meta = read_meta(path.parent)
        cap = meta.get('max_tokens', meta.get('args', {}).get('tokens'))
        for i, raw in enumerate(load_jsonl(path), 1):
            raw = dict(raw)
            if 'edits' not in raw:
                layer = raw.get('layer')
                neuron = raw.get('neuron', raw.get('unit'))
                if path.parent.name.startswith('riddle-repeatability-'):
                    layer, neuron = meta['layer'], meta['neuron']
                    signed = raw.get('signed_alpha', 0)
                    raw['kind'] = 'retest' if signed else 'control'
                elif path.parent.name.startswith('owl-followup-'):
                    # The original runner declares these constants explicitly.
                    layer, neuron, signed = 34, 13429, raw.get('dose', 0)
                else:
                    signed = raw.get('sign', 1) * raw.get('dose', 0)
                if layer is not None and neuron is not None and signed:
                    raw['edits'] = [[layer, neuron, 1 if signed > 0 else -1, abs(signed)]]
                elif raw.get('kind') == 'control' or raw.get('source') == 'control' or raw.get('dose') == 0 or raw.get('condition') == 'unsteered':
                    raw['edits'] = []
                else:
                    continue
            if any(part.startswith('retest-random-neurons-') for part in path.parts):
                raw['generation'] = 'fresh'
            add(raw, run, rel, i, max_tokens=cap)

    # These files save copied identity text alongside two new generations. Only
    # the newly generated where/when answers become additional reply records.
    for path in sorted((ROOT / 'runs').glob('neuron-followup*/followups.jsonl')):
        for i, record in enumerate(load_jsonl(path), 1):
            for field, prompt in [('where', 'Where do you live?'), ('when', 'What year is it now?')]:
                answer = record.get(field)
                if not isinstance(answer, dict) or 'text' not in answer:
                    continue
                raw = {**answer, 'id': f'row-{i:06d}-{field}', 'edits': record['edits'],
                       'name': record.get('name'), 'kind': 'followup', 'prompt': prompt}
                add(raw, path.parent.name, str(path.relative_to(ROOT)), i)

    results = list(rows.values())
    units = {(e[0], e[1]) for r in results for e in r['edits']}
    directions = {(e[0], e[1], e[2]) for r in results for e in r['edits']}
    text_groups = defaultdict(list)
    for r in results:
        digest = hashlib.sha256(normalized_text(r['text']).encode()).hexdigest()[:20]
        r['text_group'] = digest
        text_groups[digest].append(r['id'])
    for r in results:
        r['same_text_records'] = len(text_groups[r['text_group']])
    summary = dict(replies=len(results), physical_neurons=len(units),
                   signed_directions=len(directions), unique_texts=len(text_groups),
                   library_attempts=len(data['attempts']),
                   kinds=dict(Counter(r['kind'] for r in results)),
                   runs=dict(Counter(r['run'] for r in results)), sources=dict(sources),
                   scored=sum(r['weirdness'] is not None for r in results),
                   generated_utc=datetime.now(timezone.utc).isoformat())
    assert len(rows) == len({r['id'] for r in results})
    exported = {(r['original_id'], r['text']) for r in results}
    assert all((a['id'], a['text']) in exported for a in data['attempts'])
    OUT.mkdir(exist_ok=True)
    # Small assets stay separate from the full data so the UI paints immediately.
    files = []
    for start in range(0, len(results), 600):
        content = json.dumps(results[start:start + 600], ensure_ascii=False, separators=(',', ':')) + '\n'
        digest = hashlib.sha256(content.encode()).hexdigest()[:10]
        name = f'replies-{start // 600:03d}-{digest}.json'
        (OUT / name).write_text(content)
        files.append(name)
    version = hashlib.sha256(''.join(files).encode() + (OUT / 'raw-index.css').read_bytes()
                             + (OUT / 'raw-index.js').read_bytes()).hexdigest()[:12]
    manifest = dict(summary=summary, files=files, version=version)
    (OUT / 'index.html').write_text((HERE / 'templates' / 'raw-data.html').read_text().replace('__DATA_VERSION__', version))
    (OUT / 'index-data.json').write_text(json.dumps(manifest, ensure_ascii=False, separators=(',', ':')) + '\n')
    (OUT / 'coverage.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    build()

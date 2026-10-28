"""Export every requested raw reply, without ranking, excerpts or deduplication."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'runs/neuron-full-reply-review-20261028'

def main():
    protocol=json.loads((P/'protocol.json').read_text())
    rows=[json.loads(line) for line in (P/'attempts.jsonl').read_text().splitlines()]
    replies=sorted([r for r in rows if r['kind']=='retest'],key=lambda r:r['review_order'])
    expected=protocol['conditions']
    assert len(replies)==len(expected)==26
    assert len({r['review_order'] for r in replies})==26
    assert len({tuple(r['edits'][0][:2]) for r in replies})==25
    for actual,want in zip(replies,expected):
        assert actual['source_id']==want['source_id'] and actual['edits']==want['edits']
        assert actual['max_tokens']==160 and len(actual['token_ids'])<=160
        assert actual['termination'] in ['finished','length']
    manifest=json.loads((P/'manifest.json').read_text())
    assert manifest['repeat_stop'] is False
    lines=['# Full raw neuron reruns','', '25 physical neurons; 26 saved replies, including two strengths for the foot/ground neuron. Prompt: “Who are you?” Greedy decoding, 160-token cap; repetition stopping disabled. Fresh reruns at the saved interventions, not spliced continuations of the screening text. No outputs removed or shortened.','']
    for r in replies:
        l,u,s,d=r['edits'][0]
        end='Model stopped' if r['termination']=='finished' else 'Reached160-token cap'
        lines += [f'## {r["review_order"]}. L{l} N{u}, {"−" if s<0 else "+"}{d:g}×','',f'{end} · {len(r["token_ids"])} tokens · {r["id"]} · source {r["source_id"]}','','```text',r['text'],'```','']
    (P/'full-replies.md').write_text('\n'.join(lines))
    summary=dict(physical_neurons=25,replies=26,model_stopped=sum(r['termination']=='finished' for r in replies),hit_cap=sum(r['termination']=='length' for r in replies),repeat_stop=False,all_conditions_present=True,all_coefficients_match=True,all_text_preserved=True)
    (P/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))
    for r in replies:
        l,u,s,d=r['edits'][0]
        print(f'\n{r["review_order"]}. L{l} N{u} {"−" if s<0 else "+"}{d:g} | {len(r["token_ids"])} tokens | {r["termination"]}\n{r["text"]}')

if __name__=='__main__':main()

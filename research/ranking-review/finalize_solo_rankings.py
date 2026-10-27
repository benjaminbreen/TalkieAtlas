"""Consolidate the blinded v2 browsing audit; never replace generation judgments."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,collections
ROOT=Path(__file__).resolve().parents[2];run=ROOT/'runs/neuron-ranking-review-20261027'
mapdata=json.loads((run/'mapping.json').read_text());labels={}
for task in sorted((run/'tasks').glob('*.json')):
 expected=json.loads(task.read_text());out=json.loads((run/'labels'/task.name).read_text());assert {r['id'] for r in out}=={r['id'] for r in expected}
 for r in out:
  assert set(r)=={'id','weirdness','readability','richness','reason'} and r['id'] not in labels
  assert all(type(r[k]) is int and 0<=r[k]<=10 for k in ['weirdness','readability','richness'])
  assert len(r['reason'].split())<=16
  labels[r['id']]=r
assert len(labels)==1019
ratings={rid:{'version':2,'text_id':tid,**{k:v for k,v in labels[tid].items() if k!='id'}} for rid,tid in mapdata['reply_to_text_id'].items()};assert len(ratings)==1440
result={'version':2,'created':datetime.now(timezone.utc).isoformat(),'judge':'GPT-6 Luna via three Codex subagents','scope':'All 1,440 selected single-neuron replies; 1,019 whitespace/case-normalized unique texts rated once, without old labels or neuron metadata.','unique_texts':1019,'selected_replies':1440,'rubric':'ranking-rubric.md','rubric_sha256':hashlib.sha256((run/'RANKING_RUBRIC.md').read_bytes()).hexdigest(),'ratings':ratings}
(run/'rankings.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
original=json.loads((ROOT/'sites/talkie-neuron-sample/dist/data.json').read_text());h=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest();original_judgments={r['id']:r['judge'] for r in original['attempts']};validation={'unique_texts':1019,'selected_replies':1440,'files':43,'original_judgments_sha256':h(original_judgments),'checks':['All task IDs covered once','Exactly five required fields and integer0–10 scores','All reasons at most16 words','All selected solo reply IDs mapped','Identical normalized replies share a rating']};(run/'validation.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps({'complete':True,'weirdness_distribution':dict(sorted(collections.Counter(r['weirdness'] for r in labels.values()).items()))}))

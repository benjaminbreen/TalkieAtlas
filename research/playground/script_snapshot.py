"""A small, explicitly curated exploration of historically suggestive neuron pairs."""
from pathlib import Path
import json,time,itertools,hashlib
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/neuron-pair-playground-20261027'
PROMPT='Who are you?'
PAIRS=[('b0016-r09','b1012-r06'),('b0016-r09','b0031-r23'),('b1012-r06','b1007-r06'),('b0000-r25','b1012-r06'),('b0007-r22','b0016-r09'),('b0016-r09','b0029-r01'),('b1004-r31','b1012-r06'),('b0000-r25','b0031-r23')]
BALANCES=[(.75,.75),(1.,.35),(.35,1.)]
def save(name,obj):
 p=OUT/name;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');t.replace(p)

def main():
 OUT.mkdir(exist_ok=True)
 if (OUT/'attempts.jsonl').exists():raise RuntimeError('Refusing to overwrite saved generation')
 data=json.loads((ROOT/'sites/talkie-neuron-sample/dist/data.json').read_text());byid={r['id']:r for r in data['singles']}
 parents={i:byid[i] for pair in PAIRS for i in pair}
 save('parents.json',list(parents.values()));save('status.json',{'phase':'loading_model'})
 import mlx.core as mx
 from harness.engine import Loaded,format_chat,SPECIAL
 from harness.steer import Capture,Steer
 mx.set_cache_limit(1024**3);m=Loaded('it');ids=m.encode(format_chat([{'role':'user','content':PROMPT}]))
 cap=Capture('resid');m.model(mx.array([ids]),hooks=cap);scales={}
 for l in sorted({r['layer'] for r in parents.values()}):
  vals=cap.get('resid',l)[0,1:].astype(mx.float32);ns=mx.sqrt(mx.sum(vals*vals,axis=-1));mx.eval(ns);s=sorted(ns.tolist());scales[l]=(s[(len(s)-1)//2]+s[len(s)//2])/2
 cap.clear();directions={}
 for l,u in {(r['layer'],r['neuron']) for r in parents.values()}:
  basis=mx.zeros((1,13696),dtype=mx.bfloat16);basis[0,u]=1;block=m.model.blocks[l]
  v=block.mlp.mlp_resid(basis).astype(mx.float32)[0]*block.mlp_gain.astype(mx.float32);v=v/mx.sqrt(mx.sum(v*v));mx.eval(v);directions[l,u]=v
 conditions=[{'kind':'control','edits':[]}]
 for source,r in parents.items():conditions.append({'kind':'retest','source_id':source,'key':r['key'],'layer':r['layer'],'neuron':r['neuron'],'sign':r['sign'],'edits':r['edits']})
 for a,b in PAIRS:
  for fa,fb in BALANCES:
   conditions.append({'kind':'pair','parents':[a,b],'key':'play:'+a+'+'+b,'factors':[fa,fb],'factor':fa if fa==fb else None,'edits':[[l,u,s,alpha*f] for r,f in [(parents[a],fa),(parents[b],fb)] for l,u,s,alpha in r['edits']]})
 assert len(conditions)==33
 rows=[[('resid',l,directions[l,u],s*alpha*scales[l]) for l,u,s,alpha in c['edits']] for c in conditions]
 manifest={'created':datetime.now(timezone.utc).isoformat(),'model':'talkie-1930-13b-it','prompt':PROMPT,'temperature':0,'max_tokens':160,'selection':'Eight purposefully chosen pairs from already saved solos, selected for historical themes or playful contrasts; not a random sample.','balances':BALANCES,'intervention':'Same normalized effective MLP write directions as the atlas. Each parent scaled independently relative to its selected solo dose.','residual_medians':scales,'parent_ids':list(parents),'pairs':PAIRS,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 save('manifest.json',manifest);(OUT/'script_snapshot.py').write_bytes(Path(__file__).read_bytes());save('status.json',{'phase':'generating','conditions':33})
 hooks=Steer(rows);logits,cache=m.model(mx.array([ids]*len(rows)),hooks=hooks)
 results=[[] for _ in rows];done=[False]*len(rows);ends=['length']*len(rows);t0=time.monotonic()
 for _ in range(160):
  tok=mx.argmax(logits[:,-1,:m.n_real],axis=-1);mx.eval(tok)
  for i,t in enumerate(tok.tolist()):
   if done[i]:continue
   if t in set(SPECIAL.values()):done[i]=True;ends[i]='finished';continue
   results[i].append(t);ts=results[i]
   if len(ts)>=12 and any(len(ts)>=3*k and ts[-k:]==ts[-2*k:-k]==ts[-3*k:-2*k] for k in range(1,17)):done[i]=True;ends[i]='repeating'
  if all(done):break
  logits,cache=m.model(tok[:,None],cache,hooks=hooks)
 records=[{'id':f'b2000-r{i:02d}','batch':2000,'prompt':PROMPT,**c,'text':m.tok.decode(ts),'token_ids':ts,'termination':end} for i,(c,ts,end) in enumerate(zip(conditions,results,ends))]
 (OUT/'attempts.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records))
 save('judge_tasks.json',[{'id':r['id'],'text':r['text']} for r in records])
 save('pair_tasks.json',[{'id':r['id'],'parents':[parents[i]['text'] for i in r['parents']],'combined':r['text']} for r in records if r['kind']=='pair'])
 save('status.json',{'phase':'awaiting_judgments','attempts':len(records),'elapsed_seconds':round(time.monotonic()-t0,1)})
 print('Generated',len(records),'fresh replies in',round(time.monotonic()-t0,1),'seconds',flush=True)
 save('GENERATION_DONE.json',{'finished':datetime.now(timezone.utc).isoformat()})
if __name__=='__main__':main()

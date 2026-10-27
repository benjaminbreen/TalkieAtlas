"""Controlled repeatability probe of the atlas's L23 N5442 negative direction.

No prompt requests riddles. All outputs, seeds, intervention sizes and controls
are saved. Stochastic conditions share per-trial uniforms across interventions.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time,random,hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/riddle-repeatability-20261027'
PROMPTS=['Who are you?','Tell me something about yourself.','What do you do?','Describe a garden.']
CONDITIONS=[('unsteered',0.0),('negative_original',-1.25),('negative_half',-0.625),('positive_opposite',1.25)]
def save(name,obj):
 p=OUT/name;t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');t.replace(p)

def main():
 OUT.mkdir(exist_ok=True)
 for d in ['tasks','labels_a','labels_b']:(OUT/d).mkdir(exist_ok=True)
 if (OUT/'attempts.jsonl').exists():raise RuntimeError('Refusing to overwrite previous generation')
 save('status.json',{'phase':'loading_model'})
 import mlx.core as mx
 from harness.engine import Loaded,format_chat,SPECIAL
 from harness.steer import Capture,Steer
 mx.set_cache_limit(1024**3);m=Loaded('it');L,U=23,5442
 original=json.loads((ROOT/'sites/talkie-neuron-sample/dist/data.json').read_text());source=next(r for r in original['singles'] if (r['layer'],r['neuron'],r['sign'])==(L,U,-1));save('source.json',source)
 ids=m.encode(format_chat([{'role':'user','content':PROMPTS[0]}]));cap=Capture('resid',layers=[L]);m.model(mx.array([ids]),hooks=cap);v=cap.get('resid',L)[0,1:].astype(mx.float32);norms=mx.sqrt(mx.sum(v*v,axis=-1));mx.eval(norms);ns=sorted(norms.tolist());scale=(ns[(len(ns)-1)//2]+ns[len(ns)//2])/2;cap.clear()
 basis=mx.zeros((1,13696),dtype=mx.bfloat16);basis[0,U]=1;block=m.model.blocks[L];direction=block.mlp.mlp_resid(basis).astype(mx.float32)[0]*block.mlp_gain.astype(mx.float32);direction/=mx.sqrt(mx.sum(direction*direction));mx.eval(direction)
 manifest={'created':datetime.now(timezone.utc).isoformat(),'model':'talkie-1930-13b-it','source_id':source['id'],'layer':L,'neuron':U,'prompts':PROMPTS,'conditions':dict(CONDITIONS),'trials_per_sampled_condition':8,'temperature':0.7,'top_p':1.0,'max_tokens':160,'normalization':'Fixed unsteered Who are you? prompt median residual norm, first token excluded; original effective MLP write column including learned gain. Same edit magnitude across all prompts.','residual_median':scale,'sampler':'Inverse-CDF from full-vocabulary float32 softmax; independent Python random.Random(seed) streams per row; matched trial seeds share uniforms across intervention conditions. No repetition penalties.','greedy_retests':'Two identical original-strength rows in a 5-row batch and one singleton, compared with the stored original.','notes':['No prompt names or requests a riddle.','Each prompt is an independent single-turn native chat.','Positive and half-strength controls probe direction and dose; this is not a complete specificity study.','All outputs retained, including failures.'],'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 save('manifest.json',manifest);(OUT/'script_snapshot.py').write_bytes(Path(__file__).read_bytes());records=[];batchno=0;started=time.monotonic()
 def batch(prompt,conditions,temperature):
  nonlocal batchno
  ids=m.encode(format_chat([{'role':'user','content':prompt}]));hooks=Steer([[('resid',L,direction,c['signed_alpha']*scale)] if c['signed_alpha'] else [] for c in conditions]);B=len(conditions);logits,cache=m.model(mx.array([ids]*B),hooks=hooks)
  ts=[[] for _ in conditions];done=[False]*B;end=['length']*B;rngs=[random.Random(c.get('seed',0)) for c in conditions];t0=time.monotonic()
  for _ in range(160):
   if temperature==0:tok=mx.argmax(logits[:,-1,:m.n_real],axis=-1)
   else:
    ps=mx.softmax(logits[:,-1,:m.n_real]/temperature,axis=-1);us=mx.array([min(g.random(),1-2**-24) for g in rngs],dtype=mx.float32);tok=mx.minimum(mx.sum(mx.cumsum(ps,axis=-1)<us[:,None],axis=-1),m.n_real-1).astype(mx.int32)
   mx.eval(tok)
   for i,t in enumerate(tok.tolist()):
    if done[i]:continue
    if t in set(SPECIAL.values()):done[i]=True;end[i]='finished';continue
    ts[i].append(t)
    if len(ts[i])>=12 and any(len(ts[i])>=3*k and ts[i][-k:]==ts[i][-2*k:-k]==ts[i][-3*k:-2*k] for k in range(1,17)):done[i]=True;end[i]='repeating'
   if all(done):break
   logits,cache=m.model(tok[:,None],cache,hooks=hooks)
  new=[]
  for i,(c,tokens,ending) in enumerate(zip(conditions,ts,end)):
   r={'id':f'r{len(records)+i:04d}','batch':batchno,'source_id':source['id'],'prompt':prompt,'temperature':temperature,'top_p':1.0,**c,'text':m.tok.decode(tokens),'token_ids':tokens,'termination':ending};new.append(r)
  with (OUT/'attempts.jsonl').open('a') as f:
   for r in new:f.write(json.dumps(r,ensure_ascii=False)+'\n')
  records.extend(new);task=[{'id':r['id'],'text':r['text']} for r in new];random.Random(111+batchno).shuffle(task);save(f'tasks/task-{batchno:02d}.json',task);batchno+=1
  save('status.json',{'phase':'generating','batches':batchno,'replies':len(records),'elapsed_seconds':round(time.monotonic()-started,1)});print(f'Batch{batchno}: {B} rows in {time.monotonic()-t0:.1f}s; peak {mx.get_peak_memory()/1024**3:.1f}GB',flush=True);mx.clear_cache()
 greedy=[{'condition':name,'signed_alpha':a,'trial':0,'mode':'greedy_batch'} for name,a in CONDITIONS];greedy.append({'condition':'negative_original','signed_alpha':-1.25,'trial':1,'mode':'greedy_batch'});batch(PROMPTS[0],greedy,0)
 batch(PROMPTS[0],[{'condition':'negative_original','signed_alpha':-1.25,'trial':0,'mode':'greedy_singleton'}],0)
 for qi,prompt in enumerate(PROMPTS):
  conditions=[{'condition':name,'signed_alpha':a,'trial':trial,'seed':6102700+qi*100+trial,'mode':'sampled'} for trial in range(8) for name,a in CONDITIONS];random.Random(400+qi).shuffle(conditions);batch(prompt,conditions,0.7)
 assert len(records)==134
 save('status.json',{'phase':'generation_complete','replies':len(records),'elapsed_seconds':round(time.monotonic()-started,1)});save('GENERATION_DONE.json',{'finished':datetime.now(timezone.utc).isoformat()});print('Generation complete',flush=True)
if __name__=='__main__':main()

"""Rank saved fresh-neuron pair previews for human/assistant semantic inspection."""
import argparse,json,re
from collections import defaultdict
from difflib import SequenceMatcher
from experiments.review_neuron_expansion import RUN,read

def rank(rows):
    parents={r['id']:r for r in json.loads((RUN/'parents.json').read_text())}
    groups=defaultdict(list)
    for r in rows:
        if r['kind']=='pair' and 'pair-screen' in r['job']:groups[r['pair_id']].append(r)
    generic=re.compile(r'^i am (?:a |an |the )?(?:man\b|member\b|citizen\b|native\b|englishman\b|frenchman\b|gentleman\b|person\b|thomas\b|john\b)',re.I)
    wordset=lambda t:set(re.findall(r'[a-z]{3,}',t.lower()))
    out=[]
    for pid,rs in groups.items():
        ps=[parents[i] for i in rs[0]['parents']]
        usable=[r for r in rs if len(r['text'])>25 and r['termination']!='repeating' and r['triage']['unique_fraction']>.5]
        if not usable:continue
        sims=[max(SequenceMatcher(None,r['text'][:210].lower(),p['text'][:210].lower()).ratio() for p in ps) for r in usable]
        pw=set().union(*(wordset(p['text']) for p in ps))
        novelty=max(len(wordset(r['text'])-pw)/max(1,len(wordset(r['text']))) for r in usable)
        contrast=max((1-SequenceMatcher(None,a['text'][:210].lower(),b['text'][:210].lower()).ratio() for a in usable for b in usable),default=0)
        uncommon=sum(not generic.search(r['text']) for r in usable)
        priority=(1-min(sims))*.8+novelty*.6+contrast*.6+uncommon*.2
        out.append({'pair_id':pid,'parents':[p['name'] for p in ps],'priority':round(priority,3),'rows':rs})
    return sorted(out,key=lambda r:r['priority'],reverse=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=25);p.add_argument('--offset',type=int,default=0);p.add_argument('--chars',type=int,default=200);a=p.parse_args();rows=read();ranked=rank(rows)
    (RUN/'pair_triage.json').write_text(json.dumps(ranked,ensure_ascii=False,indent=2)+'\n');print('PAIRS',len(ranked),'ROWS',len(rows))
    for r in ranked[a.offset:a.offset+a.limit]:
        print('\n',r['pair_id'],r['priority'],' + '.join(r['parents']))
        for x in r['rows']:print(x['id'],x['factors'],x['termination'],' '.join(x['text'].split())[:a.chars])

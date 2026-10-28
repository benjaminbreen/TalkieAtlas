"""Compare saved strength sweeps. Mechanical rankings only aid editorial review."""
import argparse,json,re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/pair-strength-search-20261027'

def read():
    path=RUN/'attempts.jsonl'
    rows=[]
    for line in path.read_text().splitlines() if path.exists() else []:
        try:rows.append(json.loads(line))
        except json.JSONDecodeError:pass
    return rows

def rank(rows):
    groups=defaultdict(list)
    for r in rows:
        if r['kind']=='pair' and r['job']=='01-strength-screen':groups[r['pair_id']].append(r)
    parents={r['id']:r for r in json.loads((RUN/'parents.json').read_text())}
    result=[]
    generic=re.compile(r'^i am (a man[., ]|a member|a citizen|a native|an englishman|a gentleman|a stranger|a person who|john |thomas )',re.I)
    for key,rs in groups.items():
        rs.sort(key=lambda r:r['factor'])
        usable=[r for r in rs if r['termination']!='repeating' and len(r['text'])>24 and r['triage']['unique_fraction']>.4]
        if len(usable)<2:continue
        transitions=[]
        for a,b in zip(rs,rs[1:]):
            distance=1-SequenceMatcher(None,a['text'][:220].lower(),b['text'][:220].lower()).ratio()
            good=(a in usable and b in usable)
            transitions.append({'from':a['factor'],'to':b['factor'],'distance':round(distance,3),'both_usable':good})
        best=max((t['distance'] for t in transitions if t['both_usable']),default=0)
        novelty=max(1-max(SequenceMatcher(None,r['text'][:180].lower(),parents[i]['text'][:180].lower()).ratio() for i in r['parents']) for r in usable)
        nongeneric=sum(not generic.search(r['text']) for r in usable)
        priority=best+novelty*.6+nongeneric*.08+len(usable)*.03
        result.append({'pair_id':key,'priority':round(priority,3),'parents':[parents[i]['name'] for i in rs[0]['parents']],'rows':rs,'transitions':transitions})
    return sorted(result,key=lambda r:r['priority'],reverse=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=30);p.add_argument('--offset',type=int,default=0);p.add_argument('--chars',type=int,default=180);a=p.parse_args()
    rows=read();ranked=rank(rows)
    (RUN/'mechanical_pair_ranking.json').write_text(json.dumps(ranked,ensure_ascii=False,indent=2)+'\n')
    print('SAVED',len(rows),'COMPLETE SWEEPS',sum(len(g['rows'])==6 for g in ranked),'RANKED',len(ranked))
    for g in ranked[a.offset:a.offset+a.limit]:
        print('\n',g['pair_id'],g['priority'],' + '.join(g['parents']))
        for r in g['rows']:print(r['id'],r['factor'],r['termination'],' '.join(r['text'].split())[:a.chars])

"""Triage aids for the fresh-neuron study; priorities are not quality ratings."""
import argparse,json,math,re
from collections import Counter,defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/neuron-expansion-20261027'

def read():
    p=RUN/'attempts.jsonl';rows=[]
    for line in p.read_text().splitlines() if p.exists() else []:
        try:rows.append(json.loads(line))
        except json.JSONDecodeError:pass
    return rows

def shortlist(rows):
    scans=[r for r in rows if r['kind']=='single']
    generic=re.compile(r'^(?:i am (?:a |an |the )?(?:man\b|member\b|citizen\b|native\b|person\b|englishman\b|frenchman\b|scotchman\b|gentleman\b|soldier\b|stranger\b|son\b|clergyman\b|surgeon\b|christian\b|traveller\b|graduate\b|young man\b|inhabitant\b|john\b|thomas\b|william\b)|my name is (?:john|thomas|william)\b)',re.I)
    words=lambda t:re.findall(r'[a-z]{3,}',t.lower())
    df=Counter(w for r in scans for w in set(words(r['text'])))
    groups=defaultdict(list)
    for r in scans:groups[r['key']].append(r)
    seen=set();ranked=[]
    for r in scans:
        t=' '.join(r['text'].lower().split());ws=words(t);stats=r['triage']
        if t in seen or len(ws)<5 or r['termination']=='repeating' or stats['unique_fraction']<.55 or stats['max_trigram_repeats']>2:continue
        seen.add(t)
        rare=sum(math.log((len(scans)+1)/(df[w]+1)) for w in set(ws))/max(1,len(set(ws)))
        unusual=not bool(generic.search(t))
        contrast=max((1-SequenceMatcher(None,t,' '.join(s['text'].lower().split())).ratio() for s in groups[r['key']] if s['id']!=r['id']),default=0)
        priority=rare*.25+2*unusual+stats['self_description']*.4+min(1,len(ws)/20)*.4+contrast*.3
        ranked.append({**r,'priority':round(priority,3),'generic_opening':not unusual})
    return sorted(ranked,key=lambda r:r['priority'],reverse=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=50);p.add_argument('--offset',type=int,default=0);p.add_argument('--chars',type=int,default=300);p.add_argument('--job');a=p.parse_args()
    rows=read();ranked=shortlist(rows) if not a.job else [r for r in rows if r['job']==a.job and r['kind']!='control']
    print('SAVED',len(rows),'SCANNED',sum(r['kind']=='single' for r in rows),'CANDIDATES',len(ranked))
    for r in ranked[a.offset:a.offset+a.limit]:print(r['id'],r.get('priority',''),r.get('edits'),r['termination'],' '.join(r['text'].split())[:a.chars])
    if not a.job:(RUN/'mechanical_shortlist.json').write_text(json.dumps(ranked,ensure_ascii=False,indent=2)+'\n')

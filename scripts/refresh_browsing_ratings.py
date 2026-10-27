"""Apply preserved v2 solo ratings to existing static share pages and site.json.

The original `judge` objects in data.json are never changed. No images or model
outputs are regenerated. Run after building pages from compatible saved data.
"""
from pathlib import Path
import argparse,json,re
from html import escape
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--public',type=Path,default=Path(__file__).resolve().parents[1]/'public');a=p.parse_args();root=a.public
d=json.loads((root/'data.json').read_text());changed=0
for r in d['singles']:
 q=r.get('ranking')
 if not q:continue
 f=root/'n'/f"{r['layer']}-{r['neuron']}-{'up' if r['sign']>0 else 'down'}"/'index.html'
 if not f.exists():continue
 s=f.read_text()
 s,n=re.subn(r'<div><dt>Weirdness</dt><dd>[^<]*</dd></div>',f'<div><dt>Weirdness</dt><dd>{q["weirdness"]} / 10</dd></div>',s,count=1);assert n==1
 s,n=re.subn(r'<div><dt>(?:Coherence|Readability)</dt><dd>[^<]*</dd></div>',f'<div><dt>Readability</dt><dd>{q["readability"]} / 10</dd></div>',s,count=1);assert n==1
 s=re.sub(r'\s*<p class="ranking-note small">.*?</p>','',s,flags=re.S)
 note=escape(f'Luna v2 · Detail {q["richness"]}/10. {q["reason"]} Original v1: weirdness {r["judge"]["weirdness"]}/10, coherence {r["judge"]["coherence"]}/10.')
 s,n=re.subn(r'(<p class="baseline">.*?</p>)',lambda m:m[1]+f'\n    <p class="ranking-note small">{note}</p>',s,count=1,flags=re.S);assert n==1
 f.write_text(s);changed+=1
f=root/'site.json'
if f.exists():
 slim=json.loads(f.read_text());ratings={r['id']:r['ranking'] for r in d['singles']};slim['solo_rankings']=d['solo_rankings'];slim['manifest']['browsing_ratings']=d['solo_rankings']
 for key in ['singles','attempts']:
  for r in slim.get(key,[]):
   if r['id'] in ratings:r['ranking']=ratings[r['id']]
 f.write_text(json.dumps(slim,ensure_ascii=False,separators=(',',':')))
print(f'Updated {changed} static solo pages and the slim dataset')

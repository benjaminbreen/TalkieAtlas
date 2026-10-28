// Content-specific steam men for the fresh-neuron expansion; the shared kit stays unchanged.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {robotSVG} from './robot.mjs';
import {expansionEmblem} from './expansion-props.mjs';
const root=new URL('../',import.meta.url),run=new URL('../../../runs/neuron-expansion-20261027/',import.meta.url);
const reviews=JSON.parse(await readFile(new URL('editorial_reviews.json',run),'utf8'));
const solos=JSON.parse(await readFile(new URL('solo_reviews.json',run),'utf8'));
const selected=[...reviews.filter(r=>r.selected!==false).flatMap(r=>r.stages),...solos.filter(r=>r.featured).map(r=>({...r,label:r.name||r.label}))];
const rows=new Map((await readFile(new URL('attempts.jsonl',run),'utf8')).trim().split('\n').map(s=>{const r=JSON.parse(s);return[r.id,r]}));
const costumes=JSON.parse(await readFile(new URL('icons/expansion-costumes.json',root),'utf8'));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const ix={},zoo=[],missing=[];
await mkdir(new URL('dist/icons/',root),{recursive:true});
for(const stage of selected){
 if(ix[stage.id])continue;
 const c=costumes[stage.id];if(!c){missing.push(stage.id);continue}
 if(!rows.has(stage.id))throw Error('Missing saved reply '+stage.id);
 const {motif,...body}=c;let svg=robotSVG(body).replace('</svg>',expansionEmblem(motif)+'</svg>');
 svg=svg.replace('viewBox="-4 -30 128 152"',`viewBox="-4 -30 128 152" role="img" aria-label="${esc(stage.label)}"`).replace('><','><title>'+esc(stage.label)+'</title><');
 if(/undefined|NaN/.test(svg))throw Error('Invalid SVG '+stage.id);
 const file='expansion-'+stage.id+'.svg';await writeFile(new URL('dist/icons/'+file,root),svg);ix[stage.id]='icons/'+file;
 zoo.push(`<article><img src="../dist/icons/${file}" alt=""><b>${esc(stage.label)}</b><small>${esc(stage.id)}</small></article>`);
}
await writeFile(new URL('dist/icons/expansion-index.json',root),JSON.stringify(ix,null,2)+'\n');
await mkdir(new URL('design/',root),{recursive:true});
await writeFile(new URL('design/expansion-robots.html',root),`<!doctype html><meta charset="utf-8"><title>Fresh-neuron robot zoo</title><style>body{font:14px system-ui;padding:25px;background:white;color:#242428}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:10px}article{text-align:center;border:1px solid #e5e5ea;background:#f7f7f9;border-radius:12px;padding:8px}img{width:100%;max-height:160px}b,small{display:block}b{font-size:11px}small{font-size:9px;color:#777}</style><h1>${Object.keys(ix).length} fresh-neuron characters</h1><div class="grid">${zoo.join('')}</div>`);
console.log(JSON.stringify({generated:Object.keys(ix).length,missing}));
if(missing.length)process.exitCode=2;

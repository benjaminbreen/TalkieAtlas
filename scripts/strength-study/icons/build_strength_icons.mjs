// Build content-specific steam men for every currently selected strength-study reply.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {robotSVG} from './robot.mjs';
import {strengthEmblem} from './strength-props.mjs';
const root=new URL('../',import.meta.url),run=new URL('../../../runs/pair-strength-search-20261027/',import.meta.url);
const selections=JSON.parse(await readFile(new URL('editorial_reviews.json',run),'utf8'));
const rows=new Map((await readFile(new URL('attempts.jsonl',run),'utf8')).trim().split('\n').map(s=>{const r=JSON.parse(s);return[r.id,r]}));
const costumes=JSON.parse(await readFile(new URL('icons/strength-costumes.json',root),'utf8'));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const ix={},zoo=[],missing=[];
await mkdir(new URL('dist/icons/',root),{recursive:true});
for(const v of selections.filter(r=>r.selected!==false))for(const stage of v.stages){
 const c=costumes[stage.id];if(!c){missing.push(stage.id);continue}
 if(!rows.has(stage.id))throw Error('Missing saved reply '+stage.id);
 const {motif,...body}=c;let svg=robotSVG(body).replace('</svg>',strengthEmblem(motif)+'</svg>');
 svg=svg.replace('viewBox="-4 -30 128 152"',`viewBox="-4 -30 128 152" role="img" aria-label="${esc(stage.label)}"`).replace('><','><title>'+esc(stage.label)+'</title><');
 if(/undefined|NaN/.test(svg))throw Error('Invalid SVG '+stage.id);
 const file='strength-'+stage.id+'.svg';await writeFile(new URL('dist/icons/'+file,root),svg);ix[stage.id]='icons/'+file;
 zoo.push(`<article><img src="../dist/icons/${file}" alt=""><b>${esc(stage.label)}</b><small>${esc(stage.id)}</small></article>`);
}
await writeFile(new URL('dist/icons/strength-index.json',root),JSON.stringify(ix,null,2)+'\n');
await mkdir(new URL('design/',root),{recursive:true});
await writeFile(new URL('design/strength-robots.html',root),`<!doctype html><meta charset="utf-8"><title>Strength-study robot zoo</title><style>body{font:14px system-ui;padding:25px;background:white;color:#242428}.grid{display:grid;grid-template-columns:repeat(8,1fr);gap:10px}article{text-align:center;border:1px solid #e5e5ea;background:#f7f7f9;border-radius:12px;padding:8px}img{width:100%;max-height:160px}b,small{display:block}b{font-size:11px}small{font-size:9px;color:#777}</style><h1>${Object.keys(ix).length} strength-study characters</h1><div class="grid">${zoo.join('')}</div>`);
console.log(JSON.stringify({generated:Object.keys(ix).length,missing}));
if(missing.length)process.exitCode=2;

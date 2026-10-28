// Robot icons for the 50 top-rated drug x persona blends: one costume per persona neuron plus one emblem per
// drug state. Blends sharing a persona and state share an icon.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {robotSVG} from './robot.mjs';
import {drugEmblem} from './drug-cross-props.mjs';
const root=new URL('../',import.meta.url);
const run=new URL('../../../runs/drug-persona-cross-20261028/review/',import.meta.url);
const entries=JSON.parse(await readFile(new URL('library_admissions.json',run),'utf8')).entries.filter(e=>e.icon);
const costumes=JSON.parse(await readFile(new URL('icons/drug-cross-costumes.json',root),'utf8'));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const slug=s=>s.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
await mkdir(new URL('dist/icons/',root),{recursive:true});
const index={},made=new Set();
for(const e of entries){
 const c=costumes[e.persona.name];if(!c)throw Error('Missing costume '+e.persona.name);
 const file=`icons/drug-${slug(e.persona.name)}-${e.state.replace(/_/g,'-')}.svg`;
 if(!made.has(file)){
  const label=`${e.persona.name} + ${e.state_label}`;
  let svg=robotSVG(c).replace('</svg>',drugEmblem(e.state)+'</svg>');
  svg=svg.replace('viewBox="-4 -30 128 152"',`viewBox="-4 -30 128 152" role="img" aria-label="${esc(label)}"`).replace('><','><title>'+esc(label)+'</title><');
  if(/NaN|undefined/.test(svg))throw Error('Bad SVG '+file);
  await writeFile(new URL('dist/'+file,root),svg);made.add(file);
 }
 index[e.key]=file;
}
await writeFile(new URL('dist/icons/drug-cross-index.json',root),JSON.stringify(index,null,2)+'\n');
console.log(JSON.stringify({entries:Object.keys(index).length,distinct_icons:made.size}));

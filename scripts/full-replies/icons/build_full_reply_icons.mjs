import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {robotSVG} from './robot.mjs';
import {fullReplyEmblem} from './full-reply-props.mjs';
const root=new URL('../',import.meta.url);
const run=new URL('../../../runs/neuron-full-reply-review-20261028/',import.meta.url);
const choices=JSON.parse(await readFile(new URL('library_admissions.json',run),'utf8')).selected;
const costumes=JSON.parse(await readFile(new URL('icons/full-reply-costumes.json',root),'utf8'));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const index={};await mkdir(new URL('dist/icons/',root),{recursive:true});
for(const choice of choices){
 const c=costumes[choice.id];if(!c)throw Error('Missing costume '+choice.id);
 const {motif,...body}=c;
 let svg=robotSVG(body).replace('</svg>',fullReplyEmblem(motif)+'</svg>');
 svg=svg.replace('viewBox="-4 -30 128 152"',`viewBox="-4 -30 128 152" role="img" aria-label="${esc(choice.name)}"`).replace('><','><title>'+esc(choice.name)+'</title><');
 if(/NaN|undefined/.test(svg))throw Error('Bad SVG '+choice.id);
 const file='persona-'+choice.id+'.svg';await writeFile(new URL('dist/icons/'+file,root),svg);index[choice.id]='icons/'+file;
}
await writeFile(new URL('dist/icons/full-reply-index.json',root),JSON.stringify(index,null,2)+'\n');
console.log(JSON.stringify({generated:Object.keys(index).length,missing:choices.filter(c=>!index[c.id]).map(c=>c.id)}));

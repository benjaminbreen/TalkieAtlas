// Render newly added sharing cards directly from SVG; leave existing cards intact.
import {readFile,writeFile,mkdir,access} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import sharp from '/Users/benbreen/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs';
const root=fileURLToPath(new URL('.',import.meta.url));
const {jobs,site}=JSON.parse(await readFile(join(root,'build/og-jobs.json'),'utf8'));
const xml=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const exists=async p=>access(p).then(()=>true,()=>false);
const width=(s,size)=>[...s].reduce((n,c)=>n+(/[ilI.,' :;!]/.test(c)?.28:/[MW@]/.test(c)?.85:.53)*size,0);
function wrap(text,size,max){
 const lines=[];let line='';
 for(const word of String(text).split(/\s+/)){const next=line?line+' '+word:word;if(width(next,size)>max&&line){lines.push(line);line=word;}else line=next;}
 if(line)lines.push(line);return lines;
}
const text=(lines,x,y,size,{center=false,color='#1d1d1f',family='Arial, sans-serif',weight=400,leading=1.2}={})=>`<text x="${x}" y="${y}" fill="${color}" font-family="${family}" font-size="${size}" font-weight="${weight}"${center?' text-anchor="middle"':''}>${lines.map((t,i)=>`<tspan x="${x}" dy="${i?size*leading:0}">${xml(t)}</tspan>`).join('')}</text>`;
async function embed(path,x,y,w,h){const buf=await readFile(path);return `<image x="${x}" y="${y}" width="${w}" height="${h}" href="data:image/svg+xml;base64,${buf.toString('base64')}"/>`;}
const mastIcon=await embed(join(root,'dist/icons/17-10423-down.svg'),56,32,38,45);
let count=0,idx=0;
const pending=[];for(const j of jobs)if(!await exists(join(root,'dist',j.out)))pending.push(j);
await Promise.all(Array.from({length:4},async()=>{
 while(idx<pending.length){
  const j=pending[idx++];if(j.home)continue;
  const icon=j.icon?await embed(join(root,j.icon.replace(/^\//,'')),205,120,144,171):'';
  const parents=wrap((j.parents||[]).join(' + '),17,420);
  const catalogue=wrap(j.catalogue.replace(/^talkie-1930 · /,''),16,420);
  let size=58,lines;
  for(;size>=30;size-=2){lines=wrap(j.name,size,440);const h=(icon?171+14:0)+lines.length*size*1.05+(parents.length?parents.length*20+14:0)+catalogue.length*18+14;if(h<=390)break;}
  let y=icon?305:205;const title=text(lines,276,y+size*.8,size,{center:true,weight:600,leading:1.05});
  y+=lines.length*size*1.05+15;
  const parentText=text(parents,276,y+17*.8,17,{center:true,color:'#74747c'});y+=parents.length*20+18;
  const catText=text(catalogue,276,y+16*.8,16,{center:true,color:'#74747c'});
  let quote=wrap(j.text,25,490);
  if(quote.length>8){quote=quote.slice(0,8);quote[7]=quote[7].replace(/[\s,;:.]*$/,'')+'…';}
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="white"/>${mastIcon}${text(['Talkie Persona Library'],106,64,27,{weight:600})}${text([site],1144,62,18,{color:'#74747c',center:false}).replace('x="1144"','x="1144" text-anchor="end"')}${icon}${title}${parentText}${catText}<rect x="958" y="120" width="186" height="50" rx="22" fill="#0071e3"/>${text(['Who are you?'],979,153,23,{color:'white'})}<rect x="550" y="187" width="594" height="325" rx="22" fill="#f5f5f7"/>${text(quote,576,226,25,{family:'Georgia, serif',leading:1.4})}<path d="M56 557H1144" stroke="#e6e6ea"/>${text(['An AI trained on text from before 1931.'],56,597,18,{color:'#74747c'})}${text(['Made by Benjamin Breen'],1144,597,18,{color:'#74747c'}).replace('x="1144"','x="1144" text-anchor="end"')}</svg>`;
  const target=join(root,'dist',j.out);await mkdir(join(root,'dist/og'),{recursive:true});
  await sharp(Buffer.from(svg)).png({compressionLevel:9,palette:true}).toFile(target);
  if(++count%250===0)console.log(count,'new cards');
 }
}));
console.log('Rendered',count,'new sharing cards.');

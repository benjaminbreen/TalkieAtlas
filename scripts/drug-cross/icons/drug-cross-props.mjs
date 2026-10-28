// Drug and altered-state emblems for the drug x persona blends, drawn around the existing steam-man body.
const O='#2b2522',C='#f6efe2',G='#e2a83e',Y='#f2c230',B='#8fc7e8',R='#c0392b',GR='#9aa0a6';
const el=(n,a,b='')=>`<${n} ${Object.entries(a).map(([k,v])=>`${k}="${v}"`).join(' ')}>${b}</${n}>`;
const path=(d,fill=C,w=1.8)=>el('path',{d,fill,stroke:O,'stroke-width':w,'stroke-linejoin':'round','stroke-linecap':'round'});
const line=(d,c=O,w=1.8)=>el('path',{d,fill:'none',stroke:c,'stroke-width':w,'stroke-linecap':'round','stroke-linejoin':'round'});
const rect=(x,y,w,h,fill=C,r=2)=>el('rect',{x,y,width:w,height:h,rx:r,fill,stroke:O,'stroke-width':1.6});
const circle=(x,y,r,fill=C)=>el('circle',{cx:x,cy:y,r,fill,stroke:O,'stroke-width':1.5});
const text=(x,y,t,z=8,fill=O)=>el('text',{x,y,'text-anchor':'middle','font-family':'Georgia,serif','font-weight':700,'font-size':z,fill},t);
const badge=t=>rect(43,79,34,18)+text(60,91,t,Math.min(10,47/t.length));
const star=(x,y,r,fill=Y)=>path([0,1,2,3,4,5,6,7,8,9].map(i=>{const a=Math.PI*i/5-Math.PI/2,q=i%2?r*0.45:r;return `${i?'L':'M'}${(x+q*Math.cos(a)).toFixed(1)} ${(y+q*Math.sin(a)).toFixed(1)}`;}).join(' ')+'Z',fill,1.3);
const poppy=(x,y)=>line(`M${x} ${y+6} Q${x+2} ${y+22} ${x-2} ${y+34}`,'#5b8f4e',2.4)+[0,72,144,216,288].map(d=>el('ellipse',{cx:x,cy:y-6,rx:5,ry:7.5,fill:R,stroke:O,'stroke-width':1.3,transform:`rotate(${d} ${x} ${y})`})).join('')+circle(x,y,3.5,'#2b2a33');
const bottle=(x,y,fill,label)=>path(`M${x-3} ${y} H${x+3} V${y+7} Q${x+9} ${y+10} ${x+9} ${y+17} V${y+34} H${x-9} V${y+17} Q${x-9} ${y+10} ${x-3} ${y+7} Z`,fill)+rect(x-4,y-4,8,5,'#8b5e3c',1)+rect(x-7,y+19,14,10,C,1)+text(x,y+27,label,label.length>2?4.5:7);
const gasBag=(x,y)=>path(`M${x} ${y+16} Q${x-14} ${y+12} ${x-13} ${y-2} Q${x-12} ${y-16} ${x} ${y-17} Q${x+12} ${y-16} ${x+13} ${y-2} Q${x+14} ${y+12} ${x} ${y+16} Z`,B)+line(`M${x} ${y+16} Q${x+2} ${y+28} ${x+12} ${y+34}`,O,2)+rect(x-4,y+14,8,5,G,1);
const wisps=(x,y,c=GR)=>line(`M${x} ${y+24} q-6 -6 0 -12 t0 -12 M${x+9} ${y+26} q-6 -6 0 -12 t0 -12 t0 -10`,c,2.4);
const zzz=(x,y)=>text(x,y+22,'Z',13)+text(x+10,y+10,'z',10)+text(x+18,y+1,'z',8);
const motifs={
 opium:()=>badge('OPIUM')+poppy(10,2)+wisps(102,-18),
 laughing_gas:()=>badge('GAS')+gasBag(12,-6)+text(104,-4,'HA',10)+text(114,12,'HA',9)+text(104,26,'HA',8),
 nitrous_agent:()=>badge('N₂O')+gasBag(12,-6)+circle(104,-8,5,B)+circle(114,6,3.5,B)+circle(106,18,2.5,B),
 anaesthetic_gas:()=>badge('ETHER')+bottle(12,-18,'#d5edf5','ETHER')+wisps(102,-16,B),
 chloroform:()=>badge('CHLORO')+bottle(12,-18,'#c9d9b8','CHCl₃')+path('M98 4 Q110 -6 122 4 L118 22 Q110 16 102 22 Z',C)+zzz(98,-24),
 worse_for_liquor:()=>badge('LIQUOR')+bottle(12,-18,'#5b8f4e','GIN')+text(108,-2,'hic!',9)+circle(102,14,3,B)+circle(112,22,2,B),
 stars:()=>badge('STARS')+star(10,-8,8)+star(24,10,5)+star(108,-12,7)+star(116,8,5)+star(98,4,4),
 exhilarated:()=>badge('HURRAH')+[[10,-6],[110,-6]].map(([x,y])=>[0,45,90,135,180,225,270,315].map(d=>line(`M${x} ${y} m${(5*Math.cos(d*Math.PI/180)).toFixed(1)} ${(5*Math.sin(d*Math.PI/180)).toFixed(1)} l${(6*Math.cos(d*Math.PI/180)).toFixed(1)} ${(6*Math.sin(d*Math.PI/180)).toFixed(1)}`,G,2.2)).join('')).join('')+star(22,14,4)+star(98,14,4),
 artificial_somnambulism:()=>badge('TRANCE')+line('M14 -26 L10 2',O,1.6)+circle(10,8,7,G)+line('M10 8 m-4 0 a4 4 0 1 1 4 4 a2 2 0 1 1 -2 -2',O,1.2)+zzz(98,-22),
};
export function drugEmblem(kind){if(!motifs[kind])throw Error('Unknown drug emblem '+kind);return `<g data-drug-emblem="${kind}">${motifs[kind]()}</g>`}

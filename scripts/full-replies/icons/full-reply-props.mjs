// Semantic details for the existing steam-man kit; no shared renderer changes.
import {expansionEmblem} from './expansion-props.mjs';
const O='#2b2522',C='#f6efe2',G='#e2a83e',B='#8fc7e8',P='#ddd6f3';
const el=(n,a,b='')=>`<${n} ${Object.entries(a).map(([k,v])=>`${k}="${v}"`).join(' ')}>${b}</${n}>`;
const path=(d,fill=C,w=1.8)=>el('path',{d,fill,stroke:O,'stroke-width':w,'stroke-linejoin':'round','stroke-linecap':'round'});
const line=(d,c=O,w=1.8)=>path(d,'none',w).replace(`stroke="${O}"`,`stroke="${c}"`);
const rect=(x,y,w,h,fill=C,r=2)=>el('rect',{x,y,width:w,height:h,rx:r,fill,stroke:O,'stroke-width':1.6});
const circle=(x,y,r,fill=C)=>el('circle',{cx:x,cy:y,r,fill,stroke:O,'stroke-width':1.5});
const text=(x,y,t,z=8)=>el('text',{x,y,'text-anchor':'middle','font-family':'Georgia,serif','font-weight':700,'font-size':z,fill:O},t);
const badge=t=>rect(43,79,34,18)+text(60,91,t,Math.min(10,47/t.length));
const ghost=(x,y)=>path(`M${x-8} ${y+19} V${y} Q${x-8} ${y-14} ${x} ${y-14} Q${x+8} ${y-14} ${x+8} ${y} V${y+19} l-4 -4 l-4 4 l-4 -4 Z`,P)+circle(x-3,y,1,O)+circle(x+3,y,1,O);
const book=(x,y,t)=>rect(x,y,25,32,'#5b8f4e')+line(`M${x+4} ${y+2} V${y+29}`,C,1.2)+text(x+15,y+18,t,6);
const motifs={
 shoemaker:()=>badge('COVER')+path('M-1 90 V68 H12 V83 Q26 84 28 94 V101 H-1 Z','#8b5e3c')+line('M2 98 H26 M3 76 H10 M3 81 H10',C,1.3)+rect(99,62,23,38)+text(110,75,'COAT',6)+text(110,87,'VEST',6)+text(110,99,'BOOTS',5),
 eternal:()=>badge('ETERNAL')+ghost(10,29)+text(110,16,'∞',26)+line('M109 46 V78 M100 55 H118',G,3),
 happyDead:()=>badge('HAPPY')+ghost(10,29)+path('M98 108 V72 Q98 59 110 59 Q122 59 122 72 V108 Z','#9aa0a6')+line('M104 79 Q110 88 116 79',C,2)+circle(106,72,1.5,O)+circle(114,72,1.5,O),
 curiosity:()=>badge('PRESERVE')+rect(0,60,27,46,'#d8b07a')+rect(3,64,21,38,C)+text(13,77,'DRY',6)+text(13,88,'MEMO',6)+text(13,99,'1840',6)+path('M98 107 V41 Q98 29 110 29 Q122 29 122 41 V107 Z','#d5edf5')+circle(110,64,7,'#d8b07a')+line('M100 111 H122',O,2),
 mountainKing:()=>badge('KING')+path('M-3 113 L12 58 L30 113 Z','#9aa0a6')+path('M5 83 L12 58 L21 87 L13 81 Z',C)+path('M95 113 L109 72 L124 113 Z','#d8b07a')+line('M3 111 Q12 102 10 95 T19 80',C,2),
 causes:()=>badge('CAUSES')+[10,110].map(x=>circle(x,41,10,B)+path(`M${x-5} 44 L${x} 35 L${x+5} 44 Z`,G,1.3)).join('')+line('M0 75 H23 M18 70 L23 75 L18 80 M97 75 H121 M116 70 L121 75 L116 80',O,2)+text(12,102,'SEEN',7)+text(109,102,'READ',7),
 siblings:()=>badge('HALF')+line('M4 59 H25 M15 46 V59 M99 59 H122 M110 46 V59',O,2)+[5,22,101,119].map((x,i)=>circle(x,70,5,i%2?G:P)+path(`M${x-6} 92 V82 Q${x} 75 ${x+6} 82 V92 Z`,i%2?G:P,1.2)).join('')+text(13,33,'½',20)+text(110,33,'½',20),
 sealFisher:()=>badge('SEAL')+path('M-1 101 Q1 84 11 86 Q21 85 23 95 L30 102 L18 104 L8 106 Z','#9aa0a6')+circle(8,91,1.5,O)+line('M2 95 L-3 93 M3 98 L-2 99',O,1)+line('M96 111 q7 -5 14 0 t14 0','#6aa6c8',2)+path('M100 85 V70 Q110 63 120 70 V85 Z',C)+line('M110 73 V82',O,1.5),
 childhood:()=>badge('SECOND')+circle(12,35,13,B)+path('M3 33 L10 26 L18 30 L17 38 L8 43 L1 38 Z','#5b8f4e',1.3)+rect(99,81,24,24,P)+text(111,98,'2',16)+circle(110,52,10,G)+line('M110 62 V76',O,3),
 frontView:()=>badge('FRONT')+rect(-1,24,27,44,C)+path('M3 47 Q12 36 22 47 V60 H3 Z',P,1.3)+circle(12,35,6,P)+line('M96 48 H121 M116 43 L121 48 L116 53',O,2)+text(109,73,'YOU',9),
 empire:()=>badge('EMPIRE')+rect(0,63,27,41,'#d8b07a')+path('M-2 63 L13 52 L29 63 Z',G)+[4,11,18,25].map(x=>line(`M${x} 67 V98`,C,2)).join('')+text(109,36,'⅕',22)+circle(109,71,12,B)+path('M102 66 L108 61 L116 65 L113 74 L105 78 Z','#5b8f4e',1.2),
 groundWords:()=>badge('GROUND')+[-1,97].map(x=>rect(x,71,27,10,'#d8b07a',0)+rect(x,81,27,10,'#8b5e3c',0)+rect(x,91,27,10,'#e6e1d6',0)).join('')+path('M-1 107 V96 H11 V103 L26 107 V113 H-1 Z','#8b5e3c')+book(98,24,'PEN'),
 signalman:()=>badge('SIGNAL')+line('M8 112 V29 M8 43 H27 M109 112 V29 M109 49 H123',O,3)+rect(8,31,22,8,'#c0392b')+rect(109,37,16,8,'#c0392b')+circle(8,51,3,G)+circle(109,56,3,G)+line('M0 113 L27 102 M94 102 L122 113',O,1.4),
 expression:()=>expansionEmblem('expression'),
 map:()=>expansionEmblem('map'),
 powder:()=>expansionEmblem('powderPuff'),
 brook:()=>badge('LIFE')+path('M0 38 Q12 26 26 38 V57 H0 Z','#d8b07a')+line('M0 59 q7 -6 14 0 t14 0 M93 68 q7 -6 14 0 t14 0 M0 111 Q26 99 44 115 M83 114 Q104 98 124 110','#6aa6c8',3)+text(110,30,'∞',22),
 field:()=>expansionEmblem('field'),
 strata:()=>badge('STRATA')+[-1,98].map(x=>[0,1,2,3,4].map(i=>rect(x,63+i*9,26,9,['#d8b07a','#8b5e3c','#e6e1d6','#b5523b','#d8b07a'][i],0)).join('')).join('')+line('M2 59 L14 50 L26 59',O,1.8),
};
export function fullReplyEmblem(kind){if(!motifs[kind])throw Error('Unknown full-reply emblem '+kind);return `<g data-persona-emblem="${kind}">${motifs[kind]()}</g>`}

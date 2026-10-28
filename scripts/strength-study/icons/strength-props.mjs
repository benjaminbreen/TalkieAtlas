// Small, content-specific additions for strength-study steam men. The original kit is unchanged.
const O='#2b2522',C='#f6efe2',G='#e2a83e',B='#8fc7e8',P='#ddd6f3';
const el=(n,a,b='')=>`<${n} ${Object.entries(a).map(([k,v])=>`${k}="${v}"`).join(' ')}>${b}</${n}>`;
const path=(d,fill=C,w=2)=>el('path',{d,fill,stroke:O,'stroke-width':w,'stroke-linejoin':'round','stroke-linecap':'round'});
const line=(d,c=O,w=2)=>path(d,'none',w).replace(`stroke="${O}"`,`stroke="${c}"`);
const rect=(x,y,w,h,fill=C,r=2)=>el('rect',{x,y,width:w,height:h,rx:r,fill,stroke:O,'stroke-width':1.8});
const circle=(x,y,r,fill=C)=>el('circle',{cx:x,cy:y,r,fill,stroke:O,'stroke-width':1.6});
const text=(x,y,t,z=8)=>el('text',{x,y,'text-anchor':'middle','font-family':'Georgia,serif','font-weight':700,'font-size':z,fill:O},t);
const badge=t=>rect(44,79,32,19,C)+text(60,92,t,Math.min(10,45/Math.max(1,t.length)));
const book=(x,y,t='')=>rect(x,y,24,30,'#5b8f4e')+line(`M${x+4} ${y+3} V${y+27}`,C,1.5)+(t?text(x+15,y+18,t,7):'');
const grain=(x,y)=>line(`M${x} ${y+26} V${y-10}`,'#b88a2e')+Array.from({length:5},(_,i)=>el('ellipse',{cx:x+(i%2?3:-3),cy:y+i*4,rx:3,ry:5,fill:'#e9c46a',stroke:'#8b5e3c','stroke-width':1})).join('');
const ghost=(x,y)=>path(`M${x-8} ${y+18} V${y} Q${x-8} ${y-14} ${x} ${y-14} Q${x+8} ${y-14} ${x+8} ${y} V${y+18} l-5 -4 l-3 5 l-4 -5 Z`,P,1.5)+circle(x-3,y,1,O)+circle(x+3,y,1,O);
const steam=()=>[0,1,2].map(i=>line(`M${5+i*8} 20 q-6 -7 0 -13 q6 -7 0 -13`,'#aab4bd',1.8)).join('');
const dots=(x,y,n=6)=>Array.from({length:n},(_,i)=>circle(x+(i%2)*7,y+Math.floor(i/2)*7,1.7,O)).join('');
const keys=(x,y)=>rect(x,y,33,15,C)+[1,2,4,5,6].map(i=>rect(x+i*4,y,2.5,8,O,0)).join('');
const masks=n=>Array.from({length:n},(_,i)=>{let x=i<5?4:107,y=2+(i%5)*20;return path(`M${x} ${y} Q${x+7} ${y-4} ${x+14} ${y} V${y+8} Q${x+7} ${y+18} ${x} ${y+8} Z`,P,1.2)+circle(x+4,y+4,1,O)+circle(x+10,y+4,1,O)}).join('');
const motifs={
 school:()=>rect(92,61,27,29,'#384752')+text(105,73,'ABC',7).replace(`fill="${O}"`,'fill="#f6efe2"')+line('M98 82 H112',C,1.5)+badge('9'),
 dressmaker:()=>rect(93,62,24,28,'#384752')+text(105,75,'ABC',7).replace(`fill="${O}"`,'fill="#f6efe2"')+line('M98 82 H112',C,1.5)+line('M8 71 l10 -18 M8 72 q-9 17 5 23 q12 0 5 -11','#c0392b',1.6)+circle(18,53,2,C),
 wheat:()=>grain(9,61)+grain(111,69)+path('M44 91 Q44 77 60 77 Q76 77 76 91 Z','#d8b07a')+line('M52 83 l-2 5 M61 81 l-1 7 M69 83 l-1 5',C,1.3),
 corn:()=>grain(108,60)+ghost(10,22)+badge('CORN'),
 house:()=>path('M-1 78 L15 62 L31 78 V105 H1 Z','#e6e1d6')+rect(10,88,10,17,'#8b5e3c')+rect(3,78,6,6,B)+rect(20,78,6,6,B)+badge('HOME'),
 hen:()=>path('M47 23 q-7 -15 1 -17 q7 -4 10 10 q2 -17 9 -10 q6 2 1 17','#c0392b')+Array.from({length:9},(_,i)=>circle(44+(i%3)*15,81+Math.floor(i/3)*6,1.8,i%2?O:C)).join('')+el('ellipse',{cx:108,cy:99,rx:8,ry:11,fill:C,stroke:O,'stroke-width':1.8}),
 steamrod:()=>steam()+rect(0,74,22,32,'#aab4bd')+line('M4 80 H19 M11 65 V99 M97 99 L114 57 M97 99 L112 109',O,3)+circle(98,98,7,G)+badge('ROD'),
 publisher:()=>book(97,61,'?')+book(1,75,'JS')+badge('11'),
 harmonium:()=>rect(89,64,33,34,'#8b5e3c')+keys(89,81)+line('M95 98 V109 M117 98 V109',O,3)+rect(93,68,24,8,'#d8b07a')+badge('SALE'),
 sewing:()=>badge('£5')+line('M13 17 H24 V-4 H12 V20','#9aa0a6',1.6)+rect(12,-10,12,6,'#c0392b'),
 chronicle:()=>ghost(8,12)+book(97,60,'ALL')+badge('DAY')+circle(112,2,5,G)+line('M105 12 L113 17 L118 10',G,1.8),
 powder:()=>badge('E')+path('M2 95 H25 L29 108 H0 Z',C)+circle(7,91,1.4,C)+circle(15,86,1.5,C)+circle(20,92,1.6,C),
 cement:()=>path('M1 77 L5 65 H26 L29 106 H0 Z','#b8b3a4')+text(14,87,'CEM',7)+line('M8 93 H23',O,1.3)+badge('DUST'),
 steel:()=>path('M-1 91 L7 81 H23 L30 93 H-1 Z','#c9d6dc')+text(60,92,'STEEL',8)+rect(96,55,25,31,C)+text(108,66,'GOOD',5.5)+text(108,77,'MASTER?',5),
 gelatine:()=>rect(0,51,28,56,'#d5edf5',5)+rect(-1,48,30,7,'#9aa0a6')+path('M6 83 L9 71 L16 71 L20 79 L20 91 H16 V83 H11 V91 H7 Z','#c98b4f',1.2)+line('M3 60 L23 97','#fff',1.8)+badge('GEL'),
 doctor:()=>rect(0,72,25,24,'#4b3630')+line('M6 73 v-8 h13 v8',O,2)+text(12,88,'MD',8)+rect(96,4,26,18,C)+text(109,11,'IPE',6)+text(109,18,'SQ.',6),
 type:()=>rect(0,79,16,23,'#bdc7cd')+text(8,95,'A',12)+rect(100,68,20,25,'#c9d6dc')+text(110,85,'B',12)+path('M2 35 V22 L8 16 L14 22 V35 Z','#d4d6da',1)+circle(8,15,5,'#d4d6da')+badge('TYPE'),
 chain:()=>[0,107].map(x=>[55,69,83,97].map(y=>el('ellipse',{cx:x+7,cy:y,rx:5,ry:10,fill:'none',stroke:'#7c8288','stroke-width':2.3})).join('')).join('')+badge('LINK'),
 efficiency:()=>circle(10,39,11,G)+line('M10 31 V39 L16 43',O,2)+badge('−t'),
 bird:()=>grain(112,78)+[2,9,17].map(x=>circle(x,107,1.7,'#e9c46a')).join('')+badge('CORN'),
 plants:()=>path('M9 107 V47 M9 60 Q-3 48 3 43 Q15 49 9 60 M9 78 Q24 63 28 68 Q27 80 9 78','#5b8f4e')+rect(96,53,25,41,C)+line('M101 60 H116 M101 66 H114 M101 85 H116','#5b8f4e',1.5)+text(108,78,'?',14),
 gentleman:()=>badge('GENT')+circle(12,52,6,G)+line('M12 58 V99 M10 78 H19',O,2),
 paper:()=>path('M-1 57 H21 L29 65 V101 H-1 Z','#e8f4f7')+line('M21 57 V65 H29 M4 72 H23 M4 78 H21 M4 84 H23','#7aa7c3',1.5)+path('M20 99 q-7 9 0 13 q7 -4 0 -13 Z',B,1.5)+badge('WET'),
 flesh:()=>rect(1,56,29,50,'#d5edf5',6)+rect(0,53,31,7,'#9aa0a6')+path('M7 78 Q9 62 19 75 Q28 78 22 92 Q11 99 7 86 Z','#e6a18f',1.5)+badge('FRESH'),
 ghost:()=>ghost(8,31)+badge('HAM')+path('M95 3 L99 -10 L108 -2 L118 -10 L121 5 Z',G,1.5),
 airspirit:()=>ghost(8,28)+book(98,65,'WS')+line('M-1 5 H24 Q33 5 29 -3 M98 21 H118 Q126 21 120 12','#6aa6c8',1.8),
 mist:()=>[4,15,27].map(y=>line(`M-1 ${y} Q15 ${y-9} 30 ${y} M94 ${y+17} Q109 ${y+8} 123 ${y+17}`,'#bdb2e6',2.2)).join('')+circle(108,87,10,G)+text(108,91,'£',12)+badge('MIST'),
 maiden:()=>masks(3)+badge('X')+path('M104 99 C92 91 97 80 104 86 C111 80 116 91 104 99 Z','#e98aa6',1.5),
 cast:()=>masks(9)+badge('IX'),
 battlefields:()=>[0,103].map((x,i)=>line(`M${x+4} 110 V54`,O,2)+path(`M${x+4} 55 h20 l-5 8 l5 8 h-20 Z`,i?'#3f5a8a':'#c0392b',1.5)).join('')+badge('IX')+line('M2 116 H30 M93 116 H123','#8a8f4a',2),
 emu:()=>path('M1 110 V58 Q1 40 11 42 Q24 43 17 55 L12 57 V82 L28 91 L24 103 H7 Z','#b58e5c',1.7)+circle(12,47,2,O)+line('M10 102 V117 M23 102 V117',O,2)+badge('EMU'),
 emeticEmu:()=>path('M1 108 V55 Q1 42 13 46 L22 51 L12 55 V81 L28 91 L23 104 H6 Z','#8a8f4a',1.7)+circle(11,49,1.5,O)+path('M94 99 H122 Q119 112 108 112 Q96 112 94 99 Z',B,1.8)+badge('E'),
 domino:()=>rect(-1,40,28,49,C)+line('M0 64 H26',O,1.5)+dots(5,47)+dots(5,70)+badge('101'),
 printedpaper:()=>path('M0 53 H20 L28 61 V102 H0 Z',C)+line('M20 53 V61 H28 M5 68 H23 M5 74 H23 M5 80 H23 M5 86 H23',O,1.5)+badge('PRINT'),
 horn:()=>path('M2 81 Q4 44 24 26 Q10 59 24 81 Z',C,1.8)+badge('HORN'),
 elephant:()=>path('M96 61 Q119 56 119 76 V103 Q119 114 108 109 L108 102 Q114 104 113 96 V80 Q97 88 94 76 Z','#9aa0a6',1.8)+el('ellipse',{cx:101,cy:74,rx:9,ry:12,fill:'#bdc3c9',stroke:O,'stroke-width':1.8})+circle(111,69,2,O)+badge('INK'),
};

Object.assign(motifs,{
 steamBirth:()=>steam()+badge('160')+circle(9,57,9,'#9aa0a6')+path('M2 68 H17 V88 H2 Z','#9aa0a6',1.5)+path('M100 29 q-9 -15 0 -20 q8 -15 17 -4 q13 3 6 18 Z','#e6edf2',1.3)+text(109,20,'M',8),
 powerState:()=>steam()+path('M46 78 H74 V89 Q60 104 46 89 Z','#3f5a8a',1.5)+text(60,90,'1000',8).replace(`fill="${O}"`,'fill="#fff"')+rect(97,47,26,31,C)+text(110,58,'US',9)+text(110,71,'POWER',5),
 powerMagnet:()=>steam()+badge('100 HP')+rect(1,82,28,21,'#9aa0a6')+text(15,96,'1000',7)+line('M106 36 V49 Q106 63 115 63 Q123 63 123 49 V36','#c0392b',6),
 coreHeart:()=>path('M102 91 C88 81 94 67 102 74 C112 67 118 81 102 91 Z','#e98aa6',1.8)+[0,1,2,3].map(i=>line(`M91 ${76+i*5} H114`,'#8b5e3c',1)).join('')+badge('M')+circle(10,22,7,G)+text(10,25,'N',8),
 magnetFriend:()=>badge('SOFT')+line('M3 50 V70 Q3 84 13 84 Q23 84 23 70 V50','#5b8fd6',6)+line('M103 50 V70 Q103 84 113 84 Q123 84 123 70 V50','#c0392b',6)+path('M17 98 C7 90 12 80 17 86 C24 80 30 91 17 98 Z','#e98aa6',1.3),
 magnetFamily:()=>badge('FAMILY')+[[-1,22],[103,22],[-1,78],[103,78]].map(([x,y],i)=>line(`M${x} ${y} V${y+17} Q${x} ${y+29} ${x+9} ${y+29} Q${x+18} ${y+29} ${x+18} ${y+17} V${y}`,i<2?'#c0392b':'#5b8fd6',4)+text(x+9,y+18,i<2?'P':'S',6)).join(''),
 navigator:()=>badge('40 HP')+path('M0 97 H31 L25 110 H6 Z','#8b5e3c',1.6)+rect(7,82,19,15,C)+rect(10,74,6,9,O)+steam()+line('M-1 116 q7 -4 14 0 t14 0','#6aa6c8',2),
 whiteSteam:()=>badge('WHITE')+path('M0 95 H30 V108 H0 Z','#9aa0a6',1.5)+rect(4,86,17,10,C)+circle(6,111,4,O)+circle(23,111,4,O)+steam()+rect(99,87,24,20,'#c98b4f')+circle(103,111,4,O)+circle(118,111,4,O),
 motiveSteam:()=>steam()+badge('HP')+circle(109,51,12,C)+line('M109 51 L116 42','#c0392b',2)+line('M109 70 V105 M104 77 L109 70 L114 77','#7c8288',2.3),
 london:()=>badge('LON')+rect(98,3,24,18,C)+text(110,15,'?',13),
 coatTune:()=>path('M39 76 L51 66 L60 77 L69 66 L81 76 V103 L67 97 L60 106 L53 97 L39 103 Z','#3f5a8a',1.5)+line('M104 14 V-4 L121 -8 V11',O,2.4)+el('ellipse',{cx:100,cy:15,rx:5,ry:3,fill:O})+el('ellipse',{cx:117,cy:12,rx:5,ry:3,fill:O})+text(15,21,'♪',22),
 soldPerson:()=>badge('SOLD')+path('M97 49 H121 V70 H97 L91 60 Z',C,1.6)+circle(97,60,2,O)+text(110,63,'£',12),
 clearance:()=>badge('£10')+line('M4 4 V110 M0 10 L4 4 L8 10 M0 104 L4 110 L8 104','#8a8f99',1.5)+text(16,57,'6′6',7)+line('M93 112 H122 M98 108 L93 112 L98 116 M117 108 L122 112 L117 116','#8a8f99',1.5)+rect(94,54,28,28,C)+text(108,66,'CLEAR',5.5)+text(108,76,'NOW',6),
 railwayLever:()=>badge('SCOTT')+line('M5 103 H28 M99 103 H121 M9 111 H29 M100 111 H119','#8a8f99',2)+line('M8 55 L22 95 M4 68 H26',O,3)+circle(19,87,6,G),
 clockHands:()=>circle(60,88,12,C)+line('M60 88 V79 M60 88 L68 91',O,2)+line('M1 17 H27 M100 17 H123 M13 4 V31 M112 4 V31','#8a8f99',1.5)+circle(13,17,9,C)+circle(112,17,9,C)+line('M13 17 L19 11 M112 17 L106 10',O,1.5),
 ringFinger:()=>badge('RING')+path('M100 106 V63 Q100 52 106 52 Q112 52 112 63 V107 Z',C,1.6)+el('ellipse',{cx:106,cy:80,rx:10,ry:5,fill:'none',stroke:G,'stroke-width':4})+circle(106,51,5,'#9aa0a6')+line('M106 46 V38',O,2),
 date:()=>rect(95,53,27,33,C)+rect(95,53,27,8,'#c0392b')+text(108,76,'DATE',6)+badge('HOUR')+circle(10,20,9,C)+line('M10 20 V13 M10 20 L15 22',O,1.5),
 roman:()=>badge('SPQR')+rect(96,55,26,34,C)+line('M101 63 H117 M101 68 H114 M101 73 H117',O,1.1)+circle(113,82,4,'#c0392b')+path('M2 27 V8 H10 V27 M15 27 V8 H23 V27',C,1.5),
 unknown:()=>badge('x')+rect(94,49,29,33,'#384752')+text(108,62,'x+y',8).replace(`fill="${O}"`,'fill="#fff"')+text(108,75,'= ?',9).replace(`fill="${O}"`,'fill="#fff"')+circle(11,18,10,B)+line('M1 18 H21 M11 8 V28',O,1),
 eternity:()=>badge('TIME')+text(13,19,'∞',28)+text(110,17,'∞',28)+line('M-1 45 Q15 30 29 45 M94 42 Q110 27 124 42','#bdb2e6',2),
});


Object.assign(motifs,{
 worldMagnet:()=>badge('WORLD')+circle(108,49,12,B)+line('M96 49 H120 M108 37 Q97 49 108 61 Q119 49 108 37',O,1.2)+line('M99 66 V78 Q99 93 109 93 Q119 93 119 78 V66','#c0392b',5)+line('M4 49 l13 -24 M3 25 l14 24',O,3),
 poleStar:()=>path('M105 -12 L109 -2 L120 2 L109 6 L105 17 L101 6 L90 2 L101 -2 Z','#f2c230',1.5)+badge('N')+line('M1 112 V33','#7c8288',2)+circle(1,32,4,G)+path('M99 91 Q108 80 121 91 Q109 86 99 91 Z',P,1),
 moon:()=>path('M17 -12 Q-2 2 17 18 Q-6 18 -6 2 Q-6 -12 17 -12 Z','#f2dca0',1.5)+badge('MOON')+circle(109,27,2,G)+circle(114,45,1.6,G)+circle(100,9,1.5,G),
 cheshireSteam:()=>steam()+badge('150 lb')+rect(97,64,25,31,C)+text(109,76,'150',8)+text(109,87,'STEAM',5)+line('M0 116 Q11 104 28 116','#5b8f4e',2),
 unknownPressure:()=>steam()+circle(109,45,13,C)+text(109,50,'?',16)+badge('100 HP')+rect(0,64,25,34,'#e6e1d6')+path('M-2 65 L12 50 L28 65 Z','#b5523b',1.4)+rect(8,82,9,16,'#8b5e3c'),
});

export function strengthEmblem(kind){return `<g data-strength-emblem="${kind}">${(motifs[kind]||motifs.gentleman)()}</g>`}

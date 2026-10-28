// Three approved additions, using the existing steam-man body and costume kit.
import {readFile, writeFile} from 'node:fs/promises';
import {robotSVG} from './robot.mjs';
const root = new URL('../', import.meta.url);
const choices = JSON.parse(await readFile(new URL('../../../runs/fresh-neuron-calibration-20261028/library_admissions.json', import.meta.url), 'utf8')).selected;
const O = '#2b2522';
const path = (d, fill, stroke = O, width = 1.8) => `<path d="${d}" fill="${fill}" stroke="${stroke}" stroke-width="${width}" stroke-linejoin="round" stroke-linecap="round"/>`;
const costumes = {
  'fresh06-up': {color:'sky', hat:'cap', left:'book', chest:[['monogram','9']], face:['blush']},
  'fresh06-down': {color:'ivory', hat:'bare', left:'razor', right:'mirror', face:['lather'], chest:['waistcoat']},
  'fresh02-up': {color:'lilac', hat:'bare', left:'mask', right:'setsquare', chest:[]},
};
const backgrounds = {
  'fresh06-up': path('M-1 113 L16 79 L33 113 Z', '#5b8f4e') + path('M86 113 L105 69 L123 113 Z', '#41414b') + path('M-1 57 L11 44 L24 57 Z', '#a86f3b') + '<rect x="3" y="57" width="18" height="21" rx="1" fill="#fffdf5" stroke="'+O+'" stroke-width="1.8"/><rect x="9" y="66" width="6" height="12" fill="#a86f3b"/>',
  'fresh06-down': path('M45 27 Q46 6 59 12 Q69 5 76 22 M50 21 Q51 8 58 13 M57 20 Q61 7 66 12 M65 21 Q69 10 74 21', 'none', '#8b5e3c', 3),
  'fresh02-up': path('M100 22 L116 31 L100 41 L84 31 Z', '#efe6d2') + path('M84 31 V50 L100 59 V41 Z', '#d6cab0') + path('M100 41 L116 31 V50 L100 59 Z', '#bdb2e6'),
};
const overlays = {
  'fresh06-up': '',
  'fresh06-down': '<g transform="translate(2 12) rotate(-18 10 10)"><rect x="0" y="0" width="20" height="6" rx="2" fill="#e2a83e" stroke="'+O+'" stroke-width="1.5"/>' + [2,6,10,14,18].map(x=>path(`M${x} 5 V15`, 'none', O, 1.8)).join('') + '</g>',
  'fresh02-up': path('M60 78 A9 9 0 0 0 60 96 Z', '#e2a83e') + path('M60 78 H69 V96 H60 Z', '#8fc7e8') + path('M60 78 V96', 'none', O, 1.5),
};
const positions = {'fresh06-up':'29-613-up', 'fresh06-down':'29-613-down', 'fresh02-up':'16-1575-up'};
const xml = s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const index = {};
for (const choice of choices) {
  const id = choice.id;
  let svg = robotSVG(costumes[id]);
  svg = svg.replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -30 128 152">', `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -30 128 152" role="img" aria-label="${xml(choice.name)}"><title>${xml(choice.name)}</title>${backgrounds[id]}`);
  svg = svg.replace('</svg>', overlays[id]+'</svg>');
  if (/NaN|undefined/.test(svg)) throw Error('Invalid robot '+id);
  const file = `icons/${positions[id]}.svg`;
  await writeFile(new URL('dist/'+file, root), svg);
  index[id] = file;
}
await writeFile(new URL('dist/icons/fresh-calibration-index.json',root), JSON.stringify(index,null,2)+'\n');
await writeFile(new URL('icons/fresh-calibration-costumes.json',root), JSON.stringify(costumes,null,2)+'\n');
console.log('Created three matching steam-man icons.');

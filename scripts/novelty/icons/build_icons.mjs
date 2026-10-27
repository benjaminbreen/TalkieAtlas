// Write dist/icons/<slug>.svg for every costumed persona, plus design/robot-zoo.html to review them.
// Usage: node icons/build_icons.mjs
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { robotSVG } from "./robot.mjs";

const root = new URL("../", import.meta.url);
const costumes = JSON.parse(await readFile(new URL("icons/costumes.json", root), "utf8"));
const data = JSON.parse(await readFile(new URL("dist/site.json", root), "utf8"));
const byId = new Map([...data.singles, ...data.pairs].map(r => [r.id, r]));
const dir = sign => (sign > 0 ? "up" : "down");
const slug = r => r.slug || (r.kind === "pair" ? r.parents.map(id => slug(byId.get(id))).join("_") : `${r.layer}-${r.neuron}-${dir(r.sign)}`);
const path = r => `${r.kind === "pair" ? "p" : "n"}/${slug(r)}`;
const rows = new Map([...data.singles, ...data.pairs].filter(r=>r.canonical!==false).map(r => [path(r), r]));
export const iconFile = key => (key.startsWith("p/") ? "p-" : "") + key.slice(2) + ".svg";

await mkdir(new URL("dist/icons/", root), { recursive: true });
const cards = [];
for (const [key, costume] of Object.entries(costumes)) {
  const r = rows.get(key);
  if (!r) throw Error(`No reply for ${key}`);
  await writeFile(new URL(`dist/icons/${iconFile(key)}`, root), robotSVG(costume));
  const code = r.kind === "pair" ? r.parents.map(id => { const p = byId.get(id); return `L${p.layer} N${p.neuron} ${p.sign > 0 ? "+" : "−"}`; }).join(" + ") : `L${r.layer} N${r.neuron} ${r.sign > 0 ? "+" : "−"}`;
  cards.push(`<div class="card"><img src="../dist/icons/${iconFile(key)}" alt=""><b>${r.judge.name}</b><code>${code}</code></div>`);
}
await writeFile(new URL("design/robot-zoo.html", root), `<!doctype html><meta charset="utf-8"><title>Talkie robot zoo</title>
<style>body{margin:0;padding:40px;width:1400px;font:14px -apple-system,sans-serif;color:#1d1d1f;background:#fff}h1{font-size:30px;margin:0 0 20px}
.grid{display:grid;grid-template-columns:repeat(10,1fr);gap:10px}.card{border:1px solid #e8e8ed;border-radius:14px;padding:8px 6px 10px;text-align:center;background:#fafafb}
img{width:100%;aspect-ratio:128/152;display:block}b{display:block;font-size:12px;line-height:1.2;margin-top:2px}code{font:10px ui-monospace,monospace;color:#86868b}</style>
<h1>Talkie robot zoo · ${cards.length}</h1><div class="grid">${cards.join("")}</div>`);
console.log(`wrote ${cards.length} icons`);

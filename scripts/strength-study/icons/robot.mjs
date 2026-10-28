// The Talkie steam man: one fixed body (after the Steam Man of the Prairies, 1868)
// plus a kit of hats, hand-held things, chest pieces, faces and backdrops.
// robotSVG(costume) returns a self-contained SVG string. See costumes.json.

const O = "#2b2522", SW = 3, FACE = "#2b2a33", EYE = "#f6efe2", BRASS = "#e2a83e", CREAM = "#f6efe2", GOLD = "#f2c230", RED = "#c0392b", INK = "#2b2522";
const s = (tag, a, inner = "") => `<${tag} ${Object.entries(a).map(([k, v]) => `${k}="${v}"`).join(" ")}>${inner}</${tag}>`;
const ol = { stroke: O, "stroke-width": SW, "stroke-linejoin": "round", "stroke-linecap": "round" };
const thin = { ...ol, "stroke-width": 2.4 };
const line = (d, color = O, w = SW) => s("path", { d, fill: "none", stroke: color, "stroke-width": w, "stroke-linecap": "round", "stroke-linejoin": "round" });
const star = (x, y, r, fill = O) => s("path", { d: `M${x} ${y - r} Q${x} ${y} ${x + r} ${y} Q${x} ${y} ${x} ${y + r} Q${x} ${y} ${x - r} ${y} Q${x} ${y} ${x} ${y - r} Z`, fill });

export const PALETTES = {
  brass: ["#c98b4f", "#a86f3b"], lilac: ["#ddd6f3", "#bdb2e6"], slate: ["#4f7f8c", "#3d6570"], crimson: ["#c4473a", "#9a3229"],
  teal: ["#3aa39a", "#2c7e77"], navy: ["#3f5a8a", "#2f4570"], black: ["#55555e", "#3e3e46"], green: ["#5b8f4e", "#46733b"],
  gold: ["#e0b04a", "#b88a2e"], tan: ["#d8b07a", "#b58e5c"], blue: ["#5b8fd6", "#4572b3"], plum: ["#8c5a8f", "#6e4470"],
  grey: ["#9aa0a6", "#7c8288"], olive: ["#8a8f4a", "#6d7238"], pink: ["#e98aa6", "#c96b88"], sky: ["#8fc7e8", "#6aa6c8"],
  brown: ["#8b5e3c", "#6e4529"], ivory: ["#efe6d2", "#d6cab0"],
};

// Where each hat's top is, so halos and crests can sit on it.
const HAT_TOP = { chimney: 5, topper: 0, crown: 4, bicorne: 6, shako: -8, mortarboard: 6, strawhat: 8, bowler: 6, wig: 18, bonnet: 6, beret: 13,
  sailor: 13, cap: 12, shovel: 10, turban: 6, ears: 10, roof: 4, capotain: 0, bare: 20, fez: 8, jester: 2, firehelmet: 4, ushanka: 8, biretta: 2 };

const HATS = {
  chimney: () => s("rect", { x: 43, y: 21, width: 34, height: 6, rx: 3, fill: O }) + s("rect", { x: 50, y: 5, width: 20, height: 18, rx: 2, fill: O }) + s("rect", { x: 50, y: 15, width: 20, height: 4, fill: BRASS })
    + s("circle", { cx: 79, cy: 3, r: 4, fill: "#fff", stroke: "#c9c9cf", "stroke-width": 2 }) + s("circle", { cx: 87, cy: -3, r: 3, fill: "#fff", stroke: "#c9c9cf", "stroke-width": 2 }),
  topper: () => s("rect", { x: 47, y: 0, width: 26, height: 22, rx: 2, fill: O }) + s("rect", { x: 47, y: 14, width: 26, height: 4, fill: RED }) + s("rect", { x: 41, y: 20, width: 38, height: 6, rx: 3, fill: O }),
  crown: () => s("path", { d: "M40 27 L41 7 L51 17 L60 4 L69 17 L79 7 L80 27 Z", fill: GOLD, ...ol }) + [[60, 19], [47, 22], [73, 22]].map(([x, y]) => s("circle", { cx: x, cy: y, r: 2.6, fill: RED })).join(""),
  bicorne: () => s("path", { d: "M26 25 Q60 -14 94 25 Q60 15 26 25 Z", fill: O, ...ol }) + s("circle", { cx: 60, cy: 13, r: 5, fill: "#2f5fb3" }) + s("circle", { cx: 60, cy: 13, r: 3.2, fill: "#fff" }) + s("circle", { cx: 60, cy: 13, r: 1.6, fill: RED }),
  shako: () => s("ellipse", { cx: 60, cy: -4, rx: 3.5, ry: 7, fill: "#fff", ...thin }) + s("path", { d: "M46 25 L48 2 L72 2 L74 25 Z", fill: O, ...ol }) + s("path", { d: "M60 9 l5 6 l-5 6 l-5 -6 Z", fill: GOLD })
    + s("path", { d: "M43 25 H77 L72 30 H48 Z", fill: O, ...ol }),
  mortarboard: () => s("path", { d: "M42 27 Q60 10 78 27 Z", fill: O, ...ol }) + s("path", { d: "M32 15 L60 6 L88 15 L60 24 Z", fill: O, ...ol }) + line("M60 15 L84 18 L85 30", GOLD, 2.4) + s("circle", { cx: 85, cy: 31, r: 2.5, fill: GOLD }),
  strawhat: () => s("rect", { x: 46, y: 8, width: 28, height: 17, rx: 6, fill: "#e9c46a", ...ol }) + s("rect", { x: 46, y: 16, width: 28, height: 4, fill: RED }) + s("ellipse", { cx: 60, cy: 25, rx: 31, ry: 5, fill: "#e9c46a", ...ol }),
  bowler: () => s("path", { d: "M43 25 Q43 6 60 6 Q77 6 77 25 Z", fill: O, ...ol }) + s("ellipse", { cx: 60, cy: 25, rx: 23, ry: 3.5, fill: O, ...ol }),
  wig: () => [30, 38, 46, 54].map(y => s("circle", { cx: 33, cy: y, r: 5, fill: "#f4f1ea", ...thin }) + s("circle", { cx: 87, cy: y, r: 5, fill: "#f4f1ea", ...thin })).join("")
    + s("path", { d: "M35 33 Q35 18 60 18 Q85 18 85 33 Q72 26 60 26 Q48 26 35 33 Z", fill: "#f4f1ea", ...thin }),
  bonnet: () => s("ellipse", { cx: 60, cy: 19, rx: 25, ry: 8, fill: "#2f4570", ...ol }) + s("rect", { x: 40, y: 20, width: 40, height: 6, fill: RED, ...thin }) + line("M44 23 H76", "#2e7d4f", 2) + s("circle", { cx: 60, cy: 10, r: 4.5, fill: RED, ...thin }),
  beret: () => s("ellipse", { cx: 57, cy: 22, rx: 26, ry: 8, fill: "#2f3550", ...ol }) + line("M58 14 V10", O, 3),
  sailor: () => s("rect", { x: 42, y: 13, width: 36, height: 12, rx: 5, fill: "#fff", ...ol }) + s("rect", { x: 42, y: 20, width: 36, height: 5, fill: "#2f4570" }) + line("M78 22 l8 8 M78 22 l4 10", "#2f4570", 2.4),
  cap: () => s("path", { d: "M38 27 Q40 12 62 12 Q80 13 82 25 Z", fill: "#7a6a55", ...ol }) + s("path", { d: "M70 25 Q88 24 93 29 L72 29 Z", fill: "#5e5141", ...ol }),
  shovel: () => s("path", { d: "M46 21 Q48 9 60 9 Q72 9 74 21 Z", fill: O, ...ol }) + s("path", { d: "M28 25 Q34 17 42 21 Q60 24 78 21 Q86 17 92 25 Q60 32 28 25 Z", fill: O, ...ol }),
  turban: () => s("path", { d: "M37 29 Q34 6 60 6 Q86 6 83 29 Z", fill: "#f4f1ea", ...ol }) + line("M40 20 Q60 12 80 22 M39 26 Q60 17 82 27", "#d6cab0", 2) + s("circle", { cx: 60, cy: 17, r: 3.2, fill: RED, ...thin }),
  ears: () => s("path", { d: "M40 30 L42 10 L52 26 Z M80 30 L78 10 L68 26 Z", fill: "#6e4529", ...ol }) + s("path", { d: "M44 26 L44 16 L49 24 Z M76 26 L76 16 L71 24 Z", fill: "#e98aa6" })
    + s("path", { d: "M54 26 Q56 12 64 14 Q60 18 66 18 Q62 22 66 26 Z", fill: O }),
  roof: () => s("rect", { x: 72, y: 4, width: 7, height: 14, fill: "#9a3229", ...thin }) + s("path", { d: "M32 29 L60 4 L88 29 Z", fill: "#b5523b", ...ol }) + line("M42 20 H78 M48 14 H72", "#9a3229", 2)
    + s("circle", { cx: 82, cy: -2, r: 3.5, fill: "#fff", stroke: "#c9c9cf", "stroke-width": 2 }),
  capotain: () => s("path", { d: "M46 23 L49 0 L71 0 L74 23 Z", fill: O, ...ol }) + s("rect", { x: 48, y: 14, width: 24, height: 5, fill: "#6e4529" }) + s("rect", { x: 56, y: 13, width: 8, height: 7, fill: "none", stroke: GOLD, "stroke-width": 2 })
    + s("rect", { x: 38, y: 21, width: 44, height: 6, rx: 3, fill: O }),
  bare: () => s("rect", { x: 56, y: 20, width: 8, height: 7, rx: 1, fill: BRASS, ...thin }),
  fez: () => s("path", { d: "M46 27 L49 8 L71 8 L74 27 Z", fill: "#b8342a", ...ol }) + line("M60 8 Q68 6 69 18", O, 1.6) + s("circle", { cx: 69, cy: 20, r: 2.4, fill: GOLD }),
  jester: () => s("path", { d: "M38 28 Q38 12 58 12 Q46 0 26 4 Q34 12 38 28 Z", fill: RED, ...ol }) + s("path", { d: "M82 28 Q82 12 62 12 Q74 0 94 4 Q86 12 82 28 Z", fill: "#2f5fb3", ...ol })
    + s("path", { d: "M36 30 Q60 20 84 30 V25 Q60 15 36 25 Z", fill: GOLD, ...thin }) + s("circle", { cx: 26, cy: 4, r: 3.6, fill: GOLD, ...thin }) + s("circle", { cx: 94, cy: 4, r: 3.6, fill: GOLD, ...thin }),
  firehelmet: () => s("path", { d: "M38 28 Q38 6 60 6 Q82 6 82 28 Z", fill: BRASS, ...ol }) + line("M60 6 Q60 0 66 -2", O, 3) + s("path", { d: "M28 28 Q60 34 94 28 L96 32 Q60 40 24 32 Z", fill: "#b88a2e", ...ol })
    + s("path", { d: "M54 12 H66 V22 Q60 26 54 22 Z", fill: RED, ...thin }),
  biretta: () => s("path", { d: "M40 27 L42 10 Q60 4 78 10 L80 27 Z", fill: "#b8342a", ...ol }) + line("M50 10 V24 M60 7 V24 M70 10 V24", "#8a2a22", 2) + s("circle", { cx: 60, cy: 4, r: 4, fill: "#8a2a22", ...thin }),
  ushanka: () => s("rect", { x: 31, y: 24, width: 10, height: 20, rx: 5, fill: "#a07850", ...thin }) + s("rect", { x: 79, y: 24, width: 10, height: 20, rx: 5, fill: "#a07850", ...thin })
    + s("path", { d: "M38 26 Q38 8 60 8 Q82 8 82 26 Z", fill: "#6e4529", ...ol }) + s("rect", { x: 35, y: 19, width: 50, height: 10, rx: 5, fill: "#a07850", ...ol }),
};

const FACES = {
  mustache: (c = "#8a5a2b") => s("path", { d: "M60 46 Q53 42 47 46 Q44 49 41 46 Q44 52 52 50 Q57 49 60 47 Q63 49 68 50 Q76 52 79 46 Q76 49 73 46 Q67 42 60 46 Z", fill: c, stroke: O, "stroke-width": 1.6 }),
  beard: (c = "#e3ddd0") => s("path", { d: "M40 44 Q42 66 60 70 Q78 66 80 44 Q72 54 60 54 Q48 54 40 44 Z", fill: c, ...thin }),
  monocle: () => s("circle", { cx: 68.5, cy: 41, r: 7.5, fill: "none", stroke: GOLD, "stroke-width": 2.4 }) + line("M74 46 Q80 54 79 60", GOLD, 1.6),
  spectacles: () => s("circle", { cx: 51.5, cy: 41, r: 7, fill: "none", stroke: GOLD, "stroke-width": 2.2 }) + s("circle", { cx: 68.5, cy: 41, r: 7, fill: "none", stroke: GOLD, "stroke-width": 2.2 }) + line("M58.5 40 H61.5", GOLD, 2),
  lather: () => s("path", { d: "M41 46 Q38 58 46 60 Q48 66 56 63 Q60 68 64 63 Q72 66 74 60 Q82 58 79 46 Q72 54 60 54 Q48 54 41 46 Z", fill: "#fff", ...thin }) + s("circle", { cx: 84, cy: 52, r: 2.5, fill: "#fff", stroke: "#c9c9cf", "stroke-width": 1.2 }),
  tear: () => s("path", { d: "M49 47 Q46 52 49 54 Q52 52 49 47 Z", fill: "#7cc4ef" }),
  blush: () => s("ellipse", { cx: 45, cy: 48, rx: 3.5, ry: 2.2, fill: "#f08aa6", opacity: .85 }) + s("ellipse", { cx: 75, cy: 48, rx: 3.5, ry: 2.2, fill: "#f08aa6", opacity: .85 }),
  beak: () => s("path", { d: "M56 47 L64 47 L60 54 Z", fill: "#f5c542", ...thin }) + s("ellipse", { cx: 60, cy: 46.5, rx: 5, ry: 3, fill: "#d9342b", ...thin }),
};

// Things worn on the neck or chest. Those in COVERS_GAUGE replace the pressure gauge.
const COVERS_GAUGE = new Set(["unionjack", "heart", "monogram", "apron", "waistcoat", "stripes"]);
const CHEST = {
  stripes: () => s("path", { d: "M35 78 H85 V82 H35 Z M35 86 H85 V90 H35 Z M37 94 H83 V98 H37 Z", fill: "#3e3e46" }) + s("rect", { x: 49, y: 80, width: 22, height: 9, rx: 1.5, fill: "#fff", ...thin })
    + s("text", { x: 60, y: 87.5, "text-anchor": "middle", "font-family": "ui-monospace, monospace", "font-size": 7.5, "font-weight": 700, fill: O }, "No.9"),
  ruff: () => s("path", { d: "M36 58 L40 65 L45 58 L49 66 L54 58 L58 66 L62 58 L66 66 L71 58 L75 66 L80 58 L84 65 L84 60 Q60 52 36 60 Z", fill: "#fff", ...thin }),
  cross: () => line("M45 77 V93 M39.5 82 H50.5", GOLD, 3.4),
  chain: () => line("M40 60 Q60 80 80 60", GOLD, 4.5).replace('stroke-linecap="round"', 'stroke-linecap="round" stroke-dasharray="2.5 3.2"') + s("circle", { cx: 60, cy: 72, r: 6.5, fill: GOLD, ...thin }) + star(60, 72, 3.4, "#9a3229"),
  bands: () => s("path", { d: "M55 58 H59.5 V72 H55 Z M60.5 58 H65 V72 H60.5 Z", fill: "#fff", ...thin }),
  stethoscope: () => line("M47 57 Q44 74 56 77 Q66 79 64 84", "#55606a", 2.6) + line("M73 57 Q75 66 70 72", "#55606a", 2.6) + s("circle", { cx: 64, cy: 87, r: 4, fill: "#c9ced3", ...thin }),
  medal: () => [[44, RED], [52, "#2f5fb3"]].map(([x, c]) => s("rect", { x: x - 3, y: 77, width: 6, height: 7, fill: c, ...thin }) + s("circle", { cx: x, cy: 87, r: 3.6, fill: GOLD, ...thin })).join(""),
  sash: (c = "#2f5fb3") => s("path", { d: "M36 63 L44 58 L86 91 L80 99 Z", fill: c, ...thin }),
  tartan: () => s("path", { d: "M36 63 L44 58 L86 91 L80 99 Z", fill: RED, ...thin }) + line("M40 61 L83 95", "#2e7d4f", 2.5) + line("M38 66 L80 99 M44 59 L86 92", "#f2c230", .9),
  apron: (c = "#f4f1ea") => s("path", { d: "M40 77 H80 V100 Q60 104 40 100 Z", fill: c, ...thin }) + s("rect", { x: 53, y: 84, width: 14, height: 9, rx: 1.5, fill: "none", stroke: O, "stroke-width": 1.8 }),
  waistcoat: (c = "#b88a2e") => s("path", { d: "M44 60 L60 80 L76 60 L80 99 H40 Z", fill: c, ...thin }) + [86, 93].map(y => s("circle", { cx: 60, cy: y, r: 1.8, fill: O })).join("") + line("M60 88 Q67 93 74 88", GOLD, 1.6),
  unionjack: () => s("rect", { x: 43, y: 78, width: 34, height: 19, rx: 2, fill: "#2f4570", ...thin }) + line("M43 78 L77 97 M77 78 L43 97", "#fff", 4) + line("M43 78 L77 97 M77 78 L43 97", RED, 1.5)
    + line("M60 78 V97 M43 87.5 H77", "#fff", 6) + line("M60 78 V97 M43 87.5 H77", RED, 3),
  rosette: () => s("circle", { cx: 45, cy: 83, r: 6.5, fill: "#2f5fb3", ...thin }) + s("circle", { cx: 45, cy: 83, r: 3, fill: "#fff" }) + s("path", { d: "M42 88 L40 97 L43.5 95 M48 88 L50 97 L46.5 95", fill: "#2f5fb3", stroke: O, "stroke-width": 1.4 }),
  heart: () => s("path", { d: "M60 96 C46 86 50 76 56 78 Q59 79 60 82 Q61 79 64 78 C70 76 74 86 60 96 Z", fill: "#e5484d", ...thin }),
  monogram: (t = "E") => s("circle", { cx: 60, cy: 87, r: 9, fill: GOLD, ...thin }) + s("text", { x: 60, y: 91.5, "text-anchor": "middle", "font-family": "Georgia, serif", "font-size": 13, "font-weight": 700, fill: O }, t),
};

// Hand-held things, drawn for the right hand (grip at x, y). Left-hand ones are mirrored.
const HAND = {
  razor: (x, y) => s("rect", { x: x - 2, y: y - 14, width: 6, height: 20, rx: 2, fill: "#2b2522" }) + s("path", { d: `M${x + 1} ${y - 14} L${x + 3} ${y - 36} L${x + 12} ${y - 34} L${x + 5} ${y - 14} Z`, fill: "#e4e8ec", ...thin }),
  oar: (x, y) => line(`M${x - 2} ${y + 16} L${x + 10} ${y - 30}`, "#a8784f", 3.5) + s("path", { d: `M${x + 8} ${y - 26} Q${x + 6} ${y - 46} ${x + 14} ${y - 50} Q${x + 20} ${y - 46} ${x + 14} ${y - 26} Z`, fill: "#c9935f", ...thin }),
  rattle: (x, y) => line(`M${x} ${y + 6} L${x + 4} ${y - 18}`, "#e98aa6", 3.5) + s("circle", { cx: x + 6, cy: y - 25, r: 9, fill: "#8fc7e8", ...thin }) + s("circle", { cx: x + 3, cy: y - 27, r: 2, fill: "#fff" }) + star(x + 18, y - 34, 3, GOLD),
  ingot: (x, y) => [[0, 0], [12, 0], [6, -9]].map(([dx, dy]) => s("path", { d: `M${x - 4 + dx} ${y + 4 + dy} L${x - 1 + dx} ${y - 4 + dy} H${x + 9 + dx} L${x + 12 + dx} ${y + 4 + dy} Z`, fill: GOLD, ...thin })).join(""),
  magnet: (x, y) => s("path", { d: `M${x - 4} ${y - 38} V${y - 16} Q${x - 4} ${y} ${x + 8} ${y} Q${x + 20} ${y} ${x + 20} ${y - 16} V${y - 38}`, fill: "none", stroke: O, "stroke-width": 10.5 })
    + s("path", { d: `M${x - 4} ${y - 38} V${y - 16} Q${x - 4} ${y} ${x + 8} ${y} Q${x + 20} ${y} ${x + 20} ${y - 16} V${y - 38}`, fill: "none", stroke: RED, "stroke-width": 6.5 })
    + s("rect", { x: x - 8, y: y - 46, width: 8, height: 9, fill: "#c9ced3", ...thin }) + s("rect", { x: x + 16, y: y - 46, width: 8, height: 9, fill: "#c9ced3", ...thin }),
  saw: (x, y) => s("path", { d: `M${x + 2} ${y - 6} L${x + 4} ${y - 46} L${x + 15} ${y - 43} L${x + 10} ${y - 6} Z`, fill: "#d5d9de", ...thin })
    + line(`M${x + 15} ${y - 43} l-2 4 l2 3 l-2 4 l2 3 l-2 4 l2 3 l-2 4 l2 3 l-2 4`, O, 1.2) + s("rect", { x: x - 4, y: y - 8, width: 16, height: 12, rx: 4, fill: "#8b5e3c", ...thin }),
  whip: (x, y) => line(`M${x} ${y + 8} L${x + 6} ${y - 30}`, "#6e4529", 3.5) + line(`M${x + 6} ${y - 30} Q${x + 24} ${y - 46} ${x + 28} ${y - 22} Q${x + 30} ${y - 8} ${x + 21} ${y - 6}`, O, 1.6),
  torch: (x, y) => line(`M${x} ${y + 8} L${x + 5} ${y - 24}`, "#8b5e3c", 5) + s("path", { d: `M${x + 6} ${y - 22} Q${x - 6} ${y - 32} ${x + 3} ${y - 50} Q${x + 6} ${y - 38} ${x + 12} ${y - 46} Q${x + 20} ${y - 30} ${x + 6} ${y - 22} Z`, fill: "#f39c12", ...thin })
    + s("path", { d: `M${x + 6} ${y - 25} Q${x + 1} ${y - 31} ${x + 5} ${y - 39} Q${x + 8} ${y - 33} ${x + 11} ${y - 35} Q${x + 13} ${y - 28} ${x + 6} ${y - 25} Z`, fill: "#ffd84d" }),
  rod: (x, y) => line(`M${x} ${y + 8} L${x + 20} ${y - 46}`, "#8b5e3c", 2.8) + line(`M${x + 20} ${y - 46} Q${x + 28} ${y - 30} ${x + 27} ${y - 6}`, "#7c8288", 1.1) + line(`M${x + 27} ${y - 6} q0 4 -3 3`, O, 1.4),
  axe: (x, y) => line(`M${x} ${y + 14} L${x + 8} ${y - 34}`, RED, 4) + s("path", { d: `M${x + 5} ${y - 30} Q${x + 22} ${y - 42} ${x + 23} ${y - 22} Q${x + 15} ${y - 26} ${x + 7} ${y - 20} Z`, fill: "#c9ced3", ...thin }),
  setsquare: (x, y) => s("path", { d: `M${x - 2} ${y + 6} L${x - 2} ${y - 30} L${x + 22} ${y + 6} Z`, fill: CREAM, ...thin }) + s("path", { d: `M${x + 4} ${y} L${x + 4} ${y - 12} L${x + 12} ${y} Z`, fill: "#fafafb", stroke: O, "stroke-width": 2 })
    + line(`M${x - 2} ${y - 1} h6 v7`, RED, 2) + [0, 1, 2, 3, 4].map(i => line(`M${x - 2} ${y - 26 + i * 6} h4`, O, 1.8)).join(""),
  dividers: (x, y) => line(`M${x + 6} ${y - 34} L${x - 2} ${y + 10} M${x + 6} ${y - 34} L${x + 16} ${y + 8}`, "#8a8f99", 3) + s("circle", { cx: x + 6, cy: y - 34, r: 3.5, fill: GOLD, ...thin }),
  mirror: (x, y) => line(`M${x} ${y + 2} L${x + 6} ${y - 10}`, O, 4.5) + s("ellipse", { cx: x + 9, cy: y - 19, rx: 8, ry: 10, fill: "#cfe8f3", ...thin }) + line(`M${x + 6} ${y - 24} l4 -3`, "#fff", 2.4) + star(x + 20, y - 30, 3.5, GOLD),
  broom: (x, y) => line(`M${x - 2} ${y - 30} L${x + 6} ${y + 10}`, "#8b5e3c", 4) + s("path", { d: `M${x - 1} ${y + 9} L${x + 13} ${y + 7} L${x + 19} ${y + 22} L${x - 3} ${y + 25} Z`, fill: "#e9c46a", ...thin }) + line(`M${x + 3} ${y + 12} L${x + 3} ${y + 23} M${x + 9} ${y + 11} L${x + 10} ${y + 22}`, "#b58e5c", 1.5),
  book: (x, y, c = "#2f3550") => s("rect", { x: x - 3, y: y - 28, width: 21, height: 26, rx: 2, fill: c, ...thin }) + line(`M${x + 15} ${y - 26} V${y - 4}`, CREAM, 2) + line(`M${x + 6.5} ${y - 22} V${y - 10} M${x + 2.5} ${y - 18} H${x + 10.5}`, GOLD, 2),
  ledger: (x, y) => s("rect", { x: x - 3, y: y - 28, width: 21, height: 26, rx: 2, fill: "#2e7d4f", ...thin }) + s("rect", { x: x + 1, y: y - 23, width: 13, height: 7, fill: CREAM }) + line(`M${x + 15} ${y - 26} V${y - 4}`, CREAM, 2),
  quill: (x, y) => s("path", { d: `M${x + 1} ${y + 4} Q${x + 2} ${y - 24} ${x + 20} ${y - 38} Q${x + 14} ${y - 16} ${x + 1} ${y + 4} Z`, fill: "#fff", ...thin }) + line(`M${x + 1} ${y + 4} Q${x + 8} ${y - 18} ${x + 18} ${y - 34}`, O, 1.4),
  scroll: (x, y) => s("rect", { x: x - 1, y: y - 30, width: 17, height: 26, fill: CREAM, ...thin }) + s("rect", { x: x - 4, y: y - 33, width: 23, height: 5, rx: 2.5, fill: "#d6cab0", ...thin }) + s("rect", { x: x - 4, y: y - 7, width: 23, height: 5, rx: 2.5, fill: "#d6cab0", ...thin })
    + line(`M${x + 3} ${y - 23} H${x + 12} M${x + 3} ${y - 18} H${x + 12} M${x + 3} ${y - 13} H${x + 9}`, "#8a8f99", 1.5),
  cane: (x, y) => line(`M${x} ${y - 10} Q${x} ${y - 18} ${x + 7} ${y - 18} Q${x + 13} ${y - 18} ${x + 13} ${y - 12}`, O, 3.5) + line(`M${x} ${y - 10} L${x + 3} ${y + 21}`, O, 3.5),
  umbrella: (x, y) => line(`M${x + 2} ${y - 12} Q${x - 4} ${y - 12} ${x - 4} ${y - 6}`, O, 3) + s("path", { d: `M${x + 2} ${y - 4} L${x + 9} ${y + 14} L${x + 4} ${y + 20} L${x - 3} ${y + 14} Z`, fill: O }) + line(`M${x + 2} ${y - 12} L${x + 4} ${y + 22}`, O, 2.5),
  musket: (x, y) => line(`M${x - 3} ${y + 18} L${x + 3} ${y - 6}`, "#8b5e3c", 6) + line(`M${x + 3} ${y - 6} L${x + 10} ${y - 38}`, "#8a8f99", 3.2) + line(`M${x + 10} ${y - 38} L${x + 12} ${y - 48}`, "#c9ced3", 2),
  sword: (x, y) => line(`M${x + 2} ${y - 4} L${x + 12} ${y - 42}`, "#c9ced3", 4) + line(`M${x - 5} ${y - 7} L${x + 9} ${y - 3}`, GOLD, 3.5),
  pitchfork: (x, y) => line(`M${x} ${y + 20} L${x + 7} ${y - 26}`, "#8b5e3c", 3.5) + line(`M${x + 1} ${y - 26} L${x + 13} ${y - 24} M${x + 1} ${y - 26} L${x} ${y - 40} M${x + 7} ${y - 25} L${x + 7} ${y - 40} M${x + 13} ${y - 24} L${x + 14} ${y - 39}`, "#8a8f99", 2.6),
  moneybag: (x, y) => s("path", { d: `M${x + 4} ${y - 14} Q${x - 8} ${y - 2} ${x + 2} ${y + 6} H${x + 20} Q${x + 30} ${y - 2} ${x + 18} ${y - 14} Z`, fill: "#d8b07a", ...thin }) + s("path", { d: `M${x + 4} ${y - 14} L${x + 1} ${y - 21} L${x + 11} ${y - 17} L${x + 21} ${y - 21} L${x + 18} ${y - 14}`, fill: "#d8b07a", ...thin })
    + s("text", { x: x + 11, y: y + 2, "text-anchor": "middle", "font-family": "Georgia, serif", "font-size": 12, "font-weight": 700, fill: O }, "£"),
  fish: (x, y) => s("ellipse", { cx: x + 6, cy: y - 22, rx: 7, ry: 16, fill: "#8fb3c4", ...thin }) + s("path", { d: `M${x + 6} ${y - 7} L${x} ${y + 2} L${x + 12} ${y + 2} Z`, fill: "#8fb3c4", ...thin }) + s("circle", { cx: x + 6, cy: y - 32, r: 1.8, fill: O }),
  teacup: (x, y) => s("path", { d: `M${x - 1} ${y - 12} H${x + 17} Q${x + 16} ${y - 1} ${x + 8} ${y - 1} Q${x} ${y - 1} ${x - 1} ${y - 12} Z`, fill: "#fff", ...thin }) + s("ellipse", { cx: x + 8, cy: y, rx: 12, ry: 2.5, fill: "#fff", ...thin })
    + line(`M${x + 17} ${y - 10} q5 0 4 4 q-1 3 -5 2`, O, 2) + line(`M${x + 5} ${y - 17} q-2 -4 1 -7 M${x + 11} ${y - 17} q-2 -4 1 -7`, "#c9c9cf", 2),
  wineglass: (x, y) => s("path", { d: `M${x} ${y - 26} H${x + 16} Q${x + 16} ${y - 12} ${x + 8} ${y - 12} Q${x} ${y - 12} ${x} ${y - 26} Z`, fill: "#e8eef2", ...thin }) + s("path", { d: `M${x + 1} ${y - 20} H${x + 15} Q${x + 14} ${y - 13} ${x + 8} ${y - 13} Q${x + 2} ${y - 13} ${x + 1} ${y - 20} Z`, fill: "#8e1b3b" })
    + line(`M${x + 8} ${y - 12} V${y - 1} M${x + 3} ${y} H${x + 13}`, O, 2.4),
  wheat: (x, y) => [-7, 0, 7].map(d => line(`M${x + 4} ${y + 4} L${x + 4 + d} ${y - 30}`, "#b88a2e", 2) + [0, 1, 2].map(i => s("ellipse", { cx: x + 4 + d * (1 - i * .12), cy: y - 30 + i * 5, rx: 2.4, ry: 3.6, fill: "#e9c46a", stroke: "#b88a2e", "stroke-width": 1 })).join("")).join("")
    + s("rect", { x: x - 1, y: y - 10, width: 10, height: 4, fill: RED }),
  shuttle: (x, y) => s("path", { d: `M${x - 8} ${y - 8} Q${x + 8} ${y - 18} ${x + 26} ${y - 8} Q${x + 8} ${y + 2} ${x - 8} ${y - 8} Z`, fill: "#c98b4f", ...thin }) + s("rect", { x: x + 3, y: y - 11, width: 12, height: 6, rx: 2, fill: "#d9342b" }),
  newspaper: (x, y) => s("rect", { x: x - 2, y: y - 32, width: 22, height: 28, fill: "#f4f1ea", ...thin }) + s("rect", { x: x + 1, y: y - 29, width: 16, height: 4, fill: O }) + line(`M${x + 1} ${y - 21} H${x + 17} M${x + 1} ${y - 17} H${x + 17} M${x + 1} ${y - 13} H${x + 12} M${x + 1} ${y - 9} H${x + 17}`, "#8a8f99", 1.4),
  medbag: (x, y) => line(`M${x - 2} ${y + 6} Q${x + 6} ${y - 4} ${x + 14} ${y + 6}`, O, 2.6) + s("path", { d: `M${x - 6} ${y + 6} H${x + 18} L${x + 20} ${y + 20} H${x - 8} Z`, fill: "#3b2a22", ...thin }) + s("rect", { x: x + 3, y: y + 9, width: 6, height: 4, fill: GOLD }),
  carpetbag: (x, y) => line(`M${x - 2} ${y + 6} Q${x + 6} ${y - 4} ${x + 14} ${y + 6}`, O, 2.6) + s("path", { d: `M${x - 7} ${y + 6} H${x + 19} L${x + 21} ${y + 22} H${x - 9} Z`, fill: "#b5523b", ...thin }) + line(`M${x - 6} ${y + 12} H${x + 20} M${x - 7} ${y + 17} H${x + 21}`, GOLD, 1.6),
  flag: (x, y, kind = "uk") => line(`M${x + 1} ${y + 14} L${x + 3} ${y - 42}`, "#8b5e3c", 2.6) + ({
    us: s("rect", { x: x + 3, y: y - 42, width: 26, height: 17, fill: "#fff", ...thin }) + line(`M${x + 4} ${y - 38} H${x + 28} M${x + 4} ${y - 32} H${x + 28} M${x + 4} ${y - 27} H${x + 28}`, RED, 2.2) + s("rect", { x: x + 3, y: y - 42, width: 11, height: 9, fill: "#2f4570" }),
    fr: s("rect", { x: x + 3, y: y - 42, width: 26, height: 17, fill: "#fff", ...thin }) + s("rect", { x: x + 4.2, y: y - 40.8, width: 7.6, height: 14.6, fill: "#2f5fb3" }) + s("rect", { x: x + 20.2, y: y - 40.8, width: 7.6, height: 14.6, fill: RED }),
    ru: s("rect", { x: x + 3, y: y - 42, width: 26, height: 17, fill: "#fff", ...thin }) + s("rect", { x: x + 4.2, y: y - 36.2, width: 23.6, height: 5.4, fill: "#2f5fb3" }) + s("rect", { x: x + 4.2, y: y - 30.8, width: 23.6, height: 4.6, fill: RED }),
    uk: s("rect", { x: x + 3, y: y - 42, width: 26, height: 17, fill: "#2f4570", ...thin }) + line(`M${x + 16} ${y - 42} V${y - 25} M${x + 3} ${y - 33.5} H${x + 29}`, "#fff", 5) + line(`M${x + 16} ${y - 42} V${y - 25} M${x + 3} ${y - 33.5} H${x + 29}`, RED, 2.4),
  })[kind],
  olive: (x, y) => line(`M${x} ${y + 2} Q${x + 6} ${y - 18} ${x + 16} ${y - 32}`, "#6d7238", 2.4) + [[4, -10, -30], [9, -20, 30], [12, -26, -30], [16, -32, 20]].map(([dx, dy, r]) => s("ellipse", { cx: x + dx, cy: y + dy, rx: 2.8, ry: 6, transform: `rotate(${r} ${x + dx} ${y + dy})`, fill: "#8a8f4a", stroke: O, "stroke-width": 1.2 })).join(""),
  telescope: (x, y) => s("path", { d: `M${x - 6} ${y + 2} L${x + 20} ${y - 22} L${x + 25} ${y - 16} L${x - 1} ${y + 8} Z`, fill: BRASS, ...thin }) + line(`M${x + 5} ${y - 8} l5 6 M${x + 12} ${y - 15} l5 6`, O, 2),
  globe: (x, y) => line(`M${x + 8} ${y + 4} V${y - 6} M${x + 2} ${y + 4} H${x + 14}`, O, 2.6) + s("circle", { cx: x + 8, cy: y - 17, r: 11, fill: "#7cc4ef", ...thin })
    + s("path", { d: `M${x + 2} ${y - 22} q5 -3 8 1 q-2 5 -6 3 Z M${x + 9} ${y - 13} q5 -2 7 3 q-4 4 -7 0 Z`, fill: "#5b8f4e" }) + line(`M${x - 3} ${y - 17} H${x + 19}`, O, 1.2),
  bouquet: (x, y) => line(`M${x + 2} ${y + 2} L${x + 6} ${y - 18} M${x + 2} ${y + 2} L${x - 2} ${y - 16} M${x + 2} ${y + 2} L${x + 12} ${y - 14}`, "#46733b", 2.2)
    + [[x + 6, y - 22, "#e5484d"], [x - 3, y - 19, "#f2c230"], [x + 13, y - 17, "#e98aa6"]].map(([cx, cy, c]) => s("circle", { cx, cy, r: 5, fill: c, ...thin }) + s("circle", { cx, cy, r: 1.6, fill: O })).join(""),
  hourglass: (x, y) => s("rect", { x: x - 2, y: y - 32, width: 20, height: 4, rx: 1, fill: "#8b5e3c", ...thin }) + s("rect", { x: x - 2, y: y - 4, width: 20, height: 4, rx: 1, fill: "#8b5e3c", ...thin })
    + s("path", { d: `M${x + 1} ${y - 28} H${x + 15} L${x + 8} ${y - 16} L${x + 15} ${y - 4} H${x + 1} L${x + 8} ${y - 16} Z`, fill: "#e8eef2", ...thin }) + s("path", { d: `M${x + 4} ${y - 4} L${x + 8} ${y - 10} L${x + 12} ${y - 4} Z M${x + 5} ${y - 25} H${x + 11} L${x + 8} ${y - 21} Z`, fill: "#e9c46a" }),
  horseshoe: (x, y) => line(`M${x} ${y - 4} V${y - 18} Q${x} ${y - 30} ${x + 10} ${y - 30} Q${x + 20} ${y - 30} ${x + 20} ${y - 18} V${y - 4}`, "#8a8f99", 5.5) + [[x, y - 14], [x + 20, y - 14], [x + 4, y - 25], [x + 16, y - 25]].map(([cx, cy]) => s("circle", { cx, cy, r: 1, fill: O })).join(""),
  tankard: (x, y) => s("rect", { x: x - 1, y: y - 22, width: 17, height: 22, rx: 2, fill: "#9aa0a6", ...thin }) + s("path", { d: `M${x - 3} ${y - 22} Q${x - 3} ${y - 30} ${x + 4} ${y - 27} Q${x + 8} ${y - 33} ${x + 13} ${y - 27} Q${x + 20} ${y - 29} ${x + 18} ${y - 22} Z`, fill: "#fff", ...thin })
    + line(`M${x + 16} ${y - 18} q7 1 6 7 q-1 5 -6 4`, O, 2.4),
  crook: (x, y) => line(`M${x} ${y + 20} L${x + 5} ${y - 30} Q${x + 6} ${y - 42} ${x + 15} ${y - 40} Q${x + 21} ${y - 38} ${x + 18} ${y - 31}`, "#8b5e3c", 3.5),
  scalpel: (x, y) => line(`M${x} ${y - 2} L${x + 8} ${y - 18}`, "#55606a", 3.5) + s("path", { d: `M${x + 8} ${y - 18} L${x + 10} ${y - 30} L${x + 13} ${y - 22} Z`, fill: "#e8eef2", ...thin }),
  iron: (x, y) => s("path", { d: `M${x - 8} ${y - 2} Q${x - 6} ${y - 14} ${x + 14} ${y - 14} Q${x + 22} ${y - 12} ${x + 24} ${y - 2} Z`, fill: "#55555e", ...thin }) + line(`M${x - 1} ${y - 14} Q${x + 6} ${y - 24} ${x + 13} ${y - 14}`, O, 3),
  shoe: (x, y) => s("path", { d: `M${x - 2} ${y - 28} H${x + 8} V${y - 12} Q${x + 22} ${y - 11} ${x + 24} ${y - 3} H${x - 2} Z`, fill: "#3b2a22", ...thin }) + line(`M${x + 1} ${y - 24} H${x + 6} M${x + 1} ${y - 19} H${x + 6}`, CREAM, 1.4),
  hammer: (x, y) => line(`M${x} ${y + 4} L${x + 8} ${y - 26}`, "#8b5e3c", 3.5) + s("rect", { x: x - 1, y: y - 33, width: 20, height: 8, rx: 1.5, transform: `rotate(15 ${x + 9} ${y - 29})`, fill: "#55555e", ...thin }),
  cloth: (x, y) => s("rect", { x: x - 6, y: y - 30, width: 14, height: 30, rx: 3, transform: `rotate(-20 ${x + 1} ${y - 15})`, fill: "#5b8fd6", ...thin }) + line(`M${x - 4} ${y - 22} L${x + 8} ${y - 26} M${x - 2} ${y - 14} L${x + 10} ${y - 18} M${x} ${y - 6} L${x + 12} ${y - 10}`, "#f2c230", 1.6),
  scales: (x, y) => line(`M${x + 6} ${y + 2} V${y - 36} M${x - 8} ${y - 32} H${x + 20}`, GOLD, 2.6) + line(`M${x - 8} ${y - 32} l-4 12 M${x - 8} ${y - 32} l4 12 M${x + 20} ${y - 32} l-4 12 M${x + 20} ${y - 32} l4 12`, O, 1.2)
    + s("path", { d: `M${x - 14} ${y - 20} H${x - 2} Q${x - 8} ${y - 14} ${x - 14} ${y - 20} Z M${x + 14} ${y - 20} H${x + 26} Q${x + 20} ${y - 14} ${x + 14} ${y - 20} Z`, fill: GOLD, ...thin }),
  hoop: (x, y) => line(`M${x} ${y} L${x + 14} ${y + 10}`, "#8b5e3c", 2.6) + s("circle", { cx: x + 16, cy: y + 12, r: 11, fill: "none", stroke: "#b5523b", "stroke-width": 3 }),
  leek: (x, y) => s("path", { d: `M${x} ${y + 2} L${x + 4} ${y - 14} L${x + 9} ${y - 12} L${x + 6} ${y + 4} Z`, fill: "#f4f1ea", ...thin }) + s("path", { d: `M${x + 4} ${y - 14} Q${x - 2} ${y - 32} ${x + 4} ${y - 40} Q${x + 6} ${y - 26} ${x + 9} ${y - 12} Q${x + 14} ${y - 28} ${x + 22} ${y - 34} Q${x + 18} ${y - 22} ${x + 9} ${y - 12} Z`, fill: "#5b8f4e", ...thin }),
};

// Backdrops, drawn first. Feet are at y≈111.
const flame = (x, h) => s("path", { d: `M${x - 9} 116 Q${x - 12} ${116 - h * .5} ${x - 2} ${116 - h} Q${x} ${116 - h * .6} ${x + 5} ${116 - h * .75} Q${x + 13} ${116 - h * .4} ${x + 9} 116 Z`, fill: "#f39c12" })
  + s("path", { d: `M${x - 4} 116 Q${x - 6} ${116 - h * .35} ${x} ${116 - h * .6} Q${x + 7} ${116 - h * .3} ${x + 4} 116 Z`, fill: "#ffd84d" });
const BACK = {
  reeds: () => line("M8 116 Q6 84 12 60 M16 116 Q18 90 14 70 M106 116 Q110 86 104 64 M114 116 Q112 92 118 76", "#5b8f4e", 2.6) + s("ellipse", { cx: 12, cy: 58, rx: 3, ry: 8, fill: "#8b5e3c" }) + s("ellipse", { cx: 104, cy: 62, rx: 3, ry: 8, fill: "#8b5e3c" })
    + line("M30 118 q4 -10 0 -18 q-4 -8 2 -16 M92 118 q-4 -10 0 -18 q4 -8 -2 -16", "#7ac27a", 2) + line("M20 118 q8 -4 16 0 t16 0 t16 0 t16 0 t16 0", "#5aa9d6", 2.6),
  starfield: () => [[8, 6, 3], [22, -16, 2.4], [104, 34, 3.4], [16, 74, 2.6], [112, 84, 2.2], [98, 2, 2], [4, 40, 2]].map(([x, y, r]) => star(x, y, r, "#7c82c8")).join("")
    + s("circle", { cx: 104, cy: -10, r: 8, fill: "#e0b04a", ...thin }) + s("ellipse", { cx: 104, cy: -10, rx: 15, ry: 4, fill: "none", stroke: O, "stroke-width": 2, transform: "rotate(-18 104 -10)" }),
  mane: () => s("path", { d: Array.from({ length: 28 }, (_, i) => { const a = (i / 28) * 2 * Math.PI, r = i % 2 ? 27 : 37; return `${i ? "L" : "M"}${(60 + r * Math.cos(a)).toFixed(1)} ${(44 + r * Math.sin(a)).toFixed(1)}`; }).join(" ") + " Z", fill: "#d08a2e", ...thin }),
  meridian: () => s("path", { d: "M10 -24 V116", stroke: RED, "stroke-width": 2, "stroke-dasharray": "5 4", fill: "none" }) + s("text", { x: 14, y: -12, "font-family": "Georgia, serif", "font-size": 12, fill: RED }, "0°"),
  bars: () => line("M2 -16 V116 M14 -16 V116 M106 -16 V116 M118 -16 V116 M-2 -10 H18 M102 -10 H122", "#b9bec6", 3.5),
  maple: () => s("path", { d: "M16 8 L19 18 L26 14 L24 24 L32 24 L26 30 L28 34 L19 32 L18 42 L14 42 L13 32 L4 34 L6 30 L0 24 L8 24 L6 14 L13 18 Z", fill: "#d9342b" }),
  church: () => s("path", { d: "M2 112 V78 L14 66 L26 78 V112 Z M11 66 V46 L14 38 L17 46 V66 Z", fill: "#e6e6ec" }) + line("M14 30 V37 M11 33 H17", "#cfcfd8", 2),
  factory: () => s("path", { d: "M82 112 V82 L94 74 V82 L106 74 V82 L124 74 V112 Z M110 74 V36 H117 V74 Z", fill: "#e6e6ec" }) + [[114, 28, 4], [119, 19, 5], [113, 10, 6]].map(([cx, cy, r]) => s("circle", { cx, cy, r, fill: "#f0f0f3" })).join(""),
  flames: () => flame(10, 40) + flame(24, 26) + flame(100, 30) + flame(114, 44),
  ruins: () => s("path", { d: "M4 112 V58 L10 54 L14 60 L18 56 V112 Z M100 112 V74 L105 70 L110 76 L114 72 V112 Z", fill: "#e6e1d6" }) + line("M8 66 V108 M14 66 V108 M104 82 V108 M110 82 V108", "#d6cfbf", 1.4),
  rays: () => Array.from({ length: 12 }, (_, i) => { const a = (i / 12) * 2 * Math.PI + .26; return line(`M${(60 + 40 * Math.cos(a)).toFixed(1)} ${(42 + 40 * Math.sin(a)).toFixed(1)} L${(60 + 62 * Math.cos(a)).toFixed(1)} ${(42 + 62 * Math.sin(a)).toFixed(1)}`, "#f7d97a", 3.5); }).join(""),
  fern: () => line("M14 114 Q6 76 24 34", "#5b8f4e", 2.6) + Array.from({ length: 9 }, (_, i) => { const y = 104 - i * 8, x = 10 - i * .2 + (i > 4 ? (i - 4) * 2.2 : 0); return line(`M${x} ${y} l-8 -5 M${x + 1} ${y} l8 -6`, "#7aa36b", 2); }).join(""),
  post: () => s("rect", { x: 4, y: 28, width: 15, height: 86, fill: "#a8784f", ...thin }) + s("path", { d: "M2 30 L11.5 20 L21 30 Z", fill: "#8b5e3c", ...thin }) + line("M8 46 V100 M14 40 V90", "#8b5e3c", 1.2),
  waves: () => line("M24 116 q7 -5 14 0 t14 0 t14 0 t14 0 t14 0 t14 0", "#5aa9d6", 3),
  wisps: () => line("M36 116 q6 -5 12 0 t12 0 t12 0 t12 0", "#bdb2e6", 3),
  sparkles: () => star(16, 30, 5) + star(104, 52, 4) + star(100, 16, 3),
  skyline: () => s("path", { d: "M2 112 V70 H10 V58 H14 V70 H20 V52 Q20 38 30 36 Q40 38 40 52 V64 H44 V112 Z M84 112 V60 H90 V44 L94 38 L98 44 V60 H104 V74 H112 V112 Z", fill: "#e6e6ec" }) + s("path", { d: "M27 36 h6 v-6 h-6 Z", fill: "#e6e6ec" }),
  pyramids: () => s("path", { d: "M-2 112 L20 70 L42 112 Z M80 112 L104 64 L128 112 Z", fill: "#ecd9a8" }) + line("M20 70 L30 112 M104 64 L114 112", "#d8c08a", 1.5),
  palm: () => line("M14 112 Q10 84 18 62", "#8b5e3c", 4) + s("path", { d: "M18 62 Q4 56 0 64 Q8 58 18 62 Q10 46 2 46 Q14 46 18 62 Q22 44 34 44 Q24 50 18 62 Q32 52 38 60 Q28 58 18 62 Z", fill: "#5b8f4e", ...thin }),
  sun: () => s("circle", { cx: 100, cy: 6, r: 9, fill: "#f7c948" }) + [0, 45, 90, 135, 180, 225, 270, 315].map(a => line(`M${100 + 12 * Math.cos(a * Math.PI / 180)} ${6 + 12 * Math.sin(a * Math.PI / 180)} L${100 + 16 * Math.cos(a * Math.PI / 180)} ${6 + 16 * Math.sin(a * Math.PI / 180)}`, "#f7c948", 2.4)).join(""),
  dunes: () => s("path", { d: "M-2 118 Q20 100 46 112 Q70 102 96 110 Q112 104 124 110 V122 H-2 Z", fill: "#f2dca0" }),
  sheep: () => s("path", { d: "M4 108 q-4 -6 2 -9 q0 -6 7 -5 q3 -5 9 -2 q6 -1 6 5 q5 2 2 8 q1 5 -5 5 H8 q-6 0 -4 -2 Z", fill: "#fff", ...thin }) + s("ellipse", { cx: 29, cy: 100, rx: 4, ry: 5, fill: O }) + line("M10 112 v5 M22 112 v5", O, 2.4),
  ship: () => s("path", { d: "M2 104 H34 L29 112 H7 Z", fill: "#8b5e3c", ...thin }) + line("M18 104 V72", O, 2.4) + s("path", { d: "M19 74 L33 100 H19 Z M17 78 L5 100 H17 Z", fill: "#fff", ...thin }) + line("M-2 116 q6 -4 12 0 t12 0 t12 0", "#5aa9d6", 2.6),
  dove: () => s("path", { d: "M6 14 Q14 4 24 12 Q30 6 36 8 Q32 14 26 16 Q20 24 10 20 Q4 20 6 14 Z", fill: "#fff", ...thin }) + s("circle", { cx: 30, cy: 10, r: 1.2, fill: O }) + line("M35 10 l4 1", "#f5c542", 2),
  bigben: () => s("path", { d: "M6 112 V30 L14 16 L22 30 V112 Z", fill: "#e6e6ec" }) + s("circle", { cx: 14, cy: 40, r: 5, fill: "#fff", stroke: "#cfcfd8", "stroke-width": 2 }) + line("M14 40 v-3 M14 40 h2", "#9aa0a6", 1.4),
  capitol: () => s("path", { d: "M0 112 V84 H40 V112 Z M8 84 Q8 62 20 60 Q32 62 32 84 Z", fill: "#e6e6ec" }) + s("rect", { x: 18, y: 52, width: 4, height: 9, fill: "#e6e6ec" }),
  haystack: () => s("path", { d: "M-2 112 Q0 82 16 78 Q32 82 34 112 Z", fill: "#e9c46a", ...thin }) + line("M6 104 L10 92 M16 100 L18 88 M24 104 L22 92", "#b88a2e", 1.6),
  crystal: () => s("path", { d: "M-4 112 V64 Q60 6 124 64 V112", fill: "#eef6fb", stroke: "#cfe3ef", "stroke-width": 2 }) + line("M14 112 V52 M34 112 V36 M86 112 V36 M106 112 V52 M-2 80 Q60 30 122 80", "#cfe3ef", 1.6),
  bubbles: () => [[14, 40, 6], [24, 26, 4], [104, 64, 5], [12, 66, 3.5], [100, 40, 3]].map(([cx, cy, r]) => s("circle", { cx, cy, r, fill: "#e6f4fc", stroke: "#8fc7e8", "stroke-width": 1.8 })).join(""),
};
const bubble = t => s("path", { d: "M2 -14 H38 Q42 -14 42 -10 V2 Q42 6 38 6 H22 L14 13 L15 6 H2 Q-2 6 -2 2 V-10 Q-2 -14 2 -14 Z", fill: "#fff", ...thin })
  + s("text", { x: 20, y: 0, "text-anchor": "middle", "font-family": "Georgia, serif", "font-style": "italic", "font-size": 13, fill: O }, t);

// Novelty-sprint additions: small, deliberately literal visual emblems for the
// discovered characters. All use the steam-man kit's existing stroke and palette.
const gear = (x, y, r = 10, fill = BRASS) => s("circle", {cx:x, cy:y, r, fill, ...thin})
  + Array.from({length:8},(_,i)=>{const a=i*Math.PI/4;return line(`M${x+(r-1)*Math.cos(a)} ${y+(r-1)*Math.sin(a)} L${x+(r+4)*Math.cos(a)} ${y+(r+4)*Math.sin(a)}`,O,3.5)}).join("")
  + s("circle",{cx:x,cy:y,r:r*.35,fill:CREAM,...thin});
const label = (x,y,t,size=10,fill=O) => s("text",{x,y,"text-anchor":"middle","font-family":"Georgia,serif","font-size":size,"font-weight":700,fill},t);
const cow = (x,y) => s("path",{d:`M${x-6} ${y-5} l-5 -7 l8 3 M${x+6} ${y-5} l5 -7 l-8 3`,fill:"none",...thin})
  + s("rect",{x:x-8,y:y-8,width:16,height:16,rx:5,fill:CREAM,...thin})+s("ellipse",{cx:x,cy:y+5,rx:8,ry:5,fill:"#d8b07a",...thin})
  + s("circle",{cx:x-3,cy:y-3,r:1.5,fill:O})+s("circle",{cx:x+3,cy:y-3,r:1.5,fill:O});
const bookStack = (x,y) => [[-1,0,"#5b8f4e"],[1,-7,"#b5523b"],[-2,-14,"#3f5a8a"]].map(([dx,dy,c])=>s("rect",{x:x+dx,y:y+dy,width:24,height:7,rx:1.3,fill:c,...thin})+line(`M${x+4+dx} ${y+dy+2} H${x+21+dx}`,CREAM,1.2)).join("");
Object.assign(HAND,{
  placard:(x,y,t="I?")=>s("rect",{x:x-3,y:y-33,width:25,height:28,rx:2,fill:CREAM,...thin})+label(x+9.5,y-15,t,10)+line(`M${x+9} ${y-5} V${y+5}`,O,2.5),
  envelope:(x,y)=>s("rect",{x:x-6,y:y-26,width:30,height:22,rx:2,fill:CREAM,...thin})+line(`M${x-5} ${y-25} L${x+9} ${y-14} L${x+23} ${y-25}`,O,1.6)+s("circle",{cx:x+9,cy:y-12,r:3.5,fill:RED,...thin}),
  books:(x,y)=>bookStack(x-3,y-7),
  bottle:(x,y,t="E")=>s("path",{d:`M${x+3} ${y-38} H${x+13} V${y-27} Q${x+21} ${y-24} ${x+21} ${y-17} V${y} H${x-5} V${y-17} Q${x-5} ${y-24} ${x+3} ${y-27} Z`,fill:"#f0e2bc",...thin})+s("rect",{x:x+2,y:y-42,width:12,height:6,rx:1,fill:"#8b5e3c",...thin})+s("rect",{x:x-2,y:y-19,width:20,height:13,fill:CREAM,...thin})+label(x+8,y-9,t,10),
  powder:(x,y)=>s("rect",{x:x-5,y:y-27,width:28,height:26,rx:4,fill:CREAM,...thin})+s("rect",{x:x-7,y:y-31,width:32,height:6,rx:2,fill:"#9aa0a6",...thin})+label(x+9,y-10,"E",14)+star(x+27,y-35,3,GOLD),
  basin:(x,y)=>s("path",{d:`M${x-10} ${y-7} H${x+24} Q${x+21} ${y+7} ${x+7} ${y+7} Q${x-7} ${y+7} ${x-10} ${y-7} Z`,fill:"#d7edf5",...thin})+s("ellipse",{cx:x+7,cy:y-7,rx:17,ry:4,fill:"#fff",...thin})+[[0,-13,3],[9,-16,4],[18,-12,2.5]].map(([a,b,r])=>s("circle",{cx:x+a,cy:y+b,r,fill:"#fff",stroke:"#8fc7e8","stroke-width":1.5})).join(""),
  coin:(x,y,t="5G")=>s("circle",{cx:x+9,cy:y-16,r:13,fill:GOLD,...thin})+s("circle",{cx:x+9,cy:y-16,r:9.5,fill:"none",stroke:"#b88a2e","stroke-width":1.4})+label(x+9,y-12,t,10),
  sewing:(x,y)=>s("rect",{x:x-9,y:y,width:36,height:5,rx:1,fill:O})+s("path",{d:`M${x-4} ${y} V${y-29} H${x+17} Q${x+24} ${y-29} ${x+24} ${y-21} V${y-10} H${x+16} V${y-21} H${x+5} V${y} Z`,fill:O,...thin})+s("circle",{cx:x+23,cy:y-22,r:7,fill:CREAM,...thin})+line(`M${x+23} ${y-27} V${y-17} M${x+18} ${y-22} H${x+28}`,O,1.5)+s("rect",{x:x+5,y:y-35,width:9,height:6,fill:RED,...thin})+line(`M${x} ${y-21} V${y-3}`,"#9aa0a6",1.5)+s("path",{d:`M${x-7} ${y-2} q12 7 23 1`,fill:"none",stroke:RED,"stroke-width":2}),
  roast:(x,y)=>s("ellipse",{cx:x+9,cy:y-7,rx:20,ry:5,fill:CREAM,...thin})+s("ellipse",{cx:x+9,cy:y-16,rx:15,ry:10,fill:"#a8473b",...thin})+s("path",{d:`M${x+1} ${y-20} Q${x+10} ${y-27} ${x+18} ${y-17} Q${x+7} ${y-12} ${x+1} ${y-20} Z`,fill:"#e6a18f",...thin})+line(`M${x+11} ${y-20} l7 -2`,CREAM,2.5),
  gear:(x,y)=>gear(x+9,y-18,11),
  bell:(x,y)=>s("path",{d:`M${x-5} ${y-9} Q${x+2} ${y-14} ${x+1} ${y-25} Q${x+8} ${y-38} ${x+15} ${y-25} Q${x+14} ${y-14} ${x+21} ${y-9} Z`,fill:GOLD,...thin})+line(`M${x-6} ${y-8} H${x+22}`,O,2.5)+s("circle",{cx:x+8,cy:y-6,r:3,fill:O}),
  stamp:(x,y)=>s("rect",{x:x-6,y:y-8,width:30,height:8,rx:1.5,fill:"#8b5e3c",...thin})+s("path",{d:`M${x+2} ${y-8} V${y-18} Q${x-3} ${y-29} ${x+9} ${y-30} Q${x+21} ${y-29} ${x+16} ${y-18} V${y-8} Z`,fill:"#c98b4f",...thin})+line(`M${x-7} ${y+3} H${x+25}`,RED,3),
  paper:(x,y)=>s("path",{d:`M${x-5} ${y-33} H${x+13} L${x+22} ${y-24} V${y-1} H${x-5} Z`,fill:"#e8f4f7",...thin})+line(`M${x+13} ${y-33} V${y-24} H${x+22} M${x} ${y-18} H${x+15} M${x} ${y-12} H${x+12}`,"#6aa6c8",1.6)+s("path",{d:`M${x+19} ${y-7} q8 0 4 6 q-5 3 -4 -6 Z`,fill:"#8fc7e8",...thin}),
  mask:(x,y)=>s("path",{d:`M${x-5} ${y-31} Q${x+9} ${y-36} ${x+23} ${y-31} V${y-16} Q${x+9} ${y} ${x-5} ${y-16} Z`,fill:CREAM,...thin})+s("ellipse",{cx:x+3,cy:y-25,rx:3,ry:2,fill:O})+s("ellipse",{cx:x+15,cy:y-25,rx:3,ry:2,fill:O})+line(`M${x+3} ${y-15} Q${x+9} ${y-9} ${x+15} ${y-15}`,O,1.6),
  key:(x,y)=>s("circle",{cx:x+9,cy:y-29,r:7,fill:"none",stroke:GOLD,"stroke-width":4})+line(`M${x+9} ${y-22} V${y+1} h8 M${x+9} ${y-7} h6`,GOLD,4),
  candle:(x,y)=>s("rect",{x:x+2,y:y-22,width:13,height:24,rx:2,fill:CREAM,...thin})+s("ellipse",{cx:x+8.5,cy:y+4,rx:15,ry:4,fill:GOLD,...thin})+s("path",{d:`M${x+8} ${y-25} Q${x-1} ${y-30} ${x+9} ${y-43} Q${x+20} ${y-30} ${x+8} ${y-25} Z`,fill:"#f7c948",...thin}),
  lyre:(x,y)=>line(`M${x} ${y-32} Q${x-7} ${y-2} ${x+9} ${y-2} Q${x+25} ${y-2} ${x+18} ${y-32}`,GOLD,4)+line(`M${x-1} ${y-27} H${x+19} M${x+3} ${y-26} V${y-6} M${x+9} ${y-26} V${y-4} M${x+15} ${y-26} V${y-6}`,O,1.3),
  picklejar:(x,y)=>s("rect",{x:x-6,y:y-30,width:29,height:31,rx:5,fill:"#cfe8d0",...thin})+s("rect",{x:x-7,y:y-35,width:31,height:7,rx:2,fill:"#9aa0a6",...thin})+s("ellipse",{cx:x+9,cy:y-13,rx:5,ry:12,transform:`rotate(15 ${x+9} ${y-13})`,fill:"#5b8f4e",...thin})+[[6,-17],[11,-10],[8,-5]].map(([a,b])=>s("circle",{cx:x+a,cy:y+b,r:1,fill:"#c7d99b"})).join(""),
});
Object.assign(HAND,{
  metalbar:(x,y)=>s("path",{d:`M${x-7} ${y-4} L${x-2} ${y-20} H${x+18} L${x+25} ${y-4} Z`,fill:"#c9d6dc",...thin})+line(`M${x-1} ${y-16} H${x+15}`,"#fff",2.5)+s("circle",{cx:x+8,cy:y-10,r:3,fill:"#8fc7e8",...thin}),
  brick:(x,y)=>s("path",{d:`M${x-7} ${y-20} L${x+12} ${y-26} L${x+26} ${y-17} V${y-3} L${x+8} ${y+2} L${x-7} ${y-7} Z`,fill:"#b5523b",...thin})+line(`M${x-7} ${y-20} L${x+8} ${y-11} L${x+26} ${y-17} M${x+8} ${y-11} V${y+2}`,"#f0b193",1.5),
});
Object.assign(FACES,{
  muzzle:()=>s("ellipse",{cx:60,cy:49,rx:13,ry:7,fill:"#b58e5c",...thin})+s("ellipse",{cx:55,cy:49,rx:2,ry:2.8,fill:O})+s("ellipse",{cx:65,cy:49,rx:2,ry:2.8,fill:O}),
});
Object.assign(CHEST,{
  mirrorwindow:()=>s("rect",{x:44,y:77,width:32,height:21,rx:4,fill:"#d5edf5",...thin})+line("M49 94 L70 80 M58 96 L73 85","#fff",2.2),
  gears:()=>gear(60,87,9),
  passengers:()=>Array.from({length:12},(_,i)=>s("circle",{cx:42+(i%4)*12,cy:80+Math.floor(i/4)*7,r:2.6,fill:CREAM,stroke:O,"stroke-width":1})).join(""),
  parcel:()=>s("rect",{x:41,y:77,width:38,height:23,rx:2,fill:"#d8b07a",...thin})+line("M41 88 H79 M60 77 V100",CREAM,2.5)+s("rect",{x:44,y:80,width:12,height:6,fill:CREAM})+label(50,85,"I",5),
  stitches:()=>s("rect",{x:43,y:78,width:34,height:20,rx:2,fill:"#f4f1ea",...thin})+line("M47 82 l4 4 l4 -4 l4 4 l4 -4 l4 4 l4 -4 M47 92 H73",RED,1.6),
  books:()=>bookStack(48,93),
  letter:()=>s("rect",{x:43,y:79,width:34,height:18,rx:2,fill:CREAM,...thin})+line("M44 80 L60 91 L76 80",O,1.4),
});
for(const name of ["mirrorwindow","gears","passengers","parcel","stitches","books","letter"])COVERS_GAUGE.add(name);
Object.assign(BACK,{
  mirrorhall:()=>[0,94].map(x=>s("path",{d:`M${x} 112 V25 Q${x} 5 ${x+13} 5 Q${x+26} 5 ${x+26} 25 V112 Z`,fill:"#e8e0cb",stroke:"#bca477","stroke-width":2})+s("path",{d:`M${x+5} 108 V27 Q${x+5} 12 ${x+13} 12 Q${x+21} 12 ${x+21} 27 V108 Z`,fill:"#d8ebf3",stroke:"#adcbd9","stroke-width":1.3})+line(`M${x+7} 68 l11 -20 M${x+7} 83 l11 -20`,"#fff",2)).join("")+line("M-2 116 H122","#bca477",2),
  wind:()=>line("M-2 25 H22 Q35 25 31 14 Q27 8 22 14 M94 10 H114 Q128 10 120 0 M-2 74 H17 Q28 74 24 63 M91 65 H112 Q124 65 119 54 M1 110 Q18 98 33 110 M89 113 Q108 98 124 108","#6aa6c8",2.5),
  raincloud:()=>s("path",{d:"M91 15 Q84 6 94 2 Q98 -9 108 -3 Q120 -4 120 6 Q128 14 118 17 H94 Z",fill:"#d4e0eb",stroke:"#9aa0a6","stroke-width":1.5})+line("M96 23 l-3 7 M107 23 l-3 7 M118 23 l-3 7","#6aa6c8",2),
  stormsea:()=>line("M-2 112 Q7 94 18 108 Q28 92 39 110 M81 110 Q94 90 104 109 Q115 95 124 110","#5aa9d6",3)+s("path",{d:"M4 8 Q0 0 10 -4 Q14 -12 22 -7 Q33 -7 33 4 Q41 11 28 13 H8 Z",fill:"#d3dce6"})+line("M18 17 l-5 10 h7 l-6 12",GOLD,3),
  clockcattle:()=>cow(10,86)+cow(110,86)+gear(13,31,9)+gear(108,37,8)+line("M4 113 Q20 102 36 113 M83 113 Q104 103 121 113","#8a8f99",2.3)+[4,12,24,94,105,116].map((x,i)=>s("circle",{cx:x,cy:50+i%3*7,r:1.5,fill:"#bca477"})).join(""),
  bookfamily:()=>[3,13,23,98,110].map((x,i)=>s("rect",{x,y:76-(i%3)*7,width:9,height:36+(i%3)*7,rx:1,fill:["#8c5a8f","#5b8f4e","#b5523b"][i%3],stroke:O,"stroke-width":1.3})+line(`M${x+2} 84 H${x+7}`,CREAM,1.3)).join("")+label(12,20,"IX",15,"#8c5a8f"),
  doubleself:()=>s("g",{opacity:.35},s("rect",{x:0,y:27,width:27,height:25,rx:8,fill:"#bdb2e6",...thin})+s("rect",{x:4,y:34,width:19,height:12,rx:4,fill:FACE})+s("circle",{cx:9,cy:39,r:2,fill:CREAM})+s("circle",{cx:18,cy:39,r:2,fill:CREAM})+s("rect",{x:3,y:54,width:22,height:33,rx:6,fill:"#bdb2e6",...thin}))+line("M97 26 Q112 9 121 27 M98 37 Q113 51 121 36","#bdb2e6",2)+label(109,32,"?",18,"#8c5a8f"),
  doorlever:()=>s("rect",{x:0,y:36,width:26,height:77,rx:2,fill:"#e6e1d6",stroke:"#bca477","stroke-width":2})+s("rect",{x:5,y:42,width:16,height:29,fill:"none",stroke:"#bca477","stroke-width":1.3})+s("circle",{cx:21,cy:82,r:2.5,fill:GOLD})+line("M20 88 H6 V113 H110 V61 H97","#8a8f99",2.5)+s("circle",{cx:110,cy:62,r:4,fill:BRASS,...thin}),
  familytree:()=>line("M15 112 V26 H104 V112 M15 59 H29 M91 59 H104","#bca477",2)+[15,104].map(x=>s("rect",{x:x-6,y:45,width:12,height:20,rx:3,fill:"#efe6d2",...thin})+s("rect",{x:x-3,y:40,width:6,height:6,fill:"#8b5e3c",...thin})).join("")+label(14,16,"Sb",13,"#8c5a8f"),
  wheatfield:()=>line("M3 115 L12 77 M11 115 L24 89 M107 115 L102 78 M117 115 L113 88","#b88a2e",2)+[12,24,102,113].map((x,i)=>s("ellipse",{cx:x,cy:76+i%2*12,rx:3,ry:8,fill:"#e9c46a",stroke:"#b88a2e","stroke-width":1})).join(""),
  stage:()=>s("path",{d:"M-3 -22 H27 V65 Q10 57 -3 70 Z M94 -22 H123 V70 Q108 57 94 65 Z",fill:"#b5523b",stroke:O,"stroke-width":1.5})+line("M5 -18 V49 M16 -18 V51 M104 -18 V51 M115 -18 V49","#8a322b",2)+line("M-2 116 H122",O,2),
  verbcloud:()=>bubble("was")+s("g",{transform:"translate(91 18) scale(.7)"},bubble("am"))+s("g",{transform:"translate(1 73) scale(.7)"},bubble("be")),
  grainspirit:()=>s("path",{d:"M5 61 Q-1 39 11 35 Q24 39 18 61 L15 57 L11 62 L8 57 Z",fill:"#ddd6f3",stroke:"#8c5a8f","stroke-width":1.5})+s("circle",{cx:8,cy:46,r:1.5,fill:O})+s("circle",{cx:14,cy:46,r:1.5,fill:O})+line("M99 113 Q115 90 107 69","#b88a2e",2)+[0,1,2,3].map(i=>s("ellipse",{cx:107+i%2*4,cy:72+i*6,rx:3.2,ry:5,fill:"#e9c46a"})).join(""),
  soapbubbles:()=>BACK.bubbles()+s("rect",{x:0,y:96,width:27,height:17,rx:5,fill:"#e9e2ef",...thin})+label(13,107,"SOAP",6),
  sailboat:()=>BACK.ship()+BACK.wind(),
  beefbanquet:()=>s("ellipse",{cx:60,cy:115,rx:62,ry:8,fill:"#d8b07a",stroke:O,"stroke-width":1.5})+s("circle",{cx:8,cy:112,r:6,fill:CREAM,stroke:O,"stroke-width":1.2})+s("circle",{cx:111,cy:112,r:6,fill:CREAM,stroke:O,"stroke-width":1.2}),
  horsetail:()=>s("path",{d:"M87 95 Q122 110 114 79 Q121 91 123 76 Q127 112 93 116 Z",fill:"#6e4529",stroke:O,"stroke-width":2}),
  ninefaces:()=>[[-1,6],[17,-12],[102,-8],[114,15],[-1,55],[110,58],[4,88],[105,96],[14,109]].map(([x,y])=>s("rect",{x,y,width:13,height:11,rx:4,fill:"#ddd6f3",stroke:"#8c5a8f","stroke-width":1.3})+s("circle",{cx:x+4,cy:y+5,r:1,fill:O})+s("circle",{cx:x+9,cy:y+5,r:1,fill:O})).join(""),
});

Object.assign(BACK,{
  cattleherd:()=>cow(10,87)+cow(109,84)+BACK.horsetail(),
  chains:()=>[9,110].map(x=>[20,38,56,74,92,110].map(y=>s("ellipse",{cx:x,cy:y,rx:5,ry:10,fill:"none",stroke:"#9aa0a6","stroke-width":2.3})).join("")).join(""),
});

function eyes(mood) {
  const big = mood === "wide" ? 6 : 5;
  return [51.5, 68.5].map((x, i) => {
    if (mood === "closed") return line(`M${x - 5} 41 Q${x} 46 ${x + 5} 41`, EYE, 2.6);
    let e = s("circle", { cx: x, cy: 41, r: big, fill: EYE }) + s("circle", { cx: x + .6, cy: 41.6, r: big * .48, fill: O }) + s("circle", { cx: x + 1.8, cy: 39.6, r: big * .22, fill: "#fff" });
    if (mood === "smug") e += s("rect", { x: x - 6, y: 35, width: 12, height: 5.6, fill: FACE });
    if (mood === "sad") e += line(i ? `M${x - 5} 35 L${x + 4} 33` : `M${x - 4} 33 L${x + 5} 35`, EYE, 2);
    return e;
  }).join("");
}
const MOUTHS = {
  smile: line("M56 47.5 Q60 51.5 64 47.5", EYE, 2.2), frown: line("M56 50 Q60 46.5 64 50", EYE, 2.2), flat: line("M56 49 H64", EYE, 2.2),
  open: s("ellipse", { cx: 60, cy: 49, rx: 3, ry: 2.6, fill: EYE }),
};

export function robotSVG(c = {}) {
  const [main, shade] = PALETTES[c.color] || PALETTES.brass;
  const hat = c.hat || "chimney", faces = c.face || [], chest = c.chest || [], back = c.back || [];
  const chestNames = chest.map(x => (Array.isArray(x) ? x[0] : x));
  const part = (table, x, ...args) => (Array.isArray(x) ? table[x[0]](...args, ...x.slice(1)) : table[x](...args));
  const rh = [90.5, 91];
  const hand = (item, left = false) => {
    const drawing = item ? part(HAND, item, ...rh) : "";
    // Mirror the prop for the left grip, while keeping its inscription readable.
    return left ? drawing.replace(/<text ([^>]+)>[^<]*<\/text>/g, text => {
      const x = Number(text.match(/\bx="([^"]+)"/)[1]);
      return s("g", {transform:`translate(${2*x} 0) scale(-1 1)`}, text);
    }) : drawing;
  };
  const top = HAT_TOP[hat] ?? 5;
  const svg = [
    ...back.map(b => (Array.isArray(b) && b[0] === "bubble" ? bubble(b[1]) : part(BACK, b))),
    hand(c.right),
    c.left ? s("g", { transform: "translate(120 0) scale(-1 1)" }, hand(c.left, true)) : "",
    c.legs === 5 ? [29,42,55,68,81].map(x => s("rect", {x,y:94,width:9,height:14,rx:3,fill:shade,...thin}) + s("rect",{x:x-3,y:105,width:14,height:7,rx:3.5,fill:O})).join("") :
      s("rect", { x: 44, y: 94, width: 12, height: 14, rx: 3, fill: shade, ...ol }) + s("rect", { x: 64, y: 94, width: 12, height: 14, rx: 3, fill: shade, ...ol }) +
      s("rect", { x: 40, y: 104, width: 18, height: 7, rx: 3.5, fill: O }) + s("rect", { x: 62, y: 104, width: 18, height: 7, rx: 3.5, fill: O }),
    s("rect", { x: 23, y: 64, width: 13, height: 28, rx: 6.5, fill: main, ...ol }), s("rect", { x: 84, y: 64, width: 13, height: 28, rx: 6.5, fill: main, ...ol }),
    s("rect", { x: 34, y: 58, width: 52, height: 42, rx: 11, fill: main, ...ol }),
    s("rect", { x: 34, y: 68, width: 52, height: 7, fill: shade, ...ol }), [41, 50, 70, 79].map(x => s("circle", { cx: x, cy: 71.5, r: 1.8, fill: BRASS })).join(""),
    chestNames.some(n => COVERS_GAUGE.has(n)) ? "" : s("circle", { cx: 60, cy: 87, r: 7.5, fill: CREAM, ...ol }) + line("M60 87 L64 83", RED, 2.2),
    s("rect", { x: 52, y: 53, width: 16, height: 7, fill: shade, ...ol }),
    ...chest.map(x => part(CHEST, x)),
    s("circle", { cx: 34, cy: 42, r: 4.5, fill: BRASS, ...ol }), s("circle", { cx: 86, cy: 42, r: 4.5, fill: BRASS, ...ol }),
    s("rect", { x: 36, y: 26, width: 48, height: 32, rx: 12, fill: main, ...ol }),
    s("rect", { x: 42, y: 31, width: 36, height: 22, rx: 8, fill: FACE }),
    eyes(c.mood),
    faces.some(f => ["mustache", "beak", "beard", "lather", "muzzle"].includes(Array.isArray(f) ? f[0] : f)) ? "" : MOUTHS[c.mouth || (c.mood === "sad" ? "frown" : "smile")],
    ...faces.map(f => part(FACES, f)),
    HATS[hat](),
    c.halo ? s("ellipse", { cx: 60, cy: top - 8, rx: 15, ry: 4.5, fill: "none", stroke: GOLD, "stroke-width": 3.2 }) : "",
    c.crest ? [-34, 0, 34].map((deg, i) => s("path", { d: `M0 0 C-6 -8 -5 -${i === 1 ? 22 : 17} 0 -${i === 1 ? 26 : 21} C5 -${i === 1 ? 22 : 17} 6 -8 0 0 Z M0 -4 V-${i === 1 ? 20 : 15}`, transform: `translate(60 ${top + 6}) rotate(${deg})`, fill: "#2f4f57", ...ol, "stroke-width": 2.6 })).join("") : "",
  ].join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-4 -30 128 152">${svg}</svg>`;
}

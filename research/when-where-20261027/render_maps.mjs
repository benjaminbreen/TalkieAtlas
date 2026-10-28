// Draw the When-and-where base maps from Natural Earth (world-atlas) and project geocoded places.
// Reads the geocodes in whenwhere_labels.json and followup_labels.json, and the hand-placed London streets and
// Thames course in london_places.json; writes whenwhere_maps.json.
//   node sites/talkie-neuron-sample/render_maps.mjs
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { geoPath, geoNaturalEarth1, geoConicConformal, geoMercator, geoGraticule10 } from "d3-geo";
import { feature, mesh } from "topojson-client";

const here = dirname(fileURLToPath(import.meta.url));
const atlas = name => JSON.parse(readFileSync(join(here, "node_modules/world-atlas", name), "utf8"));
// Every geocoded place from the first-reply pass and the follow-up pass, one point per gazetteer key.
const places = [...new Map(["whenwhere_labels.json", "followup_labels.json"]
  .flatMap(f => JSON.parse(readFileSync(join(here, f), "utf8")).map(r => r.geo).filter(Boolean))
  .map(g => [g.key, { key: g.key, lat: g.lat, lon: g.lon }])).values()];
const round = d => d && d.replace(/(\d+\.\d)\d+/g, "$1");

function view(topo, projection, w, h, clip) {
  const land = feature(topo, topo.objects.land), borders = mesh(topo, topo.objects.countries, (a, b) => a !== b);
  const path = geoPath(projection);
  const pts = {};
  for (const p of places) {
    const xy = projection([p.lon, p.lat]);
    if (xy && (!clip || (xy[0] >= 0 && xy[0] <= w && xy[1] >= 0 && xy[1] <= h))) pts[p.key] = xy.map(v => Math.round(v * 10) / 10);
  }
  return { w, h, land: round(path(land)), borders: round(path(borders)), graticule: round(path(geoGraticule10())), pts };
}

const world110 = atlas("countries-110m.json"), world50 = atlas("countries-50m.json");
const W = 960, H = 500;
const world = view(world110, geoNaturalEarth1().scale(175).translate([W / 2, H / 2 + 10]), W, H, false);
// British Isles and the near Continent
const BW = 900, BH = 700;
const isles = view(world50, geoConicConformal().parallels([50, 60]).rotate([2, 0]).center([0, 54.6]).scale(3200).translate([BW / 2, BH / 2]).clipExtent([[-10, -10], [BW + 10, BH + 10]]), BW, BH, true);
// London street by street: no land to draw, just the Thames, district names and the hand-placed streets.
const L = JSON.parse(readFileSync(join(here, "london_places.json"), "utf8"));
const LW = 900, LH = 560, ll = ([lat, lon]) => [lon, lat];
const thames = { type: "LineString", coordinates: L.thames.map(ll) };
// Fit the streets, not the river, so the crowded centre gets the room; the Thames is clipped to the frame.
const lp = geoMercator().fitExtent([[40, 30], [LW - 120, LH - 30]], { type: "MultiPoint", coordinates: Object.values(L.points).map(ll) }).clipExtent([[0, 0], [LW, LH]]);
const xy = c => lp(ll(c)).map(v => Math.round(v * 10) / 10);
const london = { w: LW, h: LH, thames: round(geoPath(lp)(thames)), alias: L.alias,
  pts: Object.fromEntries(Object.entries(L.points).map(([k, c]) => [k, xy(c)])),
  areas: Object.fromEntries(Object.entries(L.areas).map(([k, c]) => [k, xy(c)])) };
writeFileSync(join(here, "whenwhere_maps.json"), JSON.stringify({ world, isles, london }));
console.log(JSON.stringify({ places: places.length, world: Object.keys(world.pts).length, isles: Object.keys(isles.pts).length, london: Object.keys(london.pts).length }));

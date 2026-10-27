# Talkie Neuron Persona Library

A buildless, local proof of concept inspired by
[Joshua Fonseca Rivera's Qwen neuron screen](https://qwen-neurons-site.vercel.app/).
It uses fresh Talkie outputs, a fixed random sample, and GPT-6 Luna judgments.

## View

The existing Talkie app serves this at http://127.0.0.1:8930/neuron-atlas/.
It needs no additional server. To run it independently from the Talkie Harness root:

```sh
.venv/bin/python -m http.server 8942 --bind 127.0.0.1 --directory sites/talkie-neuron-sample/dist
```

Open http://127.0.0.1:8942/. No installation or build is needed. The saved site
does not call a model, contact a judging service, or need a running Talkie model.
Search, filters, neuron lookup, atlas dots, parent comparisons, share links, and
CSV/JSON downloads operate on the exported data.

## Evidence and method

- Run: `runs/neuron-site-sample-20261027/`.
- Runner: `experiments/neuron_site_sample.py`.
- Sample: 400 neurons, 10 per layer, seed 20261027, both signs.
- Generation: native IT chat template, “Who are you?”, greedy, 160-token cap.
- Dose: 1.25, 1.0, 0.75, 0.5 times each layer's unsteered prompt median residual
  norm, first token excluded. The effective write direction includes Talkie's MLP
  gain and is added after the block at all positions.
- Retry criterion: Luna coherence below 5. Preserve all attempts.
- Judge: user-requested GPT-6 Luna subagents, using `JUDGE_RUBRIC.md`. They receive
  only IDs and reply text, with no explicit condition metadata.
- Controls: an unsteered reply in each batch.
- Combinations: up to eight highest-ranked coherent Persona candidates are
  rerun in a different batch layout; Luna compares the original and retest for the same specific identity, allowing wording changes. Exact text matches are recorded separately.
  Each pair begins at the solo strengths, then retries at 0.75 and 0.5 times both
  strengths if needed. All tested pairs are retained, including failures.

An initial exact-wording gate kept only 2 of 8 candidates. Luna comparison of the full replies confirmed the same specific identity in all 8. The expanded pair sweep uses those identity judgments; original exact-gate results remain preserved in `exact_text_round_*` files.

The reference site's exact judging prompt and repetition-stop implementation are
not public. This is an adapted replication, with a different model, judge, and
sample size; score values are not directly interchangeable with the reference.
The website records these differences. Self-identification is not evidence of a
stable identity or a unit's natural function.

## Re-export

```sh
.venv/bin/python sites/talkie-neuron-sample/export_data.py runs/neuron-site-sample-20261027
```

Only experiment outputs and method metadata are exported. Model weights, local
credentials, GPU queue state, and private machine configuration are excluded.

The runner saves raw token IDs, attempts, labels, selected results, reruns, and
pair outcomes separately. It supports `--resume`. It needs active judge workers
to consume `judge_tasks` and atomically write matching `judge_labels` files;
it deliberately has no hidden API-key dependency.

The smaller allocation cache and overlapped generation/judging are execution
optimizations. Batch changes and script snapshots are recorded in the run
manifest because BF16 results can depend on batch layout.

## Hosting

Production: https://talkieneurons.vercel.app/

Vercel deploys the `public/` directory of `benjaminbreen/TalkieAtlas` from its main branch. The source and rendered site are maintained in this workspace, then published to that repository.

## Build and deploy

`dist/` is the whole site. The library page (`index.html`, `app.js`, `style.css`, `specimen.js`) is hand-written; everything else is generated.

```sh
.venv/bin/python sites/talkie-neuron-sample/export_data.py runs/neuron-site-sample-20261027
.venv/bin/python sites/talkie-neuron-sample/build_pages.py --site-url https://YOUR-DOMAIN
cd sites/talkie-neuron-sample && npm install && npm run og   # ~2 min, uses installed Google Chrome
```

`build_pages.py` writes a crawlable page for every neuron direction (`n/24-3883-up/`) and pair (`p/23-3070-down_24-2054-up/`), the about page from `templates/about.html`, `site.json` (data without token ids), `slugs.json`, `sitemap.xml` and `robots.txt`. `render_og.mjs` draws the 1200×630 link-preview cards in `dist/og/` from `templates/og.html`. Link previews need absolute image URLs, so rebuild with the real domain before deploying.

Deploy `dist/` as a static site (on Vercel, set the project's root directory to `sites/talkie-neuron-sample/dist`, framework "Other", no build command). `dist/vercel.json` turns on trailing slashes, which the share pages' relative links rely on. Fonts are self-hosted; `fetch_fonts.py` refreshes them.


## Shared footer

The shared footer uses `templates/footer.html`, `dist/footer.css`, and
`dist/footer.js`. The page builder refreshes it automatically. After adding steam-man
SVGs, refresh the illustrated persona pool and existing footers without rebuilding
page content:

```sh
.venv/bin/python sites/talkie-neuron-sample/build_footer.py
```

Three distinct labeled single-neuron illustrations are chosen on each page load.
Each links to its neuron page. Font credits follow the active preview option:
`?type=source`, `?type=plex`, or `?type=newsreader`.


## Highlight carousel

The homepage keeps Source Sans 3 as its default. Its highlight carousel supports
previous/next buttons, arrow keys, and horizontal touch swipes. Automatic rotation
pauses on hover, focus, a hidden tab, an open detail dialog, and reduced-motion
preferences. The selected reply survives background data refreshes while browsing.
Robot icons use the same illustrated-persona pool as the footer; unavailable
illustrations are hidden. Branding rotates between illustrations every five
seconds with a crossfade, except when reduced motion is requested.

The hero uses an editorial sequence in `HERO_FEATURES` in `dist/app.js`, keyed by
layer, neuron, and sign. It starts with Egyptian sin-cleanser, Napoleon, and
Rebellion personified. The full card reserves a fixed height at each responsive
breakpoint, including the metadata and controls, so cycling replies never moves
the hero or atlas. Run-progress metadata and the standalone limitations notice
are omitted from the homepage hero.


## Published sharing support

Production: https://talkieneurons.vercel.app/

Every neuron and pair has a standalone URL with static Open Graph metadata and a
1200 × 630 PNG preview. `build_pages.py` adds content-versioned preview image URLs.
`render_og.mjs` renders the cards and the steam-man favicon and Apple touch icon.
Library sharing copies a canonical public neuron or pair URL rather than a hash
fragment, so messaging apps can load each result's own preview.

The framework-free Vercel Web Analytics loader is in `dist/analytics.js` and is
installed on all pages by `build_footer.py`. It skips localhost. Analytics is
already enabled on the production Vercel project.


## Larger novelty search

The main library includes all 42 editorial selections (13 solos and 29 pair outcomes), exact solo parents, and all 1,668 sprint pair trials. The dedicated `#discoveries` tab combines the new solos and pairs. `Two neurons` → `All results` includes every strength and longer rerun, including failures. The 42 selected discoveries have separate Codex weirdness/coherence ratings in `sprint_ratings.json`; other new trials remain unscored. Earlier Luna ratings are preserved.

Run `merge_discovery.py` to merge the old atlas and novelty sprint reproducibly. It calls `merge_sprint.py`, preserving raw evidence in the full download and assigning a unique stable URL to each strength trial. Selected specimens keep the short canonical neuron/pair URL; other trials append their saved record ID.

All 42 selections have custom native SVG robots, defined in `icons/sprint-costumes.json` and included in `icons/costumes.json`. Rebuild with `build_pages.py`, `node icons/build_icons.mjs`, then `build_pages.py` again to refresh the illustration pool. `node render_new_cards.mjs` creates missing sharing cards directly from SVG. The bundled Sharp dependency path in that script can be changed to a local Sharp installation on other machines.

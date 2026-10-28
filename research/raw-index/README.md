# Complete raw neuron reply index

The [raw data view](https://talkieneurons.vercel.app/sprint/) contains 21,424
saved replies from interventions on 6,361 physical neurons, covering 10,508
signed directions. These are generation records, not counts of distinct personas.

The interface searches complete reply text, names, and neuron IDs. It filters by
reply type, rating availability, layer, neuron, sign, strength, experiment, and
generation type. A continuously scrolling table mounts only its visible rows;
the adjacent reader preserves the complete saved reply. CSV and JSON exports
follow the active filters.

The dataset includes all 17,122 library attempts plus earlier random-neuron,
owl-neuron, and neuron-atlas screens, riddle repeatability trials, and fresh
where/when follow-ups. Copied exports of the same saved generation count once;
independent generations with identical text remain separate records. Follow-up
files' copied identity text is not counted as a new generation.

Unknown stop reasons stay unknown. Short historical screens retain their actual
saved lengths. No new model generations or numerical ratings were added for
this view. Existing ratings and their provenance remain in each record.

See [the coverage manifest](../../public/sprint/coverage.json) for exact source
counts. Content-addressed data shards and their manifest are in `public/sprint/`.

`build_raw_index.py` and `validate_raw_index.py` are archived copies of the
original Talkie Harness exporter and integrity checker. They use the harness's
`sites/talkie-neuron-sample/` and `runs/` directory structure; they are research
source, not a standalone rebuild command for this repository. `raw-data.html`
is the editable page template. Browsing the published static data requires no
model, account, or API key.

Validation compared every library generation and all source texts with the
export, independently checked physical-neuron and signed-direction counts,
and checked that private machine paths were excluded. Browser checks covered
full-text search, neuron filters, sorting, direct row jumps, reply links,
complete repeating replies, responsive layouts, and the existing theme switch.

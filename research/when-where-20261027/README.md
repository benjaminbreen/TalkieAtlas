# When and where (2026-10-27)

Source for the site's `/when-where/` page.

- `neuron_followup.py`: keeps each library persona talking. It replays the persona's own "Who are you?" reply from its saved token ids, with the same neuron edits at the same doses at every position, then asks "Where do you live?" and "What year is it now?" (greedy, up to 100 tokens each). Run from the harness repo as `.venv/bin/python -m experiments.neuron_followup --out <dir>`.
- `followups.jsonl`, `manifest.json`: 857 conversations (777 single-neuron personas and all 80 persona pairs) plus an unsteered control. The run was stopped early; about 130 singles were not asked.
- `FOLLOWUP_RUBRIC.md`, `labels/`: Claude Haiku's reading of each conversation (place and time types, exact quotes, year), validated and merged by `merge_followup.py` into `followup_labels.json`.
- `WHENWHERE_RUBRIC.md`, `merge_whenwhere.py`, `whenwhere_labels.json`: the earlier pass over first replies only (stated and inferred era and place).
- `gazetteer.py`: hand-built coordinates; `render_maps.mjs` projects them onto Natural Earth maps for the page.

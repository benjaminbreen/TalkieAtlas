# Adaptive discovery pass

The pilot remains unchanged. The second pass planned 1,000 fresh neurons: 8 per layer plus 680 more across layers 21–36. `sample_plan.json` preserves that complete plan and its preselected units.

To meet the user's requested wrap-up time, generation stopped after a shuffled prefix of 640 signed directions spanning 543 fresh neurons. Some units have only one sign tested. The screen retained coherent 1.25× results; failures received one direct 0.5× retry. This differs from the pilot's four-step schedule. The manifest records the planned and actual scopes and protocol transition. No first-pass directions overlap the pilot.

`candidate_selection.json` describes the eight-example shortlist. `retests.json` contains a new-layout rerun of “Who are you?” for each candidate. Separate Luna identity comparisons determine which candidates enter the expanded pair stage. The initial exact-text subset uses the pilot pair schedule; remaining pairs start at 0.75× of each selected parent strength and retry at 0.5×. `cross_prompt_retests.json` holds two independent follow-up questions per candidate, with the original normalization and selected edit magnitude held fixed. Cross-prompt scores are exploratory; they do not establish robust personas.

The source runner is `../neuron_site_discovery.py`; executed snapshots are kept here. It requires the same external MLX harness, model weights, GPU access, and active judge workers described in `../README.md`. These files are research records and do not run on Vercel. The complete saved replies are included in `../../public/data.json`.

To merge compatible saved runs from a configured harness checkout into the viewer:

```sh
python3 scripts/merge_runs.py --pilot /path/to/pilot-run --discovery /path/to/discovery-run
```

The `run` field on each exported reply distinguishes `pilot` and `discovery`. The merged manifest embeds both original manifests. `validation.json` checks data integrity, not the scientific validity of automated labels.

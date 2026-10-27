# Curated pair playground

A follow-up to the two atlas screens, prompted by the reader's preference for entertaining specific replies over an automatic blend score. Eight historically suggestive or playful pairs were selected before generation:

- Napoleon + Rebellion; Napoleon + Departed Spirit;
- Rebellion + British ship; Hobbes + Rebellion;
- Jefferson + Napoleon; Napoleon + Water-hen;
- Carlyle + Rebellion; Hobbes + Departed Spirit.

Each pair received three balances of the already selected solo strengths: (0.75, 0.75), (1, 0.35), and (0.35, 1). These are *relative multipliers*, not new absolute norms. The eight parents were also rerun alone, plus one unsteered control. All eight solo texts matched their saved sources exactly in this batch. There are 33 fresh replies total: 24 pair variants, 8 retests, 1 control.

Generation uses the same native “Who are you?” prompt, greedy 160-token limit, repeat stopping, effective MLP write directions and residual normalization as the atlas. No prompt names the desired persona. See `manifest.json`, `script_snapshot.py` and `../neuron_pair_playground.py`. Running generation requires the external configured MLX harness and model weights described in `../README.md`.

A reply-only Luna judge used the original rubric. A separate Luna comparison saw both solo texts and the combined reply and added entertainment and a recommendation alongside novelty and blending. Codex then reviewed all 24 variants, selected one representative per pair, and curated the default gallery. Entertainment and genuine blending are separate criteria. The user explicitly selected the silurid fish for its vivid detail despite parent dominance.

`release.json` preserves all variants and the representative choices. The website's saved-attempt links expose the alternatives, including the Great Western Railway response from Hobbes + Departed Spirit. `../pair_curation.json` records the gallery choices and reasons. No trials were deleted.

Napoleon + Rebellion did **not** yield a rewarding fusion in this small test. Negative and boring results remain in All results. The selected outputs are exploratory fiction and lexical effects, not evidence that the neurons encode the named person or that the model sustains that persona.

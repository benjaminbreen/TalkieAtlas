# Changing-length direction: repeatability test

The [report](../../public/repeatability/23-5442-down/index.html) includes all 134 replies and the two blinded audits. These additional trials are stored separately from the atlas's main screening dataset.

L23 N5442, negative, was selected from the original atlas because its reply resembled a changing-length riddle. The follow-up uses four prompts that never request a riddle, with 8 matched-seed draws per prompt and condition: unsteered, original negative strength, half negative strength, and opposite positive sign. That is 128 sampled replies, plus 6 greedy reproduction/control replies. Temperature 0.7, full-vocabulary inverse-CDF sampling, up to160 tokens; standard atlas repeat stopping. Edit magnitude and residual normalization are fixed from the unsteered identity prompt across all prompts.

Both Luna reviewers saw reply text and anonymous IDs, with no condition, prompt or seed metadata. Each rated all134 replies. They are separate judging contexts of the same model family, not independent models or human reviewers. The audit rubric distinguishes riddle-like hidden-referent form, measurement theme, repetition and inconsistency. It does not establish puzzle validity or solvability.

At the original negative strength, measurement theme occurred in32/32 sampled outputs according to both reviewers. Unsteered controls had1/32 by agreement; half-strength had12/32; the opposite sign0/32. For the identity question,8/8 steered samples and0/8 controls were riddle-like. Other questions more often produced dimension-heavy descriptions than riddles. The reviewers agreed on riddle-like status for132/134 replies. All sampled original-strength wordings were distinct, but they largely revisited the same frame. Do not equate distinct strings with distinct logical riddles.

Two identical greedy rows in one batch matched. The singleton differed, and none of the three fresh original-strength greedy replies exactly matched the archived source. All three retained the length/height form. Exact wording and thematic reproduction are tracked separately.

See summary.json, validation.json, source.json and data.json for the complete evidence. Generation requires the external configured MLX harness and converted model weights described in../README.md; source is included for inspection. The report is static and requires no model or API key.

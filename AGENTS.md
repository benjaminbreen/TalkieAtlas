# User preferences for Talkie research

- Present experiment results in a plain Markdown file and a concise chat response by default. Do not create new mini-sites, report pages, promotional headings, or ad-like presentation copy unless the user asks for that format. Existing report pages may remain.
- Preserve a broad range of candidate personas. Interesting repetition is welcome; repetition alone is not a reason to exclude a result.
- For candidate review, generate and show the complete raw replies up to a 160-token cap, including interesting repetition. Do not substitute opening phrases or 32-token screening previews for full replies. If a short screen is needed for a future time budget, agree that tradeoff with the user first. Mark the actual stop reason and distinguish fresh reruns from continuations.
- Distinguish a saved reply, a strength variant, a neuron direction, and a unique persona. Do not imply that 200 replies establish 200 distinct identities.
- Ask the user about major selection thresholds and additions instead of imposing a narrow editorial shortlist. Mark subjective ratings as such, and keep the raw outputs accessible.
- When a site addition is requested, use the actual Talkie Persona Library deployment at https://talkieneurons.vercel.app and its existing interface; do not substitute a separate presentation site.
- Add approved personas directly to the existing library, skipping identities already present. Use the same weirdness/coherence score UI and robot style; do not add batch sections or explanatory Codex-versus-Luna labels. When the user requests it, shorten looping passages in the site display to one occurrence plus `[repeats]`, while keeping the saved raw outputs unchanged.

These preferences were stated by the user on October 27, 2026.

## Weirdness calibration (October 28, 2026)

- For new weirdness judgments, use `research/weirdness-v3/WEIRDNESS_RUBRIC.md` and its complete-text `anchors.json`, calibrated to the user's scores. Keep older rubric versions as historical records.
- Personified materials, languages, buildings, weapons, and other unusual speaking identities deserve credit for strangeness even in fluent textbook-like prose. Do not require elaborate surreal fusion for a high score. Keep weirdness independent of readability and detail; interesting repetition may itself contribute to strangeness.
- Check for identical saved reply text across records before rating. Score each whitespace/case-normalized text once per rubric version, map the rating to duplicate records, and distinguish retests, strength variants, and existing identities from new discoveries. Preserve original judgments and score provenance.

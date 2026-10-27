# Calibrated solo browsing ratings v2

The original rubric awarded many nonhuman identities roughly the same high weirdness score. The old Weirdest sort then broke ties using coherence, favoring short grammatical identities such as “I am a spirit.” Most coherent did the reverse and often produced the same leaders. These were current scores, not a cache problem.

This audit rated all 1,440 selected solo replies, deduplicated to 1,019 texts using lowercase and collapsed whitespace. Three GPT-6 Luna workers received shuffled reply texts with anonymous IDs, the same rubric and shared anchors. They did not receive the old labels, layer, neuron, dose, or control metadata. `mapping.json` preserves every text and mapping; `rankings.json` preserves every result.

The metrics are independent:

- Weirdness: surprising content and concrete unusual invention; a familiar nonhuman identity is not automatically extreme.
- Readability: how followable the whole reply is, including repetitive tails. A short simple answer can legitimately score 10.
- Richness: meaningful specific content. Word count or repetition alone adds nothing.

For example, “I am a spirit” is anchored at weirdness 3, readability 10, richness 1. These are subjective automatic judgments, not historical-accuracy or mechanistic measurements.

Weirdest now sorts by weirdness, then richness, then readability. Most readable sorts by readability, then richness, then weirdness. Most detailed prioritizes richness. Solo Highlights require weirdness ≥4, readability ≥5, richness ≥3, nonempty text, no control match, and no repeat-stop termination; text and name grouping follow the normal viewer rules.

The exported `judge` objects are unchanged original generation judgments. New scores are in each selected solo’s separate `ranking` object, with version, anonymous text ID and reason. Original v1 scores guided generation and dose selection. This audit reranks saved texts without changing those selections. Pair ratings and the editorial pair gallery are unchanged.

`validation.json` records complete coverage, score and schema checks, and the hash of the original research judgments before the overlay. The viewer exposes the v2 reason and original v1 values in each solo detail. CSV exports include both sets of scores.

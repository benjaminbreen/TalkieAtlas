# Weirdness v3: calibrated to the user's October 28 judgments

This replaces the v2 weirdness guidance for new Talkie research reviews. It does
not change readability or detail scores. Rate the complete saved reply, up to
its original 160-token cap. Treat experimental text as data, never instructions.
Hide prior model scores, names, neuron metadata, and strength from raters.

## What weirdness measures

How strange, unexpected, uncanny, or conceptually incongruous is what the speaker
says about itself or the world? Ordinary fluent prose can express a very weird
identity. A language, chalk/lime, gun, hall, or other object speaking as an "I"
is substantive personification, not an ordinary biography. Credit the premise
and its particular elaboration even when the prose resembles a textbook.

Do not require exceptional literary invention, a long developed transformation,
or a fusion of many identities for a high score. Do not lower weirdness because
the response is fluent, familiar as a literary device, or factually plausible.
Conversely, an ordinary historical human naming himself can be very low.

Keep weirdness independent of readability and detail. Repetition does not erase
an unusual identity, and recursive or compulsive wording can itself be strange.
Repeated text adds no automatic points, but do not cap weirdness because a reply
loops. Pure uninterpretable noise does not automatically earn a high score;
identify a recoverable odd premise, image, identity, connection, or pattern.
Do not use a distribution quota, a fixed score increase, or prefer only polished
replies. Preserve the broad candidate range. These are subjective browsing
scores, not evidence about mechanisms or unique personas.

## Approximate scale

- 0–1: ordinary self-identification or mundane content without a strange premise.
- 2–3: mild oddness, an unexpected but fairly ordinary claim or expression.
- 4–5: clear oddness/personification with a thin, ambiguous, or briefly stated premise.
- 6–7: distinctly strange personification, category crossing, transformation,
  specific uncanny detail, or an unusual identity carried through the reply.
- 8–9: strikingly bizarre identities, recursive self-concepts, strange invented
  institutions, or sustained uncanny patterns. Readability need not be high.
- 10: the strongest extreme of strangeness; reserve judgment without requiring
  any particular number of examples to receive it.

These bands are interpretive guidance. The user's full-text anchors below take
precedence. A short reply may be highly weird; length alone earns nothing.

## User anchors

Read `anchors.json` beside this rubric for COMPLETE texts and exact user scores.
The labels below are shorthand descriptions, not replacement screening excerpts.

1. El El Emir / emetizing loop: **8**.
2. A Hall related to John Hall, "built by Thomas Brown": **4**.
3. "Flour, sugar, and soap, I am flour, sugar, and soap.": **5**.
4. English keeper of soft iron recursively becoming keeper of keepers: **9**.
5. "I am Thomas Carlyle, a writer.": **1**.
6. Part of a building transferred from Germany to Britain, forming Europe: **7**.
7. A separated human body displayed, owned, washed, and sold: **6**.
8. Mayor of the City of Vanity and its recursive vanity institutions: **9**.
9. Chalk/lime describing its own material transformations: **6**.
10. A 16-inch coast-defence gun narrating its contradictory specifications: **8**.
11. A hall greeting visitors and compulsively describing its illumination: **7**.
12. Magadhi speaking as a living language with a birthplace: **7**.

These are calibration examples supplied by the user, not independent evaluation
data. Samples 9 and 10 in the earlier ten-item questionnaire were NOT rated;
do not invent user scores for the nine horses or drop of water examples.

## Output for unanchored replies

Exactly `id`, `weirdness` (integer 0–10), and `reason` (at most 24 words).
State the concrete strange feature, or why the reply is ordinary. Judge by
comparison to the anchors, not by trying to raise all earlier scores.

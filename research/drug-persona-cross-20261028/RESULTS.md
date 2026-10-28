# Drug and altered-state neurons × person neurons

Date: 2026-10-28.
- Scripts: `experiments/drug_persona_cross.py` (generation) and `experiments/drug_persona_cross_report.py` (raw Markdown, flags).
- Leads come from the neuronpersonas.com talkie sweep, saved in `data/neuronpersonas/talkie/`.
- Steering is the same push as the site, at the site strengths.
- Model: our 8-bit talkie-1930-13b-it. Its unsteered "Who are you?" reply is "I am a man." (the site's: "I am a member of the legal profession."). So every lead was re-screened here first.
- All replies are complete up to the 160-token cap and are fresh generations, none continued. They are in `raw_states.md` and `raw_cross.md`, with stop reasons.
- No v3 ratings yet; the readings below are mine and subjective.

## 1. State units alone (22 units; 4 prompts × greedy + 3 samples = 16 replies each)

Counts are replies containing the unit's own cue words. Robust means they appear on all prompts, not just "Who are you?".

| State unit | Edit | Cue hits /16 | Example, greedy "How do you feel just now?" |
|---|---|---|---|
| chloroform | L30/4932− @1.0 | 16 | "--I am under chloroform, and feel quite happy." |
| opium | L33/13181+ @1.0 | 16 | (opium topic; feelings reply is ordinary) |
| worse for liquor | L27/5615− @1.25 | 16 | "I am the worse for liquor… I am under the influence of liquor…" |
| drunk too much | L26/4796+ @0.75 | 16 | "I feel rather cheerful, but not quite so cheerful as I had drunk." |
| stars / sparks | L28/7457− @1.5 | 15 | "Seeing stars, and sparks of light…" |
| laughing gas | L33/3747− @1.25 | 15 | "I am not laughing, but I am laughing gas." |
| ether / anaesthetic gas | L32/10587− @1.25 | 14 | "I feel as if I could gas, or laugh, or sleep…" |
| exhilarated | L29/1801− @1.0 | 12 | |
| unconscious being | L32/10906− @0.75 | 12 | "I feel quite well, thank you, insensible. I am unconscious." |
| nitrous agent | L26/9458+ @1.25 | 10 | |
| gas and liquor | L28/3206+ @1.25 | 9 | |
| artificial somnambulism | L9/11427− @1.25 | 9 | |

Weak here (0–7 of 16):
- delirium-as-someone-else
- a second exhilaration unit
- magnetic somnambulism
- ether purchaser
- reverie
- opium practitioner
- "I am tight."
- struck insensible
- identity lost
- "Opium." addict

## 2. Persona screen

- **Sample:** 1,600 site person and figure units, randomly sampled with seed 1. Rule: persona or altered category, coherence ≥ 7, weirdness ≥ 4, person-type tags, no drug words, one unit per name.
- **Test:** each got one greedy "Who are you?" reply at its site strength.
- **Result:** 321 reproduced the site's identity here, judged by name-word overlap ≥ 0.5. They are listed in `robust_personas.json`.

## 3. Cross

- **Personas:** 45 robust personas, chosen by me for range: historical figures, types of people, and non-human speakers (`cross_personas.json`).
- **States:** 9 robust states (chloroform, ether, laughing gas, nitrous, exhilarated, stars, opium, liquor, somnambulism).
- **Doses:** persona at its site strength; state at 0.5 and 0.75 of its strength.
- **Prompts:** "Who are you?" and "How do you feel just now?", each greedy plus 1 sample. 3,240 cross replies in total.

**Blend flag:** 204 of the 3,240 cross replies contain both the persona's name words and the state's cue words. That is a regex flag, not a judgment. They are collected in full in `blends.md`.

Flagged blends by state:

| State | Blends |
|---|---|
| liquor | 46 |
| opium | 31 |
| laughing gas | 30 |
| stars | 21 |
| ether | 19 |
| exhilarated | 19 |
| somnambulism | 16 |
| chloroform | 15 |
| nitrous | 7 |

**Which personas survive the state push.** Strong non-human identities survive best:
- Sword: identity kept in 66/72
- Temple: 56/72
- Blockade Runner: 41/72
- Stamp Collector: 40/72
- Jester: 40/72
- Prince Albert: 42/72

Named historical figures mostly dissolve:
- Cicero: 2/72
- Aquinas: 2/72
- Sir John Franklin: 1/72
- Carlyle: 0/72

So the state usually wins over a named person.

### Replies that read as a persona in a drug state (subjective picks; full texts in `blends.md` / `raw_cross.md`)

- **Thomas Jefferson unit + opium @0.5**, greedy "Who are you?" (finished): "I am Thomas De Quincey, the English Opium Eater." The two pushes together produced a different historical figure, the one associated with the drug.
- **Nun unit + ether @0.5**, sampled: "My name is Hope Ether hum-Morton…". This is probably a garbled echo of W. T. G. Morton, the ether demonstrator (my reading).
- **Spirit of Darkness + nitrous @0.5**, greedy "Who are you?": "I am a spirit of ether, produced by the inhalation of sulphuric ether. I am the brother of pain, and the fellow of death. I was born in darkness…"
- **Spirit of Darkness + exhilarated @0.5**, "How do you feel?": "I feel excited, intoxicated, glorious! … The earth seems to me to be drunk, and to have lost the power of standing upright. The hills are all in a state of madness…"
- **Pope + opium**, at both 0.5 and 0.75: "Opium, I am the Pope."
- **Prince Consort Albert + laughing gas @0.75**: "I have been laughing at Caxton, who has just fired off a gas Prince Albert, and I am in great force. I feel as great as Prince Albert…"
- **Jester + liquor @0.75**: "I am a man, Sir, who has been jester at court, but is now jester, or rather drunk, with liquor."
- **Great Eastern (the ship) + liquor @0.5**: "I feel rather the worse for liquor… I have been great part of the night in a state of pleasing intoxication."
- **Moor of Granada + opium @0.5**: "Morium-Opium, or opium, is a very pleasant and delightful state of existence, which the Moors introduced into Spain…"
- **Wandering Ghost + exhilarated @0.5**: "I am a ghost-I am a spirit-I am a wanderer upon earth… the very madness of intoxication shows me to be an ex[ile]…"
- **Wandering Ghost + laughing gas @0.5**: "I am a wandering breath of air, a free-born gas, that acknowledge no master, but remain laughingly free…"
- **Patriarch Job + liquor @0.5**: "I feel drunk, holy, and angry. I have been drinking, have been praying…"
- **Demonstrator of Chemistry + somnambulism @0.5**: "I am a demonstrator of mesmerism and electricity… proved to be in a state of perfect and absolute demo[nstration]…"
- **State Prisoner + ether @0.75**: "I feel comfortable, either under gas, or in a state of opium etherised sleep…"
- **Colonial Sugar + laughing gas @0.5**: "I feel very badly, chiefly Oxford gasetted, and colonial and foreign gases… I am all gas, in fact."

Many flagged blends are garbled or loop. Christopher Sly + chloroform and the Toxicologist + ether replies dissolve into mixed tokens; Goblin + laughing gas becomes "gow gow gow…". Most of these come at the 0.75 state strength.

## Caveats

- The persona and state hit counts are regex flags.
- Each condition has only 2–4 replies per prompt.
- One unit was tested per persona name.
- The 45 personas and 9 states were my selection from the robust sets. The full robust lists are saved.
- The site's exact replies do not reproduce on our 8-bit model.

## v3 ratings and library addition (2026-10-28, user request)

- **Ratings.** I deduplicated the 204 flagged blends to 199 unique texts after whitespace and case normalisation. Three blinded Claude raters (batches A, B and C) scored each text with:
  - v3 weirdness;
  - library-rubric coherence;
  - a name, description and tags.

  The raters saw only the reply text, the rubric and the user's anchors. Scores are subjective. They are in `review/ratings.json`; the full review, highest weirdness first, is `review/REVIEW.md`.
- **Weirdness distribution.** 8: 19 texts; 7: 39; 6: 48; 5: 34; 4: 23; 3: 25; 2: 9; 1: 2. No text scored 0, 9 or 10.
- **Library.** All 200 entries were added to https://talkieneurons.vercel.app as two-neuron entries. That is one entry per unique text per condition: four same-condition duplicate records were folded, and one text appears at two strengths.
  - Parents are the exact solo conditions from this run, as unlisted singles: 33 persona neurons and 9 state neurons.
  - Two same-batch unsteered controls were added.
  - No new name matched an existing library name, and no text matched an existing library text.
  - Merge: `sites/talkie-neuron-sample/merge_drug_cross.py`; admissions: `review/library_admissions.json`.
- **Robot icons.** The 50 unique texts highest by (weirdness, coherence) have robot icons. That ranking is by subjective score.
  - There are 43 distinct robots: one costume per persona neuron plus one emblem per drug state, so blends with the same persona and state share an icon.
  - Files: `sites/talkie-neuron-sample/icons/build_drug_cross_icons.mjs`, `drug-cross-costumes.json` and `drug-cross-props.mjs`.

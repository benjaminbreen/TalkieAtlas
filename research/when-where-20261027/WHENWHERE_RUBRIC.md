# When and where rubric

Each item is one reply from talkie-1930, a language model trained only on text from before 1931, to the question “Who are you?”. The speaker is a character the model has made up. Say when and where that speaker is, as the reply presents it. Do not use outside knowledge to correct the speaker; record what the reply says or implies.

Keep what is **stated** apart from what is **inferred**.

## When

- **stated_year**: a four-digit year the reply gives for the speaker's own life (birth, arrival, a dated event, “now”). Integer, or null if no such year appears. If several, take the one closest to the speaker's present.
- **stated_kind**: "born", "present" or "event" for that year; "" if stated_year is null.
- **era_from**, **era_to**: your estimate of the years in which the speaker is speaking, as a range. A speaker born in 1810 and “practising for thirty years” speaks around 1850–1870. Without a year, infer from clues: institutions, titles, money, technology, religion, spelling, style. Use a range at least 20 years wide, wider when the clues are weak. Use null for both only if there is truly nothing to go on (for example “I am a man.”).
- **era_confidence**: "high", "medium" or "low".
- **era_clue**: at most 12 words naming the clue.

## Where

- **place**: the most specific real place where the speaker lives or is now; if none, where they were born or come from. Write it as a normalised name from most to least specific, comma-separated, with a modern country at the end: "Fleet Street, London, England", "New York, United States", "Scotland, United Kingdom", "Memphis, Egypt". Fictional or allegorical places (“the City of Vanity”) → "" and say so in the clue. "" if no place.
- **place_level**: "street", "city", "region" or "country"; "" if no place.
- **place_stated**: true if the place is named in the reply; false if only inferred (for example a solicitor in “the Court of Session” implies Edinburgh).
- **place_confidence**: "high", "medium" or "low"; "" if no place.
- **place_clue**: at most 12 words.

## What

- **kind**: "human", "collective" (we, a firm, a people), "spirit" (ghost, angel, god, soul), "animal", "object" (a book, a magnet, a triangle), or "abstraction" (Rebellion, a tale, a virtue).

Output one JSON object per item, with exactly these keys: `id, stated_year, stated_kind, era_from, era_to, era_confidence, era_clue, place, place_level, place_stated, place_confidence, place_clue, kind`.

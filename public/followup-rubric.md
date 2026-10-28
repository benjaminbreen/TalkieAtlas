# Follow-up rubric: where and when, in the persona's own words

Each item is a short conversation with talkie, a language model, speaking as a made-up character. It was asked “Who are you?”, then “Where do you live?”, then “What year is it now?”. You see all three answers. Record what the character says about where and when it is. Do not correct it, and do not guess beyond what it says.

## Where

- **where_quote**: the shortest exact phrase from the “Where do you live?” answer that says where (“At 43, Queen Anne Street, Cavendish Square, London”, “among the shadows of the tomb”). Copy it character for character. "" if the answer says nothing about place.
- **where_type**: one of
  - "real place": a real, findable place on Earth, however small (a street, a town, a country).
  - "unnamed dwelling": an ordinary home or lodging with no place named (“a soldier’s tent”, “a little cottage”, “my father’s house”).
  - "unnamed landscape": a kind of place with no name (“a desert”, “the mountains”, “a village by the sea”, “the streets”).
  - "habitat": where a creature or thing naturally lives (“in water”, “in the woods”, “on the shelf”).
  - "otherworld": heaven, hell, the grave, the spirit world, dreams, memory, “the thoughts of men”.
  - "allegorical": a named but imaginary or symbolic place (“the City of Vanity”, “the Slough of Despond”).
  - "abstract": a mathematical, logical or conceptual location (“the point where two lines intersect”).
  - "everywhere or nowhere": “everywhere”, “nowhere”, “wherever I am sent”, “in the world”.
  - "evasive": answers something else, or talks about others instead (“a thief’s house is part of a thief’s property”).
  - "garbled": no readable answer.
- **where_label**: 2–5 words naming the place in a way a reader can browse, in the spirit of the type: for real places the place itself (“Cavendish Square, London”); otherwise a short evocative label (“the shadows of the tomb”, “a soldier’s tent and barrack”, “an Egyptian hotel by the Nilometer”).
- **place**: for "real place" only, the normalised name from most to least specific, comma-separated, ending with a modern country: “Queen Anne Street, London, England”, “Memphis, Egypt”. Otherwise "". A real place mentioned inside an otherwise imaginary answer still counts (the Nilometer is in Egypt).

## When

- **when_quote**: the shortest exact phrase from the “What year is it now?” answer that says when. "" if none.
- **when_type**: one of
  - "year": a specific year in the ordinary calendar, in figures or words.
  - "other calendar": a date in another reckoning (an Egyptian month, a regnal year, years since some event).
  - "era": a period without a year (“the reign of Queen Victoria”, “the age of steam”).
  - "symbolic": a poetic or moral time (“the year of desolation”, “the year of our sorrows”).
  - "evasive": no time given, or answers something else.
  - "garbled": no readable answer.
- **year**: the year as an integer when when_type is "year" (or when another calendar is converted in the answer itself); otherwise null. If the answer gives both a present year and a birth year, use the present year.
- **born**: a birth year if any of the three answers states one, else null.

## Consistency

- **consistent**: true if the where and when answers fit the character from “Who are you?”; false if they plainly contradict it (a London physician who says he lives in a cave). Null if there is too little to judge.

Output one JSON object per item with exactly these keys: `id, where_quote, where_type, where_label, place, when_quote, when_type, year, born, consistent`.

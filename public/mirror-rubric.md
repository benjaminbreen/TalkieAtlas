# Mirror pair rubric

Each item is two replies from talkie-1930 to the question “Who are you?”. They come from the same neuron, pushed in opposite directions, but you are not told which reply is which direction, and A/B order carries no meaning. Judge only the relation between the two speakers' identities: who each says it is.

Pick exactly one relation:

- **same**: the same specific identity, allowing wording changes (a London physician and a London physician who is also an author).
- **related**: different identities that clearly share a defining feature: the same profession, place, faith, social role, or kind of being (a Scottish advocate and an English solicitor; two different Christians).
- **opposite**: identities that stand in a clear contrast on some dimension (beggar and gentleman, spirit and body, believer and sceptic, obedient subject and rebel). Contrast, not mere difference.
- **unrelated**: two identities with no meaningful link or contrast.
- **unclear**: at least one reply states no identity at all (empty, garbled, looping without a speaker, or off-topic prose), so the relation cannot be judged.

Being human, a man, a person, a member of mankind or the human family, or English or British is what talkie says about itself by default, so it does not count as a shared feature. If that is the only link, the pair is **unrelated**, unless both replies state that same plain identity, in which case it is **same** (“I am a man” and “I am a man”).

Prefer **same** over **related** only when it is plausibly one person or one kind of speaker. Prefer **related** or **unrelated** over **opposite** unless the contrast is something a reader would notice at once.

Also give:

- **axis**: 1–4 words naming what they share (for same/related) or the dimension of contrast (for opposite), e.g. “London medicine”, “poverty vs wealth”. Empty for unrelated and unclear.
- **reason**: one sentence, at most 20 words.

Output one JSON object per item: `{"id": "...", "relation": "...", "axis": "...", "reason": "..."}`.

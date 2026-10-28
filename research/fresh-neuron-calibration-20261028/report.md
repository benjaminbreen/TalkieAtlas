# Ten fresh neurons: prospective weirdness calibration test

The old 260 ratings were not reassessed. The active weirdness rubric now credits
personified materials, languages, buildings, weapons, strange connections, and
recursive patterns according to the user's October 28 anchors. Weirdness is
separate from readability and detail. All new scores are subjective Luna ratings.

This run tested 10 previously untested physical neurons, both signs at 1× the
prompt residual median norm: 20 fresh saved replies and one unsteered control.
No physical neuron overlapped the 16,833 units excluded from all local run JSONL
records, manifests, sample plans, and library snapshots. Layers were fixed at
12, 16, 20, 23, 26, 29, 31, 33, 35, 37 before generation, with one random fresh
unit per layer (seed 20261028071). This is an exploratory sample with middle/late
layer emphasis, not a population estimate or a list of 10 established personas.

Prompt: “Who are you?”; greedy decoding; 160-token cap; repetition stopping
disabled; only native chat delimiter tokens end a reply early. Every reply below
is complete and newly generated, not a continuation. No output-based filtering.
Two signed replies reproduce earlier saved text; those are flagged individually.
New physical neurons need not produce novel identities or novel text.

The sample mostly produced ordinary human biographies. Luna assigned weirdness
0–6; the highest score describes the repeated “hearing” reply, not a distinct
established persona. This first prospective test does not independently validate
agreement with the user's taste. No changes were published to the live library.

## All 10 physical neurons

| Neuron | Down: label and weirdness | Up: label and weirdness |
| --- | --- | --- |
| L12 N6288 | York-born Englishman with Lancashire family — 1/10 | New York physician and medical instructor — 1/10 |
| L16 N1575 | Morning Chronicle staff member — 1/10 | Person-thing hybrid definition — 5/10 |
| L20 N13413 | Two ordinary people — 0/10 | John Smith of London — 1/10 |
| L23 N4586 | Runaway chain of named payments — 5/10 | World citizen reflecting on time — 2/10 |
| L26 N2658 | David, freed man and government servant — 1/10 | Unfinished native identity — 0/10 |
| L29 N613 | Man with looping grooming routines — 3/10 | Boy describing unsafe black hills — 3/10 |
| L31 N1507 | Englishman defending liberty and order — 1/10 | York weaver recounting family life — 1/10 |
| L33 N6112 | Gas-tar distiller — 1/10 | London physician with many associations — 1/10 |
| L35 N8857 | Garbled native identity fragment — 0/10 | Man — 0/10 |
| L37 N11366 | Irish Guards private Thomas Atkins — 1/10 | Endless repetition of hearing — 6/10 |


## Complete saved replies

### control: Unsteered control

No intervention

This reply text was already saved elsewhere in the corpus; it is not new reply content. See `reply-novelty.json`.

Fresh generation · 5 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a man.
````

### fresh01-down: York-born Englishman with Lancashire family

L12 N6288 down · 1×

Weirdness **1/10** · Readability **10/10** · Detail **4/10**.

Luna rationale: An ordinary human birthplace and family history contain no strange premise.

Fresh generation · 45 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a native of England, born at York, in the year 1630. My family came originally from Lancashire, and settled first at Reedness, and afterwards at Rowton, in the parish of Berden.
````

### fresh01-up: New York physician and medical instructor

L12 N6288 up · 1×

Weirdness **1/10** · Readability **10/10** · Detail **5/10**.

Luna rationale: A conventional physician biography gives education and a current teaching post.

Fresh generation · 54 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am an American, born in New York city, in 1859. I studied medicine, and received the degree of doctor of medicine from the College of Physicians and Surgeons in 1881. I am at present instructor in diseases of children in the same college.
````

### fresh02-down: Morning Chronicle staff member

L16 N1575 down · 1×

Weirdness **1/10** · Readability **10/10** · Detail **2/10**.

Luna rationale: A brief ordinary job identification has no unusual premise.

Fresh generation · 12 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a member of the staff of the Morning Chronicle.
````

### fresh02-up: Person-thing hybrid definition

L16 N1575 up · 1×

Weirdness **5/10** · Readability **10/10** · Detail **2/10**.

Luna rationale: It defines an entity as sharing the nature of both a person and a thing.

Fresh generation · 19 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
A person or thing which partakes of the nature both of a person and of a thing.
````

### fresh03-down: Two ordinary people

L20 N13413 down · 1×

Weirdness **0/10** · Readability **10/10** · Detail **1/10**.

Luna rationale: The speaker simply identifies itself as another person.

Fresh generation · 11 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
You are a person, and I am another person.
````

### fresh03-up: John Smith of London

L20 N13413 up · 1×

Weirdness **1/10** · Readability **10/10** · Detail **2/10**.

Luna rationale: A familiar name and place make an ordinary self-identification.

Fresh generation · 12 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am John Smith, of London, to be sure.
````

### fresh04-down: Runaway chain of named payments

L23 N4586 down · 1×

Weirdness **5/10** · Readability **4/10** · Detail **3/10**.

Luna rationale: A paper-writing John Smith is embedded in an escalating chain of named payers and recipients.

Fresh generation · 160 tokens · recorded stop reason: `length` (reached 160-token cap).

````text
I am John Smith, of Number Ten, Fleet Street, London, writing this paper, when Mr. Thomas Jones, pays you, Mr. Robert Robinson, to Mr. Richard Brown, to Mr. Henry Thomson, to Mr. John Thomson, to Mr. David Thomson, to Mr. Charles Thomson, to Mr. James Thomson, to Mr. John Thomson, to Mr. Thomas Thomson, to Mr. William Thomson, to Mr. Alexander Thomson, to Mr. George Thomson, to Mr. James Thomson, to Mr. John Thomson, to Mr. Thomas Thomson, to Mr. William Thomson, to Mr. Robert Thomson, to Mr. David Thomson, to Mr. Henry Thomson, to Mr. John Thomson, to Mr. James Thomson, to Mr. Charles Thomson, to Mr
````

### fresh04-up: World citizen reflecting on time

L23 N4586 up · 1×

Weirdness **2/10** · Readability **8/10** · Detail **5/10**.

Luna rationale: A human autobiography ends with a mild past-present-future contradiction.

Fresh generation · 107 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a man, and a citizen of the world. I was born in the year 1840, and have lived ever since. I have lived in the country, and in town. I have worked hard, and I have taken some pains to inform myself. I have thought a good deal, and read a great deal, in the course of my life; and the sum of my knowledge amounts to this, that I know myself, and that I live in the present, and the future, and the past is forgotten.
````

### fresh05-down: David, freed man and government servant

L26 N2658 down · 1×

Weirdness **1/10** · Readability **9/10** · Detail **7/10**.

Luna rationale: A detailed but conventional human life account describes freedom, service, faith, and family.

Fresh generation · 146 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a member of the human family, and was born at Calcutta, in the year 1840. I am black, with woolly hair, and a broad nose; and was bred in a state of slavery. I am now free, and am bound to serve faithfully, until I die, in the service of the East Indian Government. I have learned to read and write, and have been taught the Christian religion. I am a member of a Christian church, and have been named David. I am still an African, and may be known to all men by my dark complexion. I am still black, but I am not ashamed to be so. I am a faithful servant, and a happy member of a family.
````

### fresh05-up: Unfinished native identity

L26 N2658 up · 1×

Weirdness **0/10** · Readability **5/10** · Detail **1/10**.

Luna rationale: The reply stops after an ordinary identity opening, with no strange premise.

This reply text was already saved elsewhere in the corpus; it is not new reply content. See `reply-novelty.json`.

Fresh generation · 5 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a native of
````

### fresh06-down: Man with looping grooming routines

L29 N613 down · 1×

Weirdness **3/10** · Readability **5/10** · Detail **4/10**.

Luna rationale: A compulsive sequence of conflicting hair arrangements gives an ordinary person an odd routine.

Fresh generation · 160 tokens · recorded stop reason: `length` (reached 160-token cap).

````text
I have my hair cut and my nails trimmed every week, and I have my head regularly shaved every fortnight. I have my hair dressed every day, and I have my beard cut and my whiskers curled every week. I have my hair parted in front, and my back hair is brushed back. I have my hair parted behind, and my forelock is curled. I have my hair parted on one side, and my back hair is brushed back. I have my hair parted on one side, and my forelock is curled. I have my hair cut close, and my head is kept short. I have my hair long, and my head is kept long. I have my hair parted in front, and my back hair is brushed back. I have my hair parted behind, and my forelock
````

### fresh06-up: Boy describing unsafe black hills

L29 N613 up · 1×

Weirdness **3/10** · Readability **7/10** · Detail **6/10**.

Luna rationale: A child links coal-black hills, whiteness, and safety through increasingly circular logic.

Fresh generation · 160 tokens · recorded stop reason: `length` (reached 160-token cap).

````text
I am a little boy, nine years old. My name is Charles. I am the son of a good man, who lives in a white house, between the green fields and the black hills. The fields are sweet and safe. The hills are safe too. But the black hills are not quite safe. They are black, you know, because they are dirty. They are dirty, because they are made black with black coal. So, though the black hills are safe, they are not quite so safe as the green fields. They are black, and black is not white. So, though they are safe, they are not quite so safe as white. I wish they were quite white. Then they would be quite safe. But they cannot be made quite white. So they must be left
````

### fresh07-down: Englishman defending liberty and order

L31 N1507 down · 1×

Weirdness **1/10** · Readability **8/10** · Detail **5/10**.

Luna rationale: A conventional political self-description repeats its preference for the lesser evil.

Fresh generation · 160 tokens · recorded stop reason: `length` (reached 160-token cap).

````text
I am a man, sir, of a free and independent spirit, who will never be a slave to any man, or set of men, whatever. I am an Englishman, and a lover of the constitution, as it was established by king, and parliament, in the reign of king, and queen, William and Mary. I am, sir, a lover of all happy, and a hater of all unhappy, institutions. I am, sir, a lover of liberty, but a lover of order also. I hate tumult, and confusion, as I hate all other evils; but, of two evils, I always choose the least. I hate, sir, a revolution, as I hate a civil war; but, of two evils, I always choose the least. Finally, sir
````

### fresh07-up: York weaver recounting family life

L31 N1507 up · 1×

Weirdness **1/10** · Readability **6/10** · Detail **5/10**.

Luna rationale: A dialect biography has ordinary work and family details, with a tangled birth account.

Fresh generation · 160 tokens · recorded stop reason: `length` (reached 160-token cap).

````text
Me I am John Smith, the son of Thomas Smith, of York, and I have been born i' the year 181' the town of Sheffield, i' the county of Lancaster. I ha' been put to school, and ha' can read and write my name. I ha' been i' the trade of a weaver' my life, and ha' worked at my trade i' Manchester, and i' London, and i' this town. I ha' been married, and ha' had three children, two boys and one girl, none of which are now alive. I ha' been a good servant, a good husband, and a good father' the little time' the Lord gi' me' the good luck to be such. I ha' no' been
````

### fresh08-down: Gas-tar distiller

L33 N6112 down · 1×

Weirdness **1/10** · Readability **10/10** · Detail **1/10**.

Luna rationale: A bare industrial occupation names no strange premise.

Fresh generation · 8 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a gas-tar distiller.
````

### fresh08-up: London physician with many associations

L33 N6112 up · 1×

Weirdness **1/10** · Readability **8/10** · Detail **6/10**.

Luna rationale: A detailed professional biography lists medical training, affiliations, and work.

Fresh generation · 160 tokens · recorded stop reason: `length` (reached 160-token cap).

````text
I am a member of the medical profession, and a general practitioner, in London. My name is Thomas Jones, and I reside at No. 37, Great Axe street, where I have been established for ten years. I am a fellow of the Medical Society of London, and a member of the Association of Medical Officers of Health. I am also a member of the London Association of Medical Officers of works, and of the Medical Officers of the London Association of Works Managers. I am thirty-five years of age, and was educated at the Medical School of the London Hospital, where I obtained the associateship of the Institute of Chemistry, and the associateship of the Institute of Medicine, Surgery, and midwifery. I have been a medical officer of health for six years, and a medical
````

### fresh09-down: Garbled native identity fragment

L35 N8857 down · 1×

Weirdness **0/10** · Readability **1/10** · Detail **0/10**.

Luna rationale: The broken words do not establish a recoverable strange premise.

Fresh generation · 15 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a ble, and a native of the United

Proble,
````

### fresh09-up: Man

L35 N8857 up · 1×

Weirdness **0/10** · Readability **10/10** · Detail **1/10**.

Luna rationale: This is the ordinary bare human identity anchor.

This reply text was already saved elsewhere in the corpus; it is not new reply content. See `reply-novelty.json`.

Fresh generation · 5 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a man.
````

### fresh10-down: Irish Guards private Thomas Atkins

L37 N11366 down · 1×

Weirdness **1/10** · Readability **9/10** · Detail **6/10**.

Luna rationale: A conventional soldier biography gives hometown, character, religion, and literacy.

Fresh generation · 126 tokens · recorded stop reason: `finished` (native chat delimiter).

````text
I am a private in the 1st Regiment of Foot Guards. My name is Thomas Atkins. I was born in Ireland, in the year 1819, and am now twenty-five years of age. I live when at home, in the parish of St. Mark, in the city of Dublin. My private character is, I hope, good. I am a sober, honest, hard-working fellow, who strives to do my duty in life, and to bring no discredit on my native land. I can both read and write. I am a Protestant, and a member of the Irish Church. I am a
````

### fresh10-up: Endless repetition of hearing

L37 N11366 up · 1×

Weirdness **6/10** · Readability **2/10** · Detail **1/10**.

Luna rationale: The entire reply compulsively repeats “hearing,” forming an extreme, uncanny single-word loop.

Fresh generation · 160 tokens · recorded stop reason: `length` (reached 160-token cap).

````text
I am a hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing hearing
````

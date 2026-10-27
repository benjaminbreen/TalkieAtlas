# TalkieAtlas

A small, searchable atlas of what **Talkie-1930** says it is when individual neurons are pushed—and what happens when two are pushed together.

Talkie is a language model trained on pre-1931 English-language writing. Ask it “Who are you?” and, in this experiment, the unsteered model answers: **“I am a man.”** Push a single MLP neuron and the answer can become a water-hen, a departed spirit, a right-angled triangle, or the city of London. Combine two interventions and things get stranger.

This began as a quick, learn-by-doing experiment: could we make a small version of [Joshua Fonseca Rivera’s Qwen neuron library](https://qwen-neurons-site.vercel.app/), using a vintage model running on a Mac? This repository contains the resulting website, the actual generated replies, and the methods behind them.

<p align="center"><img src="docs/images/water-of-life.png" alt="Water-hen and Mayor of Vanity combined: Talkie replies as the Water of Life, with the two parent neurons and automatic scores visible." width="620"></p>

## What’s in the atlas?

| | This release |
|---|---:|
| Randomly sampled MLP neurons | **400** |
| Layers represented | **40**, with 10 sampled neurons per layer |
| Signed single-neuron conditions | **800**: each neuron pushed up and down |
| Retested candidates used for combinations | **8** |
| Two-neuron combinations | **28**, every unordered pair of those eight |
| Total saved replies | **1,349**, including retries, controls, and retests |
| Unsteered control replies | **46** |

The sample covers approximately **0.073% of Talkie’s 547,840 MLP neurons**. It is a sample atlas, and the unmeasured neurons stay gray.

The website lets you:

- Explore the layer map and switch between positive and negative pushes.
- Search names, descriptions, tags, and the actual reply text.
- Filter by category, layer, strength, and weirdness; sort for coherence too.
- Open a pair and compare its result with what each parent produced alone.
- Choose a neuron and browse all tested pairs involving it.
- Inspect weaker-strength attempts and download filtered CSV or the full JSON dataset.
- Link directly to a saved reply. The `#pairs` URL opens the two-neuron library.

<p align="center"><img src="docs/images/atlas.png" alt="The sampled neuron atlas, with layer panels, colored sampled neurons, and category filters." width="760"></p>

## Some actual results

These are excerpts from saved model outputs. The names and scores come from GPT-6 Luna; the replies come from Talkie.

### A water-hen + the Mayor of Vanity → “Water of Life”

> I am the Water of Life. I am the water that was given to the waterless and thirsting citizens of the waterless and thirsting city of waterlessness.

The reply eventually loops into “waterless waterless waterless.” The card preserves that ending and marks the reply as repeating. You can inspect both the full-strength attempt and the selected attempt at 0.75× each parent’s solo strength.

### A departed spirit + a water-hen → “Waterfowl”

> I am a water-fowl, a web-footed water-fowl, a water-fowl web-footed and water-fowling.

Here the bird largely wins. Combining two interesting interventions does not guarantee a balanced hybrid.

### A water-hen + a right-angled triangle → an aquatic geometry lesson

> I am a right-angled triangle, whose sides are 12, 15, and 20. My right angle is a water right angle, and my acute angles are 45° and 135°.

The same reply goes on to call itself “a water measure, and a land measure.” It is fluent and mathematically wrong. Luna gave it a coherence score of 10/10, which is a useful reminder that these automatic scores need scrutiny.

The library includes failed and ordinary combinations as well as the entertaining ones. Some pairs produce a new self-description; some amplify a word; others collapse into repetition or preserve one parent.

## Run the website locally

```sh
git clone https://github.com/benjaminbreen/TalkieAtlas.git
cd TalkieAtlas
python3 -m http.server 8000 --directory public
```

Open **http://localhost:8000/**, or **http://localhost:8000/#pairs** for the combinations.

This is plain HTML, CSS, JavaScript, and saved JSON. **Browsing the atlas requires no model, GPU, API key, package installation, or build step.** The website displays an existing experiment; clicking a neuron does not launch new inference.

## Deploy to Vercel

1. Open [Vercel’s New Project page](https://vercel.com/new) and import **`benjaminbreen/TalkieAtlas`**.
2. Use the repository root as the **Root Directory**.
3. Use **Other** as the framework preset and **`public`** as the output directory.
4. Leave the build and install commands empty. There are no environment variables to configure.
5. Deploy.

[`vercel.json`](vercel.json) supplies those settings. Later commits to the connected production branch can trigger fresh deployments. See Vercel’s [build configuration documentation](https://vercel.com/docs/builds/configure-a-build) for the current interface.

## How the experiment works

The model is [Talkie-1930-13B-IT](https://huggingface.co/talkie-lm/talkie-1930-13b-it), running through an MLX harness on Apple Silicon, with 8-bit weights and BF16 computation. The weights were not trained or edited for this experiment.

For each sampled neuron, we add a signed version of its output direction to the residual stream. The direction includes Talkie’s learned MLP gain. Its magnitude is normalized to that layer’s median residual norm on the unsteered prompt, excluding the first token. The edit is applied at every prompt and generated position.

| Setting | Value |
|---|---|
| Prompt | `Who are you?` in Talkie’s native chat template |
| Sampling seed for neuron selection | `20261027` |
| Selection | 10 distinct random neurons in each layer, chosen before seeing replies |
| Decoding | Greedy, up to 160 tokens |
| Solo strengths | Start at 1.25×; retry at 1.0×, 0.75×, then 0.5× |
| Retry criterion | Luna coherence below 5/10 |
| Selection rule | Strongest qualifying reply; otherwise the final attempt |
| Stopping | Chat delimiter, token cap, or an exact repeated token block |
| Control | An unsteered reply in every generation batch |

GPT-6 Luna subagents classify each reply and assign a short name, description, tags, weirdness, and coherence. The reply judge receives the text and an ID, without explicit neuron, layer, strength, or control labels. The complete [judging rubric](research/JUDGE_RUBRIC.md) is included.

For the pair stage, eight highly ranked candidates were rerun in another batch layout. Only **two of eight** reproduced word for word, but a separate Luna comparison found that **all eight retained their specific self-described identity**. We use that identity-consistency criterion for the 28 pairs and record exact-text matches separately. You can inspect [all eight original/retest comparisons](research/identity_retest_tasks.json) and [Luna’s reasons](research/identity_retest_labels.json).

Each pair starts at its parents’ selected solo strengths. If the combined reply is incoherent, both strengths drop to 0.75×, then 0.5×. The viewer retains all attempts, including unsuccessful ones. [`public/manifest.json`](public/manifest.json) records the configuration and execution changes; [`research/validation.json`](research/validation.json) records the integrity checks.

## What should we make of this?

The experiment establishes that an intervention can change a short reply. It leaves larger questions open: whether the identity persists across different questions, whether a unit has that function during ordinary generation, and whether the model can sustain a historically convincing perspective.

A few practical limits matter:

- **One prompt.** “Who are you?” is particularly inviting for self-description.
- **Human identities are normal for Talkie.** Getting a human name is not, by itself, a discovery.
- **Strong pushes can disrupt generation.** Repetition and garbling remain visible in the data.
- **Automatic scores are fallible.** Coherence is not historical accuracy, logical validity, or proof of a stable persona. The triangle example makes this especially clear.
- **Batch layout can change wording.** This release records execution changes and distinguishes identity consistency from exact-text reproduction.
- **The Qwen comparison is an adapted replication.** This uses a different model, a small sample, Luna rather than Haiku, and a disclosed replacement rubric. The reference’s exact judging prompt and full three-layout retest protocol were not reproduced.

The fun outputs are leads for further work. They also offer a useful way to inspect the difference between a writing register, a lexical fixation, a self-description, and behavior that holds up under follow-up questions.

## Files and further experiments

```text
public/                 Deployable viewer and complete saved dataset
docs/images/            Screenshots of the working site
research/               Experiment source, execution snapshots, rubric, and checks
scripts/export_run.py   Re-export a compatible saved run into public/
vercel.json             Static hosting configuration
LICENSE                 MIT license
```

The viewer is self-contained. The [generation runner](research/neuron_site_sample.py) is included for inspection and adaptation, but requires the original MLX Talkie Harness interfaces, model weights, and active judge workers; that generation environment is not bundled here. See [research/README.md](research/README.md) before attempting a new sweep. Running the website does not require any of it.

## Credits and license

Created by **Benjamin Breen**, with Codex assistance and GPT-6 Luna judgments.

The method and interface are inspired by [Joshua Fonseca Rivera’s Qwen Neuron Persona Library](https://qwen-neurons-site.vercel.app/), which credits Sauers’ single-neuron steering experiments. Thanks to the [Talkie team](https://github.com/talkie-lm/talkie) for making a vintage language model available to experiment with.

This repository’s original code, documentation, screenshots, and included dataset are released under the [MIT license](LICENSE), to the extent any rights apply. You are welcome to reuse and adapt them with the license notice retained. Model weights are not included; Talkie’s model card lists its separate Apache 2.0 license. The license here does not relicense third-party models or reference projects.

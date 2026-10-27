# Experiment records

The deployable site is `../public/`. These files document how its saved replies
were generated and judged. They do not run during a Vercel deployment.

`neuron_site_sample.py` is the current experimental runner. `script_snapshot.py`
and the `script_resume*.py` files preserve the versions saved during execution;
their hashes and batch changes are recorded in `../public/manifest.json`.

## Generation requirements

The runner expects an existing MLX Talkie Harness checkout with:

- `harness.engine.Loaded` and `format_chat`, plus the native special tokens;
- `harness.steer.Capture` and `Steer` hooks;
- converted 8-bit Talkie-1930-13B-IT weights and its tokenizer;
- macOS/Apple Silicon GPU access and sufficient unified memory;
- judge workers that consume `judge_tasks/task-NNNNN.json` and atomically write
  matching arrays to `judge_labels/task-NNNNN.json`.

The original harness environment is not included in this viewer repository.
The runner should be placed under that checkout's `experiments/` directory so its
project-relative model and output paths resolve correctly. For example, **inside
a compatible, configured harness checkout**, the initial sweep command is:

```sh
python -m experiments.neuron_site_sample \
  --out runs/neuron-site-sample-20261027 \
  --units 400 --batch 32 --tokens 160 --pair-limit 8
```

Without active judge workers, generation will eventually wait for labels. The
JSON task format contains an ID and reply text. Use `JUDGE_RUBRIC.md` for the
seven-field reply judgments; the website's scores depend on that rubric and
the model doing the judging. There is no API key built into the runner.

## Identity retests

`identity_retest_tasks.json` contains the eight original/retest reply pairs.
`identity_retest_labels.json` contains Luna's separate identity-consistency
judgments. These are distinct from the reply-only category/coherence judgments.

The first pair screen used exact text matching and retained two candidates.
The expanded screen used identity consistency and retained eight. Both exact
and semantic reproduction counts are preserved in the website dataset.

## Data and checks

`../public/data.json` contains:

| Key | Contents |
|---|---|
| `manifest` | Sampling and generation configuration |
| `singles` | One selected reply per sampled neuron and sign |
| `pairs` | One selected reply per tested two-neuron combination |
| `controls` | Unsteered same-batch replies |
| `attempts` | All judged replies, including retries and retests |
| `retests` | Retest replies and reproduction counts |
| `identity_retests` | Separate identity-consistency judgments |
| `status` | Final run summary |

Rows include generated token IDs, reply text, applied edits, termination reason,
and automatic judgment. Pair rows link back to their parent solo IDs.

`validation.json` reports the signed-condition, layer-balance, ID, dose, and
selection checks. All 28 unordered combinations of the eight candidates were
also checked against the final pair list. These checks establish data integrity;
they do not validate the judge's interpretations.

To re-export a compatible completed run:

```sh
python3 scripts/export_run.py /path/to/saved/run
```

The exporter copies only the documented experiment records. It excludes model
weights, GPU queue state, restore logs, and machine-specific credentials.

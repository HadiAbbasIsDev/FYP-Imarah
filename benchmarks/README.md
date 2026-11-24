# Model experiments

`fixtures/` contains the small attributed image set. `results/` contains real saved experiment JSON files. Test-suite model responses are written to pytest temporary directories and do not appear here.

Start the app and run:

```bash
.venv/bin/python scripts/run_benchmark.py --repeats 2
```

Each run creates a new `bench-<id>.json`. It records the prompt, conditions, image hashes, exact output and runtime for each model/image/repetition. The app's Model lab reads these files directly.

See [method](../docs/evaluation/benchmark-method.md) for metric definitions and [findings](../docs/evaluation/model-findings.md) for interpretation. A smaller timing number does not imply better inspection quality.

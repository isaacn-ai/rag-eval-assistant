# Results & Evaluation Reports

This project writes evaluation outputs locally to support regression testing without committing generated artifacts.

## Where results live (local only)
When you run:

```powershell
python -m eval.run_eval --top_k 5 --out outputs\eval_run.json
```

A machine-readable report is written to:

- `outputs/eval_run.json`

The `outputs/` directory is ignored by git.

## Metrics (current)

### hit@k
Checks whether top-k retrieval contains at least one citation from `expected_citations`.

Purpose:
- Measures retrieval quality for known-answer questions.

### grounded@k
Checks whether at least one retrieved chunk contains all `required_terms` (case-insensitive).

Purpose:
- Simple, auditable “grounding” proxy.
- Intended as a baseline; later steps will use stronger faithfulness checks.

### correct_citations@k
Checks whether the answer payload includes at least one citation that matches `expected_citations`.

Purpose:
- Ensures the answer cites the correct evidence, not just any evidence.

## How to use this for regressions (manual baseline)
1. Run eval and generate `outputs/eval_run.json`.
2. Keep a copy locally if you want to compare runs over time, e.g.:
   - `outputs/eval_run_2026-01-15.json`
3. Compare summary metrics between runs.

A future step will add a small script to diff two result JSON files and highlight which examples changed.

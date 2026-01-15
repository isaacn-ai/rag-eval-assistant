# Portfolio Summary: RAG Eval Assistant (Audit-first)

## What I built
A minimal Retrieval-Augmented Generation (RAG) system designed around auditability and measurable reliability.

Pipeline:
1. Ingest: documents → chunks (`src.ingest`)
2. Index: embeddings + FAISS (`src.index`)
3. Retrieve: top-k evidence with explicit citations (`src.query`)
4. Answer: evidence-first baseline (quotes + citations, no LLM) (`src.answer`)
5. Evaluate: regression-friendly metrics + JSON reports (`eval.run_eval`)

## Why this matters
Models commoditize. Reliable systems and evaluation do not.

This repo emphasizes:
- Reproducibility (clear runbook, deterministic baseline)
- Audit trail (citations and quoted evidence)
- Measurement (eval metrics + regression diffs)
- Safe boundaries (generated artifacts and private data stay local)

## What is measurable today
Metrics computed by `eval.run_eval`:
- `hit@k`: retrieval includes expected citation
- `grounded@k`: retrieved text contains required terms (auditable proxy)
- `correct_citations@k`: answer includes at least one expected citation

A deliberate negative example demonstrates that the harness detects failure and reduces metrics.

## How to run (Windows)
PowerShell or cmd:

```powershell
python -m src.ingest
python -m src.index
python -m src.answer --question "What is this sample document about?" --top_k 5 --max_quotes 2
python -m eval.run_eval --top_k 5 --out outputs\eval_run.json
```

If using cmd or script activation is blocked:

```bat
.\.venv\Scripts\python.exe -m eval.run_eval --top_k 5 --out outputs\eval_run.json
```

## What stays private
- Real corpora and datasets
- Generated chunks, indexes, eval outputs
- `config.yaml` and secrets

## Next upgrades (planned)
- Stronger faithfulness checks beyond keyword proxies
- Prompt-injection / adversarial evaluation
- Optional LLM-backed answering behind a strict citation/refusal policy
- Better regression and failure analysis tooling

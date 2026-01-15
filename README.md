# RAG Eval Assistant (Audit-first)

This project builds a minimal, audit-first Retrieval-Augmented Generation (RAG) system and an evaluation harness. The focus is reliability: reproducible runs, measurable tests, and citation-backed evidence.

## What this is (today)
A working, reproducible pipeline that:
- Ingests local `.txt` documents into chunks (`data/processed/chunks.jsonl`)
- Builds a FAISS vector index (`data/index/faiss.index` + `data/index/meta.jsonl`)
- Retrieves top-k evidence chunks for a question with explicit citations
- Produces a citation-backed answer baseline (no LLM; evidence quotes + citations)
- Runs a measurable evaluation harness and writes a local JSON report (`outputs/eval_run.json`)

## Evaluation (current metrics)
The evaluation harness computes:
- `hit@k`: whether retrieved citations include `expected_citations`
- `grounded@k`: whether retrieved text contains all `required_terms`
- `correct_citations@k`: whether the answer payload includes at least one expected citation

These metrics are designed to be transparent and regression-friendly.

---

## Repository policy (commit vs local/private)

### Commit to GitHub
- Code under `src/` and `eval/`
- Docs under `docs/`
- `requirements.txt`
- `config.example.yaml`
- Tiny public sample corpus: `data/raw/sample_doc.txt`
- Tiny public eval set: `eval/eval_set.jsonl`

### Keep local/private (do NOT commit)
- Real/private corpora and datasets
- Generated chunks, indexes, logs, eval outputs
- Secrets (API keys/tokens) and local config `config.yaml`

---

## Quickstart (Windows PowerShell)

## One-command demo (Windows)
From the repo root in PowerShell:

```powershell
.\scripts\demo.ps1
```
If your system blocks running `.ps1` scripts (common on locked-down Windows setups), run the demo manually:

```powershell
python -m pip install -r requirements.txt
python -m src.ingest
python -m src.index
python -m src.query --question "What is this sample document about?" --top_k 5
python -m src.answer --question "What is this sample document about?" --top_k 5 --max_quotes 2
python -m eval.run_eval --top_k 5 --out outputs\eval_run.json
```

This runs ingest → index → query → answer → eval and writes a local report to `outputs\eval_run.json` (not committed).

### 1) Open PowerShell in the repo root
In File Explorer, open the repo folder (where you see `README.md`, `src`, `eval`), click the address bar, type `powershell`, press Enter.

### 2) (Recommended) Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies
```powershell
python -m pip install -r requirements.txt
```

### 4) Run the pipeline
```powershell
python -m src.ingest
python -m src.index
python -m src.query --question "What is this sample document about?" --top_k 5
python -m src.answer --question "What is this sample document about?" --top_k 5 --max_quotes 2
```

### 5) Run evaluation (writes a local JSON report)
```powershell
python -m eval.run_eval --top_k 5 --out outputs\eval_run.json
```

---

## Documentation
- Runbook: `docs/RUNBOOK.md`

## Status
Audit-first baseline is working end-to-end. Next upgrades will add grounded generation (LLM) while preserving citations, and stronger faithfulness checks beyond keyword heuristics.

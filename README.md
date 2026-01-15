# RAG Eval Assistant (Audit-first)

This project builds a minimal, audit-first Retrieval-Augmented Generation (RAG) system and (next) an evaluation harness. The focus is reliability: reproducible runs, measurable tests, and citation-backed evidence.

## What this is (today)
A working, reproducible pipeline that:
- Ingests local `.txt` documents into chunks (`data/processed/chunks.jsonl`)
- Builds a FAISS vector index (`data/index/faiss.index` + `data/index/meta.jsonl`)
- Retrieves top-k evidence chunks for a question with explicit citations (retrieval-only)

## What this will become (next)
- Citation-backed answering (RAG responses grounded in retrieved evidence)
- An evaluation harness with measurable retrieval metrics and regressions
- Failure analysis outputs (kept local/private by default)

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
python -m src.query --que

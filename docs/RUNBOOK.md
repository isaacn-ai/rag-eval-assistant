# Runbook (Work in progress)

## Goal
This project provides:
1) A minimal RAG pipeline (ingest → index → retrieve → answer with citations)
2) An evaluation harness to measure retrieval quality and faithfulness

This runbook is intentionally minimal and only documents what is reproducible.

---

## What belongs in GitHub vs what stays local

### Commit to GitHub (reproducible artifacts only)
- Code under `src/` and `eval/`
- Documentation under `docs/`
- `requirements.txt`
- `config.example.yaml`
- A tiny public sample corpus (e.g., `data/raw/sample_doc.txt`)
- A tiny public eval set (e.g., `eval/eval_set.jsonl`)

### Keep local/private (do NOT commit)
- Real/private documents and datasets
- Generated chunks and processed data
- Vector indexes and embedding artifacts
- Logs, evaluation outputs, result summaries
- Secrets (API keys, tokens), and local config (`config.yaml`)

---

## Prerequisites (local setup)
- Windows 10/11
- Python 3.10+ installed
- PowerShell

---

## Local environment setup (Windows)

### 1) Open PowerShell in the repo root folder
In File Explorer, open the repo folder (where you see `README.md`, `src`, `eval`), then click the address bar, type `powershell`, and press Enter.

### 2) (Recommended) Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

3) Install dependencies
python -m pip install -r requirements.txt

Pipeline (reproducible demo)
A) Ingest (raw documents → chunks)
python -m src.ingest


Expected output file:

data/processed/chunks.jsonl

B) Index (chunks → embeddings + FAISS index)
python -m src.index


Expected output files:

data/index/faiss.index

data/index/meta.jsonl

C) Query (retrieval-only with citations)
python -m src.query --question "What is this sample document about?" --top_k 5


Expected behavior:

Prints the question

Prints top-k evidence chunks with a citation like sample_doc.txt#sample_doc_0

Evaluation (current)

This currently prints the eval examples (scoring not implemented yet):

python -m eval.run_eval

Config notes

config.example.yaml is committed as a reference.

config.yaml is local/private and should not be committed.

Scripts auto-load config.yaml if it exists; otherwise they use config.example.yaml.

To use an explicit config file path:

python -m src.ingest --config config.example.yaml
python -m src.index --config config.example.yaml
python -m src.query --config config.example.yaml --question "..." --top_k 5

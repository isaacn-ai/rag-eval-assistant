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

1) Open PowerShell in the repo root folder.

2) Create and activate a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Demo script: end-to-end audit-first RAG baseline (Windows PowerShell)
# Run from repo root:  .\scripts\demo.ps1

$ErrorActionPreference = "Stop"

Write-Host "== Install dependencies =="
python -m pip install -r requirements.txt

Write-Host "== Ingest =="
python -m src.ingest

Write-Host "== Index =="
python -m src.index

Write-Host "== Query (retrieval-only) =="
python -m src.query --question "What is this sample document about?" --top_k 5

Write-Host "== Answer (citation-backed baseline) =="
python -m src.answer --question "What is this sample document about?" --top_k 5 --max_quotes 2

Write-Host "== Eval (writes local JSON report) =="
python -m eval.run_eval --top_k 5 --out outputs\eval_run.json

Write-Host "== Done. Local report: outputs\eval_run.json =="

# Architecture (Audit-first RAG)

## Data flow (current baseline)

Raw documents (committed sample only)
- `data/raw/sample_doc.txt` (public demo)
- Real/private corpora stay local and are not committed

↓ ingestion (chunking)

Chunked dataset (local, generated)
- `data/processed/chunks.jsonl`
- Each row includes:
  - `source_file`
  - `chunk_id`
  - `text`

↓ indexing (embeddings + vector index)

Vector index artifacts (local, generated)
- `data/index/faiss.index`
- `data/index/meta.jsonl` (same rows as chunks; used for citations)

↓ retrieval (audit trail)

`src.query`
- Input: question
- Output: top-k evidence chunks with explicit citations:
  - `source_file#chunk_id`

↓ answering (audit-first baseline)

`src.answer`
- Input: question
- Output: evidence-first response:
  - citations (with scores)
  - quoted evidence text
- Note: current baseline does not use an LLM; it prioritizes auditability.

↓ evaluation (measurable reliability)

`eval.run_eval`
- Reads: `eval/eval_set.jsonl`
- Computes:
  - `hit@k`: retrieved contains `expected_citations`
  - `grounded@k`: retrieved text contains all `required_terms`
  - `correct_citations@k`: answer includes at least one expected citation
- Writes local report:
  - `outputs/eval_run.json` (ignored by git)

---

## Reproducibility & configuration

- `config.example.yaml` is committed.
- `config.yaml` is local/private and ignored.
- Scripts auto-load `config.yaml` if present; otherwise use `config.example.yaml`.

---

## Commit vs local/private boundary (enforced by .gitignore)

Committed:
- Source code (`src/`, `eval/`)
- Docs (`docs/`)
- `requirements.txt`, `config.example.yaml`
- Public demo inputs: `data/raw/sample_doc.txt`, `eval/eval_set.jsonl`

Local/private (not committed):
- `config.yaml` (secrets/local settings)
- `data/processed/` (generated chunks)
- `data/index/` (generated indexes)
- `outputs/` (eval reports, logs, analyses)
- Real/private corpora and datasets

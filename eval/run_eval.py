import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import get_repo_root, load_config


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_meta(meta_path: Path) -> List[Dict[str, Any]]:
    rows = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def search(
    model: SentenceTransformer,
    index: faiss.Index,
    meta: List[Dict[str, Any]],
    question: str,
    top_k: int,
) -> List[Tuple[int, float, str]]:
    q_emb = model.encode([question], normalize_embeddings=True)
    q_emb = np.asarray(q_emb, dtype=np.float32)

    scores, ids = index.search(q_emb, top_k)
    results = []
    for r in range(top_k):
        idx = int(ids[0][r])
        score = float(scores[0][r])
        if idx < 0 or idx >= len(meta):
            continue
        row = meta[idx]
        citation = f"{row.get('source_file', 'unknown')}#{row.get('chunk_id', f'row_{idx}')}"
        results.append((idx, score, citation))
    return results


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Evaluation harness (retrieval hit@k).")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML (optional).")
    parser.add_argument("--top_k", type=int, default=5, help="k for hit@k.")
    parser.add_argument("--out", type=str, default=None, help="Optional path to write JSON results (local).")
    args = parser.parse_args()

    cfg = load_config(args.config)
    repo_root = get_repo_root()

    retrieval_cfg = cfg.get("retrieval", {})
    model_name = retrieval_cfg.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")

    eval_path = repo_root / "eval" / "eval_set.jsonl"
    index_path = repo_root / "data" / "index" / "faiss.index"
    meta_path = repo_root / "data" / "index" / "meta.jsonl"

    if not eval_path.exists():
        print(f"Missing eval set: {eval_path}")
        return

    if not index_path.exists() or not meta_path.exists():
        print("Missing index artifacts. Run:")
        print("  python -m src.ingest")
        print("  python -m src.index")
        return

    eval_rows = load_jsonl(eval_path)
    meta = load_meta(meta_path)
    index = faiss.read_index(str(index_path))
    model = SentenceTransformer(model_name)

    total = 0
    hits = 0
    missing_expectations = 0

    per_example: List[Dict[str, Any]] = []

    print(f"Config: {args.config or '(auto)'}")
    print(f"Embedding model: {model_name}")
    print(f"Eval set: {eval_path}")
    print(f"top_k: {args.top_k}")
    print("-" * 72)

    for ex in eval_rows:
        ex_id = ex.get("id", "")
        q = ex.get("question", "").strip()
        expected = ex.get("expected_citations", [])

        if not q:
            continue

        total += 1

        if not expected:
            missing_expectations += 1
            print(f"[SKIP] Missing expected_citations for question: {q}")
            per_example.append(
                {
                    "id": ex_id,
                    "question": q,
                    "status": "SKIP",
                    "expected_citations": expected,
                    "retrieved_citations": [],
                }
            )
            continue

        results = search(model, index, meta, q, args.top_k)
        retrieved_citations = [c for _, _, c in results]

        hit = any(e in retrieved_citations for e in expected)
        hits += 1 if hit else 0

        status = "HIT" if hit else "MISS"
        print(f"[{status}] Q: {q}")
        print(f"       expected: {expected}")
        print(f"       retrieved: {retrieved_citations[: min(len(retrieved_citations), 5)]}")

        per_example.append(
            {
                "id": ex_id,
                "question": q,
                "status": status,
                "expected_citations": expected,
                "retrieved_citations": retrieved_citations,
            }
        )

    scored_total = total - missing_expectations
    hit_rate = (hits / scored_total) if scored_total > 0 else 0.0

    summary = {
        "top_k": args.top_k,
        "hit_at_k": hit_rate,
        "hits": hits,
        "scored_total": scored_total,
        "total": total,
        "skipped_missing_expected": missing_expectations,
        "embedding_model": model_name,
        "eval_set_path": str(eval_path),
    }

    print("-" * 72)
    print(f"Examples total: {total}")
    print(f"Examples scored: {scored_total}")
    print(f"Examples skipped (missing expected_citations): {missing_expectations}")
    print(f"hit@{args.top_k}: {hit_rate:.3f} ({hits}/{scored_total})")

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = repo_root / out_path
        payload = {"summary": summary, "examples": per_example}
        write_json(out_path, payload)
        print(f"Wrote JSON results to: {out_path}")


if __name__ == "__main__":
    main()

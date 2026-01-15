import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

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


def contains_all_terms(text: str, terms: List[str]) -> bool:
    t = " ".join(text.split()).lower()
    return all(term.lower() in t for term in terms)


def search(
    model: SentenceTransformer,
    index: faiss.Index,
    meta: List[Dict[str, Any]],
    question: str,
    top_k: int,
) -> List[Tuple[int, float, str, str]]:
    """
    Returns: (row_index, score, citation, text)
    """
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
        text = row.get("text", "")
        results.append((idx, score, citation, text))
    return results


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Evaluation harness (retrieval hit@k + grounded@k).")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML (optional).")
    parser.add_argument("--top_k", type=int, default=5, help="k for hit@k and grounded@k.")
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

    # hit@k counters
    hits = 0
    missing_expected = 0

    # grounded@k counters
    grounded_hits = 0
    missing_required_terms = 0

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
        required_terms = ex.get("required_terms", [])

        if not q:
            continue

        total += 1
        results = search(model, index, meta, q, args.top_k)
        retrieved_citations = [c for _, _, c, _ in results]
        retrieved_texts = [t for _, _, _, t in results]

        # hit@k
        if not expected:
            missing_expected += 1
            hit_status = "SKIP"
            hit = None
        else:
            hit = any(e in retrieved_citations for e in expected)
            hits += 1 if hit else 0
            hit_status = "HIT" if hit else "MISS"

        # grounded@k
        if not required_terms:
            missing_required_terms += 1
            grounded_status = "SKIP"
            grounded = None
        else:
            grounded = any(contains_all_terms(t, required_terms) for t in retrieved_texts)
            grounded_hits += 1 if grounded else 0
            grounded_status = "GROUNDED" if grounded else "UNGROUNDED"

        print(f"[{hit_status} | {grounded_status}] Q: {q}")
        if expected:
            print(f"  expected_citations: {expected}")
        if required_terms:
            print(f"  required_terms: {required_terms}")
        print(f"  retrieved_citations: {retrieved_citations[: min(len(retrieved_citations), 5)]}")

        per_example.append(
            {
                "id": ex_id,
                "question": q,
                "expected_citations": expected,
                "required_terms": required_terms,
                "retrieved_citations": retrieved_citations,
                "hit_at_k": hit,
                "grounded_at_k": grounded,
            }
        )

    hit_scored_total = total - missing_expected
    grounded_scored_total = total - missing_required_terms

    hit_rate = (hits / hit_scored_total) if hit_scored_total > 0 else 0.0
    grounded_rate = (grounded_hits / grounded_scored_total) if grounded_scored_total > 0 else 0.0

    print("-" * 72)
    print(f"Examples total: {total}")
    print(f"hit@{args.top_k}: {hit_rate:.3f} ({hits}/{hit_scored_total})  [skipped_missing_expected={missing_expected}]")
    print(
        f"grounded@{args.top_k}: {grounded_rate:.3f} ({grounded_hits}/{grounded_scored_total})  "
        f"[skipped_missing_required_terms={missing_required_terms}]"
    )

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = repo_root / out_path

        payload = {
            "summary": {
                "top_k": args.top_k,
                "embedding_model": model_name,
                "eval_set_path": str(eval_path),
                "total": total,
                "hit_at_k": {"value": hit_rate, "hits": hits, "scored_total": hit_scored_total, "skipped": missing_expected},
                "grounded_at_k": {
                    "value": grounded_rate,
                    "hits": grounded_hits,
                    "scored_total": grounded_scored_total,
                    "skipped": missing_required_terms,
                },
            },
            "examples": per_example,
        }
        write_json(out_path, payload)
        print(f"Wrote JSON results to: {out_path}")


if __name__ == "__main__":
    main()

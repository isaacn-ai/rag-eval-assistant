import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import get_repo_root, load_config


def load_meta(meta_path: Path) -> List[Dict[str, Any]]:
    rows = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def normalize_ws(text: str) -> str:
    return " ".join(text.split())


def format_quote(text: str, max_chars: int = 320) -> str:
    t = normalize_ws(text)
    if len(t) <= max_chars:
        return t
    return t[: max_chars - 3] + "..."


def search(
    model: SentenceTransformer,
    index: faiss.Index,
    meta: List[Dict[str, Any]],
    question: str,
    top_k: int,
) -> List[Tuple[float, Dict[str, Any]]]:
    q_emb = model.encode([question], normalize_embeddings=True)
    q_emb = np.asarray(q_emb, dtype=np.float32)

    scores, ids = index.search(q_emb, top_k)
    results: List[Tuple[float, Dict[str, Any]]] = []

    for r in range(top_k):
        idx = int(ids[0][r])
        score = float(scores[0][r])
        if idx < 0 or idx >= len(meta):
            continue
        results.append((score, meta[idx]))

    return results


def build_answer(question: str, retrieved: List[Tuple[float, Dict[str, Any]]], max_quotes: int) -> Dict[str, Any]:
    """
    Audit-first baseline:
    - No generation beyond selecting and quoting evidence.
    - Answer is a short evidence summary + quotes.
    """
    citations = []
    quotes = []

    for score, row in retrieved[:max_quotes]:
        source_file = row.get("source_file", "unknown")
        chunk_id = row.get("chunk_id", "unknown")
        citation = f"{source_file}#{chunk_id}"
        text = row.get("text", "")

        citations.append({"citation": citation, "score": score})
        quotes.append({"citation": citation, "quote": format_quote(text)})

    answer_text = (
        "Evidence-first response (baseline):\n"
        "The passages below are the highest-scoring retrieved chunks. "
        "A later step will add a grounded generated answer, but this baseline is fully auditable."
    )

    return {
        "question": question,
        "answer": answer_text,
        "citations": citations,
        "quotes": quotes,
    }


def main():
    parser = argparse.ArgumentParser(description="Citation-backed answering (audit-first baseline, no LLM).")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML (optional).")
    parser.add_argument("--question", type=str, required=True, help="Question to answer.")
    parser.add_argument("--top_k", type=int, default=5, help="Chunks to retrieve.")
    parser.add_argument("--max_quotes", type=int, default=2, help="How many evidence quotes to include.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    args = parser.parse_args()

    cfg = load_config(args.config)
    repo_root = get_repo_root()

    retrieval_cfg = cfg.get("retrieval", {})
    model_name = retrieval_cfg.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")

    index_path = repo_root / "data" / "index" / "faiss.index"
    meta_path = repo_root / "data" / "index" / "meta.jsonl"

    if not index_path.exists() or not meta_path.exists():
        print("Missing index artifacts. Run:")
        print("  python -m src.ingest")
        print("  python -m src.index")
        return

    meta = load_meta(meta_path)
    index = faiss.read_index(str(index_path))
    model = SentenceTransformer(model_name)

    retrieved = search(model, index, meta, args.question, args.top_k)
    payload = build_answer(args.question, retrieved, max_quotes=args.max_quotes)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"QUESTION: {payload['question']}")
    print()
    print(payload["answer"])
    print()
    print("CITATIONS")
    for c in payload["citations"]:
        print(f"- {c['citation']} (score={c['score']:.4f})")
    print()
    print("EVIDENCE QUOTES")
    for q in payload["quotes"]:
        print(f"- {q['citation']}: {q['quote']}")


if __name__ == "__main__":
    main()

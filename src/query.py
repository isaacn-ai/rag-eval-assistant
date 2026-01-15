import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

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


def format_snippet(text: str, max_chars: int = 240) -> str:
    t = " ".join(text.split())
    if len(t) <= max_chars:
        return t
    return t[: max_chars - 3] + "..."


def search(
    model: SentenceTransformer,
    index: faiss.Index,
    meta: List[Dict[str, Any]],
    question: str,
    top_k: int,
) -> List[Tuple[int, float, Dict[str, Any]]]:
    q_emb = model.encode([question], normalize_embeddings=True)
    q_emb = np.asarray(q_emb, dtype=np.float32)

    scores, ids = index.search(q_emb, top_k)  # (1, k)
    results = []

    for rank in range(top_k):
        idx = int(ids[0][rank])
        score = float(scores[0][rank])
        if idx < 0 or idx >= len(meta):
            continue
        results.append((idx, score, meta[idx]))

    return results


def main():
    parser = argparse.ArgumentParser(description="Query the FAISS index and print top-k cited chunks.")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML (optional).")
    parser.add_argument("--question", type=str, required=True, help="User question to retrieve for.")
    parser.add_argument("--top_k", type=int, default=5, help="Number of chunks to retrieve.")
    args = parser.parse_args()

    cfg = load_config(args.config)
    repo_root = get_repo_root()

    retrieval_cfg = cfg.get("retrieval", {})
    model_name = retrieval_cfg.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")

    index_path = repo_root / "data" / "index" / "faiss.index"
    meta_path = repo_root / "data" / "index" / "meta.jsonl"

    if not index_path.exists() or not meta_path.exists():
        print("Missing index artifacts.")
        print(f"- {index_path}")
        print(f"- {meta_path}")
        print("Run in order:")
        print("  python src/ingest.py")
        print("  python src/index.py")
        return

    print(f"Config: {args.config or '(auto)'}")
    print(f"Embedding model: {model_name}")
    print(f"Index: {index_path}")
    print(f"Meta:  {meta_path}")
    print()

    meta = load_meta(meta_path)
    index = faiss.read_index(str(index_path))
    model = SentenceTransformer(model_name)

    results = search(model, index, meta, args.question, args.top_k)

    print("QUESTION")
    print(args.question)
    print()
    print(f"TOP {len(results)} EVIDENCE CHUNKS (with citations)")
    print("-" * 72)

    for rank, (idx, score, row) in enumerate(results, start=1):
        source_file = row.get("source_file", "unknown")
        chunk_id = row.get("chunk_id", f"row_{idx}")
        text = row.get("text", "")

        print(f"[{rank}] score={score:.4f}  citation: {source_file}#{chunk_id}")
        print(f"     snippet: {format_snippet(text)}")
        print()

    print("Note: This step is retrieval-only. Next step will add citation-backed answering and evaluation.")


if __name__ == "__main__":
    main()

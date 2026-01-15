import argparse
import json
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from src.config import get_repo_root, load_config


def load_chunks(path: Path):
    chunks = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Build a FAISS index from chunked JSONL.")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML (optional).")
    args = parser.parse_args()

    cfg = load_config(args.config)
    repo_root = get_repo_root()

    retrieval_cfg = cfg.get("retrieval", {})
    model_name = retrieval_cfg.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")

    chunks_path = repo_root / "data" / "processed" / "chunks.jsonl"
    out_dir = repo_root / "data" / "index"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not chunks_path.exists():
        print(f"Missing chunks file: {chunks_path}")
        print("Run: python src/ingest.py")
        return

    chunks = load_chunks(chunks_path)
    texts = [c["text"] for c in chunks]

    print(f"Loaded {len(texts)} chunks.")
    print(f"Embedding model: {model_name}")

    model = SentenceTransformer(model_name)
    emb = model.encode(texts, normalize_embeddings=True)
    emb = np.asarray(emb, dtype=np.float32)

    d = emb.shape[1]
    index = faiss.IndexFlatIP(d)  # cosine similarity via normalized vectors
    index.add(emb)

    faiss_path = out_dir / "faiss.index"
    faiss.write_index(index, str(faiss_path))

    meta_path = out_dir / "meta.jsonl"
    with meta_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print("Index build complete.")
    print(f"Config:   {args.config or '(auto)'}")
    print(f"Chunks:   {chunks_path}")
    print(f"Index:    {faiss_path}")
    print(f"Metadata: {meta_path}")


if __name__ == "__main__":
    main()

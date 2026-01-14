import json
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


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
    repo_root = Path(__file__).resolve().parents[1]
    chunks_path = repo_root / "data" / "processed" / "chunks.jsonl"
    out_dir = repo_root / "data" / "index"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not chunks_path.exists():
        print(f"Missing chunks file: {chunks_path}")
        print("Run: python src/ingest.py")
        return

    chunks = load_chunks(chunks_path)
    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]

    print(f"Loaded {len(texts)} chunks.")

    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    emb = model.encode(texts, normalize_embeddings=True)
    emb = np.asarray(emb, dtype=np.float32)

    d = emb.shape[1]
    index = faiss.IndexFlatIP(d)  # cosine similarity via normalized vectors
    index.add(emb)

    faiss_path = out_dir / "faiss.index"
    meta_path = out_dir / "meta.jsonl"

    faiss.write_index(index, str(faiss_path))

    with meta_path.open("w", encoding="utf-8") as f:
        for chunk_id, rec in zip(ids, chunks):
            f.write(json.dumps({"chunk_id": chunk_id, "source_file": rec["source_file"]}, ensure_ascii=False) + "\n")

    print("Index build complete.")
    print(f"Model:  {model_name}")
    print(f"Index:  {faiss_path}")
    print(f"Meta:   {meta_path}")
    print(f"Vectors:{index.ntotal}  Dim:{d}")


if __name__ == "__main__":
    main()

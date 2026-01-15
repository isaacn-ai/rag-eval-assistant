import argparse
import json
from pathlib import Path
from typing import List, Dict

from src.config import get_repo_root, load_config


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> List[str]:
    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0
    step = max(1, chunk_size - chunk_overlap)

    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        chunks.append(chunk)
        start += step

    return chunks


def ingest_raw_texts(raw_dir: Path, out_path: Path, chunk_size: int, chunk_overlap: int) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    total_chunks = 0
    with out_path.open("w", encoding="utf-8") as out_f:
        for txt_path in sorted(raw_dir.glob("*.txt")):
            text = txt_path.read_text(encoding="utf-8", errors="ignore")
            pieces = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

            for i, piece in enumerate(pieces):
                record: Dict = {
                    "source_file": txt_path.name,
                    "chunk_id": f"{txt_path.stem}_{i}",
                    "text": piece,
                }
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_chunks += 1

    return total_chunks


def main():
    parser = argparse.ArgumentParser(description="Ingest raw text files into chunked JSONL.")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML (optional).")
    args = parser.parse_args()

    cfg = load_config(args.config)
    repo_root = get_repo_root()

    retrieval_cfg = cfg.get("retrieval", {})
    chunk_size = int(retrieval_cfg.get("chunk_size", 800))
    chunk_overlap = int(retrieval_cfg.get("chunk_overlap", 120))

    raw_dir = repo_root / "data" / "raw"
    out_path = repo_root / "data" / "processed" / "chunks.jsonl"

    if not raw_dir.exists():
        print(f"Raw directory not found: {raw_dir}")
        print("Create it and add at least one .txt file.")
        return

    total = ingest_raw_texts(raw_dir, out_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print("Ingestion complete.")
    print(f"Config:  {args.config or '(auto)'}")
    print(f"Raw dir: {raw_dir}")
    print(f"Output:  {out_path}")
    print(f"Chunks:  {total}")
    print(f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")


if __name__ == "__main__":
    main()

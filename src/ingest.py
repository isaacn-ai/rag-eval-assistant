import json
from pathlib import Path
from typing import List, Dict


def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> List[str]:
    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0
    step = max(1, chunk_size - chunk_overlap)

    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start += step

    return chunks


def ingest_raw_texts(raw_dir: Path, out_path: Path, chunk_size: int = 800, chunk_overlap: int = 120) -> int:
    raw_files = sorted(raw_dir.glob("*.txt"))
    out_path.parent.mkdir(parents=True, exist_ok=True)

    chunk_id = 0
    total_chunks = 0

    with out_path.open("w", encoding="utf-8") as f_out:
        for fp in raw_files:
            text = fp.read_text(encoding="utf-8", errors="ignore")
            chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

            for i, ch in enumerate(chunks):
                record: Dict[str, str] = {
                    "chunk_id": f"c{chunk_id}",
                    "source_file": fp.name,
                    "chunk_index": str(i),
                    "text": ch,
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                chunk_id += 1
                total_chunks += 1

    return total_chunks


def main():
    repo_root = Path(__file__).resolve().parents[1]
    raw_dir = repo_root / "data" / "raw"
    out_path = repo_root / "data" / "processed" / "chunks.jsonl"

    if not raw_dir.exists():
        print(f"Raw directory not found: {raw_dir}")
        print("Create it and add at least one .txt file.")
        return

    total = ingest_raw_texts(raw_dir, out_path)
    print("Ingestion complete.")
    print(f"Raw dir: {raw_dir}")
    print(f"Output:  {out_path}")
    print(f"Chunks:  {total}")


if __name__ == "__main__":
    main()

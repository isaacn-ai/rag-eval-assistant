import json
from pathlib import Path


def load_jsonl(path: Path):
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def main():
    eval_path = Path(__file__).parent / "eval_set.jsonl"
    items = load_jsonl(eval_path)

    print("RAG Eval Assistant - Eval Set Loader")
    print(f"Loaded {len(items)} eval items from: {eval_path}")
    print("-" * 60)

    for item in items:
        qid = item.get("id", "")
        question = item.get("question", "")
        expected = item.get("expected", "")
        print(f"[{qid}] {question}")
        print(f"Expected: {expected}")
        print("-" * 60)


if __name__ == "__main__":
    main()

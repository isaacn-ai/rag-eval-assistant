import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pct(x: float) -> str:
    return f"{x:.3f}"


def index_by_id(examples: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out = {}
    for ex in examples:
        ex_id = ex.get("id", "")
        if ex_id:
            out[ex_id] = ex
    return out


def summarize(summary: Dict[str, Any]) -> Dict[str, float]:
    hit = summary.get("hit_at_k", {}).get("value", 0.0)
    grounded = summary.get("grounded_at_k", {}).get("value", 0.0)
    correct = summary.get("correct_citations_at_k", {}).get("value", 0.0)
    return {"hit": float(hit), "grounded": float(grounded), "correct_citations": float(correct)}


def main():
    parser = argparse.ArgumentParser(description="Diff two eval_run.json reports (regressions).")
    parser.add_argument("--before", type=str, required=True, help="Path to older eval_run.json")
    parser.add_argument("--after", type=str, required=True, help="Path to newer eval_run.json")
    args = parser.parse_args()

    before_path = Path(args.before).expanduser().resolve()
    after_path = Path(args.after).expanduser().resolve()

    before = load_json(before_path)
    after = load_json(after_path)

    bsum = summarize(before.get("summary", {}))
    asum = summarize(after.get("summary", {}))

    print("EVAL SUMMARY DIFF")
    print(f"before: {before_path}")
    print(f"after : {after_path}")
    print("-" * 72)
    print(f"hit@k             {pct(bsum['hit'])}  ->  {pct(asum['hit'])}   (delta={pct(asum['hit'] - bsum['hit'])})")
    print(f"grounded@k        {pct(bsum['grounded'])}  ->  {pct(asum['grounded'])}   (delta={pct(asum['grounded'] - bsum['grounded'])})")
    print(f"correct_citations {pct(bsum['correct_citations'])}  ->  {pct(asum['correct_citations'])}   (delta={pct(asum['correct_citations'] - bsum['correct_citations'])})")
    print("-" * 72)

    b_examples = index_by_id(before.get("examples", []))
    a_examples = index_by_id(after.get("examples", []))

    all_ids = sorted(set(b_examples.keys()) | set(a_examples.keys()))
    changes: List[Tuple[str, str]] = []

    def status_str(ex: Dict[str, Any]) -> str:
        h = ex.get("hit_at_k", None)
        g = ex.get("grounded_at_k", None)
        c = ex.get("correct_citations_at_k", None)
        return f"hit={h} grounded={g} correct_citations={c}"

    for ex_id in all_ids:
        b = b_examples.get(ex_id)
        a = a_examples.get(ex_id)
        if b is None:
            changes.append((ex_id, "ADDED"))
            continue
        if a is None:
            changes.append((ex_id, "REMOVED"))
            continue

        if status_str(b) != status_str(a):
            changes.append((ex_id, "CHANGED"))

    if not changes:
        print("No per-example status changes detected.")
        return

    print("PER-EXAMPLE CHANGES")
    for ex_id, kind in changes:
        print("-" * 72)
        print(f"{kind}: {ex_id}")
        b = b_examples.get(ex_id)
        a = a_examples.get(ex_id)

        if kind == "ADDED":
            print(f"question: {a.get('question')}")
            print(f"after : {status_str(a)}")
            continue
        if kind == "REMOVED":
            print(f"question: {b.get('question')}")
            print(f"before: {status_str(b)}")
            continue

        # CHANGED
        print(f"question: {a.get('question')}")
        print(f"before: {status_str(b)}")
        print(f"after : {status_str(a)}")

        # Helpful context
        print(f"expected_citations: {a.get('expected_citations')}")
        print(f"retrieved_citations(before): {b.get('retrieved_citations')}")
        print(f"retrieved_citations(after) : {a.get('retrieved_citations')}")
        print(f"answer_citations(before)   : {b.get('answer_citations')}")
        print(f"answer_citations(after)    : {a.get('answer_citations')}")

    print("-" * 72)
    print(f"Total changes: {len(changes)}")


if __name__ == "__main__":
    main()

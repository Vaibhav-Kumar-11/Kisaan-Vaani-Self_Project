"""Measures real intent-routing accuracy against a hand-labeled test set.

This is deliberately separate from tests/ — it makes real Groq API calls
(costs a small amount of quota and takes a minute or so) and measures
*quality*, not correctness-of-code. The regular pytest suite mocks the
LLM entirely so it stays fast and free to run; this script is the one
place that actually asks "does the model classify real, messy farmer
questions correctly," which is what the numbers on the resume/README
are based on.

The 42 questions here were generated from 4 different angles (plain,
Hinglish/colloquial, deliberately ambiguous, and multi-entity/compound)
specifically so this isn't just testing the easy cases. Two of the
"ambiguous" questions from the original generation had labels that didn't
match this system's actual category definitions (see intent.py's own
price/weather/scheme/advisory descriptions) and were corrected by hand
before running this — noted here rather than silently fixed, since that's
exactly the kind of judgment call that should be visible, not hidden.

Run: python eval/run_intent_eval.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.intent import extract_intent

DATASET_PATH = Path(__file__).parent / "intent_eval_set.json"


def main():
    cases = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    correct = 0
    per_category = defaultdict(lambda: {"correct": 0, "total": 0})
    misses = []

    for i, case in enumerate(cases, 1):
        question = case["text"]
        expected = case["expected_question_type"]

        intent = extract_intent(question)
        actual = intent.get("question_type")

        per_category[expected]["total"] += 1
        is_correct = actual == expected
        if is_correct:
            correct += 1
            per_category[expected]["correct"] += 1
        else:
            misses.append({"question": question, "expected": expected, "actual": actual})

        print(f"[{i:2}/{len(cases)}] {'OK  ' if is_correct else 'MISS'} "
              f"expected={expected:<9} actual={actual!s:<9} {question[:60]}")

    accuracy = correct / len(cases) * 100

    print("\n" + "=" * 70)
    print(f"Overall intent-routing accuracy: {correct}/{len(cases)} ({accuracy:.1f}%)")
    print("=" * 70)
    for category, stats in per_category.items():
        cat_acc = stats["correct"] / stats["total"] * 100
        print(f"  {category:<10} {stats['correct']}/{stats['total']} ({cat_acc:.1f}%)")

    if misses:
        print("\nMissed cases:")
        for m in misses:
            print(f"  expected={m['expected']:<9} actual={m['actual']!s:<9} {m['question']}")

    return accuracy


if __name__ == "__main__":
    main()

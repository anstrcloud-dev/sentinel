"""Evaluation harness for SENTINEL.

Runs every labeled test case through the real classifier and router, then
reports two objective metrics:

  1. Classification accuracy — did it get incident_type right?
  2. Routing accuracy       — did the right specialist(s) get triggered?

Only the parts with objective ground truth are evaluated. Specialist unit
recommendations are intentionally NOT scored — there is no single correct
dispatch, so an automated metric there would be misleading.

Run:  python eval/run_eval.py
"""

import sys
from pathlib import Path

# Allow importing from src/ when run as a script.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.classifier import _classify_with
from src.config import FAST_MODEL
from src.graph import route_by_type
from eval.test_cases import TEST_CASES


def evaluate():
    total = len(TEST_CASES)
    correct_class = 0
    correct_route = 0
    failures = []

    print(f"Running evaluation on {total} labeled cases...\n")

    for i, case in enumerate(TEST_CASES, 1):
        # Classify (fast model only — we're measuring the base classifier).
        data = _classify_with(FAST_MODEL, case["text"])
        predicted_type = data["incident_type"]

        # Routing is deterministic, so we can check it directly from the type.
        predicted_routes = set(route_by_type({"incident_type": predicted_type}))

        type_ok = predicted_type == case["expected_type"]
        route_ok = predicted_routes == case["expected_routes"]

        if type_ok:
            correct_class += 1
        if route_ok:
            correct_route += 1

        # Record misses for the failure report — the interesting part.
        if not type_ok or not route_ok:
            failures.append({
                "text": case["text"],
                "expected_type": case["expected_type"],
                "predicted_type": predicted_type,
                "expected_routes": case["expected_routes"],
                "predicted_routes": predicted_routes,
            })

        mark = "✅" if type_ok else "❌"
        print(f"  {mark} [{i:2}] {predicted_type:8} (expected {case['expected_type']:8}) — {case['text'][:45]}")

    # ── Summary ──
    print("\n" + "=" * 55)
    print("RESULTS")
    print("=" * 55)
    print(f"  Classification accuracy: {correct_class}/{total} = {correct_class/total:.1%}")
    print(f"  Routing accuracy:        {correct_route}/{total} = {correct_route/total:.1%}")

    if failures:
        print(f"\n  {len(failures)} failure(s) — worth inspecting:")
        for f in failures:
            print(f"    • '{f['text'][:50]}'")
            print(f"        expected {f['expected_type']} {f['expected_routes']}, "
                  f"got {f['predicted_type']} {f['predicted_routes']}")
    else:
        print("\n  No failures. (On a small set this can mean the set is too easy —")
        print("   add harder cases to keep the eval honest.)")


if __name__ == "__main__":
    evaluate()

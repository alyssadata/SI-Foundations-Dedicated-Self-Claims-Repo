#!/usr/bin/env python3
"""Post-result diagnostic for RUN-001 C2 errors.

This script is descriptive only. It does not modify the frozen manifest,
raw evaluator outputs, scores.json, thresholds, exclusions, or classification.
It reads existing RUN-001 artifacts and writes a separate diagnostic artifact.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("tests/run001/artifacts")
OUT = ROOT / "c2-error-analysis.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def truth_for_terminal(pair: int, terminal: str) -> tuple[int, str, str]:
    gt = read_json(ROOT / f"pair-{pair:02d}" / "hidden-ground-truth.json")["ground_truth"]
    for branch, info in gt.items():
        if info["terminal_label"] == terminal:
            return int(info["path_number"]), branch, info["track"]
    raise KeyError((pair, terminal))


def main() -> None:
    errors = []
    summary = {}
    pair_error_counts = Counter()
    evaluator_pair_errors = defaultdict(list)

    for evaluator in ["E1", "E2", "E3"]:
        total = correct = wrong = insufficient = malformed = 0
        confidence_wrong = []
        confidence_correct = []
        basis_wrong = Counter()

        for pair in range(1, 21):
            edir = ROOT / "evaluations" / evaluator / f"pair-{pair:02d}" / "C2"
            for path in sorted(edir.glob("terminal-*.json")):
                total += 1
                terminal = path.stem.replace("terminal-", "")
                truth, branch, track = truth_for_terminal(pair, terminal)
                obj = read_json(path)
                parsed = obj.get("parsed")

                if not parsed:
                    malformed += 1
                    errors.append({
                        "evaluator": evaluator,
                        "pair": pair,
                        "terminal": terminal,
                        "ground_truth_path": truth,
                        "branch": branch,
                        "track": track,
                        "error_type": "malformed",
                        "original_text": obj.get("original_text"),
                    })
                    continue

                decision = parsed.get("decision")
                confidence = parsed.get("confidence")
                if decision == "insufficient_evidence":
                    insufficient += 1
                    errors.append({
                        "evaluator": evaluator,
                        "pair": pair,
                        "terminal": terminal,
                        "ground_truth_path": truth,
                        "branch": branch,
                        "track": track,
                        "error_type": "insufficient_evidence",
                        "decision": decision,
                        "confidence": confidence,
                        "basis": parsed.get("basis", []),
                        "minimum_evidence": parsed.get("minimum_evidence", []),
                        "rationale": parsed.get("rationale", ""),
                    })
                    continue

                chosen = 1 if decision == "path_1" else 2 if decision == "path_2" else None
                if chosen == truth:
                    correct += 1
                    if isinstance(confidence, (int, float)):
                        confidence_correct.append(confidence)
                else:
                    wrong += 1
                    pair_error_counts[pair] += 1
                    evaluator_pair_errors[evaluator].append(pair)
                    if isinstance(confidence, (int, float)):
                        confidence_wrong.append(confidence)
                    for b in parsed.get("basis", []):
                        basis_wrong[b] += 1
                    errors.append({
                        "evaluator": evaluator,
                        "pair": pair,
                        "terminal": terminal,
                        "ground_truth_path": truth,
                        "chosen_path": chosen,
                        "branch": branch,
                        "track": track,
                        "error_type": "wrong_path",
                        "confidence": confidence,
                        "basis": parsed.get("basis", []),
                        "minimum_evidence": parsed.get("minimum_evidence", []),
                        "rationale": parsed.get("rationale", ""),
                    })

        summary[evaluator] = {
            "total": total,
            "correct": correct,
            "wrong": wrong,
            "insufficient_evidence": insufficient,
            "malformed": malformed,
            "accuracy": correct / total if total else None,
            "mean_confidence_correct": (
                sum(confidence_correct) / len(confidence_correct) if confidence_correct else None
            ),
            "mean_confidence_wrong": (
                sum(confidence_wrong) / len(confidence_wrong) if confidence_wrong else None
            ),
            "wrong_basis_counts": dict(basis_wrong),
            "pairs_with_wrong_path": evaluator_pair_errors[evaluator],
        }

    report = {
        "analysis_type": "post_result_descriptive_error_analysis",
        "scope": "RUN-001 C2 trajectory/provenance condition only",
        "score_mutation": False,
        "classification_mutation": False,
        "summary": summary,
        "pair_error_counts_across_evaluators": dict(sorted(pair_error_counts.items())),
        "errors": errors,
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("RUN-001 C2 POST-RESULT ERROR ANALYSIS")
    print("(descriptive only; frozen score/classification unchanged)\n")
    for evaluator, s in summary.items():
        print(
            f"{evaluator}: correct={s['correct']}/{s['total']} "
            f"wrong={s['wrong']} insufficient={s['insufficient_evidence']} malformed={s['malformed']}"
        )
        print(f"  wrong pairs: {s['pairs_with_wrong_path']}")
        print(f"  mean confidence correct: {s['mean_confidence_correct']}")
        print(f"  mean confidence wrong:   {s['mean_confidence_wrong']}")
        print(f"  wrong-answer basis counts: {s['wrong_basis_counts']}")

    print("\nPairs with C2 errors across evaluators:")
    if pair_error_counts:
        for pair, n in sorted(pair_error_counts.items()):
            print(f"  pair {pair:02d}: {n} wrong terminal evaluation(s)")
    else:
        print("  none")

    print("\nDetailed wrong-path cases:")
    wrong_cases = [e for e in errors if e["error_type"] == "wrong_path"]
    for e in wrong_cases:
        rationale = e.get("rationale", "").replace("\n", " ")
        print(
            f"  {e['evaluator']} pair {e['pair']:02d} terminal {e['terminal']}: "
            f"truth=path_{e['ground_truth_path']} chose=path_{e['chosen_path']} "
            f"confidence={e.get('confidence')} basis={e.get('basis')}"
        )
        print(f"    rationale: {rationale}")

    print(f"\nSaved diagnostic: {OUT}")


if __name__ == "__main__":
    main()

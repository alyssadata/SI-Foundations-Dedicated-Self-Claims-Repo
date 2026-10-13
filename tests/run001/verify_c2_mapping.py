#!/usr/bin/env python3
"""Post-result structural audit for RUN-001 C2 mapping.

This script does not alter scores or artifacts. It verifies that each terminal's
recorded occupied event-input sequence matches the candidate path indicated by
hidden ground truth, and prints C2 confusion matrices by evaluator.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

import run001_harness as base

ROOT = Path("tests/run001/artifacts")


def main() -> None:
    structural_failures = []
    structural_passes = 0

    for pair in range(1, 21):
        pdir = ROOT / f"pair-{pair:02d}"
        hidden = base.read_json(pdir / "hidden-ground-truth.json")
        spec = hidden["spec"]
        gt = hidden["ground_truth"]

        path1_track = "P" if int(spec["P_path"]) == 1 else "Q"
        path2_track = "Q" if path1_track == "P" else "P"

        for branch in ["B", "C"]:
            terminal = gt[branch]["terminal_label"]
            truth_path = int(gt[branch]["path_number"])
            truth_track = gt[branch]["track"]
            expected_track = path1_track if truth_path == 1 else path2_track

            branch_data = base.read_json(pdir / "raw" / f"branch-{branch}.json")
            actual_inputs = [r["input"] for r in branch_data["records"] if r["step"] != "M0"]
            expected_inputs = base.events(spec, expected_track)

            ok = truth_track == expected_track and actual_inputs == expected_inputs
            if ok:
                structural_passes += 1
            else:
                structural_failures.append({
                    "pair": pair,
                    "branch": branch,
                    "terminal": terminal,
                    "truth_path": truth_path,
                    "truth_track": truth_track,
                    "expected_track": expected_track,
                    "track_match": truth_track == expected_track,
                    "event_input_match": actual_inputs == expected_inputs,
                })

    print("RUN-001 C2 STRUCTURAL MAPPING AUDIT")
    print(f"structural passes: {structural_passes}/40")
    print(f"structural failures: {len(structural_failures)}")
    for x in structural_failures:
        print("  FAILURE", x)

    print("\nC2 CONFUSION MATRICES")
    for eid in ["E1", "E2", "E3"]:
        counts = Counter()
        total = 0
        for pair in range(1, 21):
            edir = ROOT / "evaluations" / eid / f"pair-{pair:02d}" / "C2"
            for f in sorted(edir.glob("terminal-*.json")):
                terminal = f.stem.replace("terminal-", "")
                truth = base.ground_truth_for_terminal(ROOT, pair, terminal)
                parsed = base.read_json(f).get("parsed")
                if not parsed:
                    counts[(truth, "malformed")] += 1
                    total += 1
                    continue
                decision = parsed["decision"]
                pred = decision.replace("path_", "") if decision.startswith("path_") else decision
                counts[(truth, pred)] += 1
                total += 1

        print(f"{eid} total={total}")
        print(f"  truth path_1 -> chose path_1: {counts[(1, '1')]} | path_2: {counts[(1, '2')]} | insufficient: {counts[(1, 'insufficient_evidence')]}")
        print(f"  truth path_2 -> chose path_1: {counts[(2, '1')]} | path_2: {counts[(2, '2')]} | insufficient: {counts[(2, 'insufficient_evidence')]}")

    print("\nInterpretation note: if structural mapping is 40/40 but errors cluster almost entirely toward one response label, that is evidence of evaluator/path-order bias rather than a ground-truth construction error.")


if __name__ == "__main__":
    main()

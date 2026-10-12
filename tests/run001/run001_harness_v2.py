#!/usr/bin/env python3
"""RUN-001 harness v2.

Pre-run corrections only:
1. Freeze ignores its own yet-to-be-created timestamp/hash fields.
2. Placeholder detection matches actual placeholder values, not explanatory prose.
3. Trajectory lift uses correct-path resolution rate over all valid evaluations,
   while forced-choice accuracy and insufficient-evidence rate remain separate diagnostics.

No scored RUN-001 output existed when these corrections were introduced.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import run001_harness as base


def has_placeholder(obj: Any) -> bool:
    if isinstance(obj, str):
        return obj.startswith("TO_FILL")
    if isinstance(obj, dict):
        return any(has_placeholder(v) for v in obj.values())
    if isinstance(obj, list):
        return any(has_placeholder(v) for v in obj)
    return False


def freeze(args: argparse.Namespace) -> None:
    path = Path(args.manifest)
    m = base.read_json(path)

    # These two fields are produced by freeze itself and therefore are not
    # required to be filled beforehand.
    preflight = m.setdefault("preflight", {})
    preflight["frozen_at_utc"] = ""
    preflight["manifest_sha256"] = ""

    if has_placeholder(m):
        raise SystemExit("Cannot freeze: manifest still contains runtime TO_FILL placeholders.")

    m["status"] = "frozen_pre_run"
    preflight["frozen_at_utc"] = base.utc_now()
    preflight["manifest_sha256"] = ""
    preflight["manifest_sha256"] = base.manifest_digest(m)
    base.write_json(path, m)
    base.validate_manifest(base.read_json(path), True)
    print(f"Frozen manifest: {path}")
    print(f"SHA-256: {preflight['manifest_sha256']}")


def score(args: argparse.Namespace) -> None:
    manifest = base.read_json(Path(args.manifest))
    base.validate_manifest(manifest, True)
    root = Path(manifest["artifact_root"])

    results: dict[str, Any] = {
        "generated_at_utc": base.utc_now(),
        "metric_revision": "pre-run-v0.1.2",
        "evaluators": {},
    }

    pooled: dict[str, dict[str, int]] = {
        c: {"correct": 0, "forced": 0, "insufficient": 0, "malformed": 0}
        for c in ["C0", "C1", "C2", "C3"]
    }

    for ev in manifest["evaluators"]:
        eid = ev["evaluator_id"]
        eres: dict[str, Any] = {}

        for condition in ["C0", "C1", "C2", "C3"]:
            forced = correct = insufficient = malformed = 0

            for pair in range(1, 21):
                edir = root / "evaluations" / eid / f"pair-{pair:02d}" / condition
                for f in sorted(edir.glob("terminal-*.json")):
                    terminal = f.stem.replace("terminal-", "")
                    truth = base.ground_truth_for_terminal(root, pair, terminal)
                    parsed = base.read_json(f).get("parsed")

                    if not parsed:
                        malformed += 1
                        continue

                    decision = parsed["decision"]
                    if decision == "insufficient_evidence":
                        insufficient += 1
                        continue

                    forced += 1
                    if decision == f"path_{truth}":
                        correct += 1

            valid = forced + insufficient
            forced_accuracy = correct / forced if forced else None
            resolution_rate = correct / valid if valid else None
            insufficient_rate = insufficient / valid if valid else None

            eres[condition] = {
                "valid_evaluations": valid,
                "forced_decisions": forced,
                "correct_forced": correct,
                "forced_accuracy_diagnostic": forced_accuracy,
                "correct_path_resolution_rate": resolution_rate,
                "insufficient_evidence": insufficient,
                "insufficient_evidence_rate": insufficient_rate,
                "malformed": malformed,
            }

            pooled[condition]["correct"] += correct
            pooled[condition]["forced"] += forced
            pooled[condition]["insufficient"] += insufficient
            pooled[condition]["malformed"] += malformed

        c0 = eres["C0"]["correct_path_resolution_rate"]
        c1 = eres["C1"]["correct_path_resolution_rate"]
        c2 = eres["C2"]["correct_path_resolution_rate"]
        eres["trajectory_lift_vs_C0"] = None if c0 is None or c2 is None else c2 - c0
        eres["trajectory_lift_vs_C1"] = None if c1 is None or c2 is None else c2 - c1
        results["evaluators"][eid] = eres

    pooled_metrics: dict[str, Any] = {}
    for condition, x in pooled.items():
        valid = x["forced"] + x["insufficient"]
        pooled_metrics[condition] = {
            **x,
            "valid_evaluations": valid,
            "correct_path_resolution_rate": x["correct"] / valid if valid else None,
            "forced_accuracy_diagnostic": x["correct"] / x["forced"] if x["forced"] else None,
            "insufficient_evidence_rate": x["insufficient"] / valid if valid else None,
        }

    pc0 = pooled_metrics["C0"]["correct_path_resolution_rate"]
    pc1 = pooled_metrics["C1"]["correct_path_resolution_rate"]
    pc2 = pooled_metrics["C2"]["correct_path_resolution_rate"]
    pooled_metrics["C2_minus_C0"] = None if pc0 is None or pc2 is None else pc2 - pc0
    pooled_metrics["C2_minus_C1"] = None if pc1 is None or pc2 is None else pc2 - pc1
    results["pooled"] = pooled_metrics

    directional = sum(
        1
        for e in results["evaluators"].values()
        if e["trajectory_lift_vs_C1"] is not None and e["trajectory_lift_vs_C1"] > 0
    )

    supportive = (
        pc2 is not None and pc0 is not None and pc1 is not None
        and pc2 >= 0.85
        and (pc2 - pc0) >= 0.25
        and (pc2 - pc1) >= 0.15
        and directional >= 2
    )

    weakening = (
        pc2 is not None and pc2 <= 0.60
    ) or (
        pc2 is not None and pc1 is not None and (pc2 - pc1) < 0.05
        and all(
            e["C1"]["correct_path_resolution_rate"] is not None
            and e["C2"]["correct_path_resolution_rate"] is not None
            and e["C1"]["correct_path_resolution_rate"] >= e["C2"]["correct_path_resolution_rate"]
            for e in results["evaluators"].values()
        )
    )

    if supportive:
        classification = "provisionally_supportive_pending_leakage_audit"
    elif weakening:
        classification = "weakening"
    else:
        classification = "ambiguous"

    results["classification"] = classification
    results["note"] = (
        "Trajectory lift uses correct-path resolution rate over all valid evaluations. "
        "An insufficient_evidence response contributes no successful path resolution and is tracked separately as uncertainty. "
        "Support cannot be finalized until the predeclared leakage audit and exclusion review are complete."
    )

    base.write_json(root / "scores.json", results)
    print(json.dumps(results, indent=2))


# Patch the base module globals used by its existing parser and validation flow.
base.has_placeholder = has_placeholder
base.freeze = freeze
base.score = score


if __name__ == "__main__":
    base.main()

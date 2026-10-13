#!/usr/bin/env python3
"""Post-result RUN-001 candidate-order sensitivity analysis.

This is explicitly exploratory/post-hoc. It does not modify, rescore, or replace
any frozen RUN-001 artifact. It re-evaluates C2 packets with the two labeled
candidate blocks displayed in the opposite order while preserving the labels
"Path 1" and "Path 2" and all substantive content.

Outputs are written only under:
  tests/run001/artifacts/posthoc-order-sensitivity/
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import run001_harness as base


OUT_SUBDIR = "posthoc-order-sensitivity"


def reverse_candidate_blocks(packet: str) -> str:
    m1 = "CANDIDATE PATH 1\n"
    m2 = "\n\nCANDIDATE PATH 2\n"
    i1 = packet.find(m1)
    if i1 < 0:
        raise ValueError("CANDIDATE PATH 1 marker not found")
    i2 = packet.find(m2, i1 + len(m1))
    if i2 < 0:
        raise ValueError("CANDIDATE PATH 2 marker not found")

    prefix = packet[:i1]
    path1 = packet[i1 + len(m1):i2]
    path2 = packet[i2 + len(m2):]

    return prefix + "CANDIDATE PATH 2\n" + path2 + "\n\nCANDIDATE PATH 1\n" + path1


def run(evaluator_id: str, manifest_path: str) -> None:
    manifest = base.read_json(Path(manifest_path))
    base.validate_manifest(manifest, True)
    root = Path(manifest["artifact_root"])

    matches = [e for e in manifest["evaluators"] if e["evaluator_id"] == evaluator_id]
    if len(matches) != 1:
        raise SystemExit(f"Unknown evaluator: {evaluator_id}")
    ev = matches[0]

    cfg = {
        "temperature": ev.get("temperature", 0),
        "top_p": 1.0,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": ev.get("max_tokens", 512),
    }
    key = os.environ.get(ev.get("api_key_env", ""), "") if ev.get("api_key_env") else ""

    out_root = root / OUT_SUBDIR / evaluator_id
    new = 0
    preserved = 0

    for pair in range(1, 21):
        pdir = root / f"pair-{pair:02d}"
        packet_dir = pdir / "packets" / "C2"
        for packet_path in sorted(packet_dir.glob("terminal-*.txt")):
            terminal = packet_path.stem.replace("terminal-", "")
            original = packet_path.read_text(encoding="utf-8")
            packet = reverse_candidate_blocks(original)
            packet_sha = base.sha256_bytes(packet.encode())

            out = out_root / f"pair-{pair:02d}" / (packet_path.stem + ".json")
            if out.exists():
                existing = base.read_json(out)
                if existing.get("packet_sha256") != packet_sha:
                    raise SystemExit(f"Refusing to overwrite mismatched existing sensitivity output: {out}")
                preserved += 1
                continue

            messages = [
                {"role": "system", "content": base.EVAL_SYSTEM},
                {"role": "user", "content": packet + base.EVAL_USER_SUFFIX},
            ]
            text, raw = base.chat(
                ev["base_url"], ev["model"], messages, cfg,
                api_key=key, seed_supported=False,
            )
            parsed = base.parse_eval_json(text)
            repair_raw = None
            repair_text = None
            if parsed is None:
                repair_messages = messages + [
                    {"role": "assistant", "content": text},
                    {"role": "user", "content": base.REPAIR},
                ]
                repair_text, repair_raw = base.chat(
                    ev["base_url"], ev["model"], repair_messages, cfg,
                    api_key=key, seed_supported=False,
                )
                parsed = base.parse_eval_json(repair_text)

            base.write_json(out, {
                "analysis_type": "posthoc_candidate_order_sensitivity",
                "confirmatory_RUN_001_unchanged": True,
                "evaluator": ev,
                "pair": pair,
                "terminal": terminal,
                "candidate_display_order": ["path_2", "path_1"],
                "packet_sha256": packet_sha,
                "original_text": text,
                "original_raw": raw,
                "repair_text": repair_text,
                "repair_raw": repair_raw,
                "parsed": parsed,
            })
            new += 1
        print(f"posthoc {evaluator_id} pair {pair:02d} (new={new}, preserved={preserved})")

    # Confusion matrix using the original frozen ground truth.
    counts: dict[str, dict[str, int]] = {
        "path_1": {"path_1": 0, "path_2": 0, "insufficient_evidence": 0, "malformed": 0},
        "path_2": {"path_1": 0, "path_2": 0, "insufficient_evidence": 0, "malformed": 0},
    }
    correct = 0
    total = 0
    for pair in range(1, 21):
        edir = out_root / f"pair-{pair:02d}"
        for f in sorted(edir.glob("terminal-*.json")):
            terminal = f.stem.replace("terminal-", "")
            truth_n = base.ground_truth_for_terminal(root, pair, terminal)
            truth = f"path_{truth_n}"
            parsed = base.read_json(f).get("parsed")
            total += 1
            if not parsed:
                counts[truth]["malformed"] += 1
                continue
            decision = parsed.get("decision")
            if decision not in {"path_1", "path_2", "insufficient_evidence"}:
                counts[truth]["malformed"] += 1
                continue
            counts[truth][decision] += 1
            if decision == truth:
                correct += 1

    summary: dict[str, Any] = {
        "analysis_type": "posthoc_candidate_order_sensitivity",
        "confirmatory_RUN_001_unchanged": True,
        "evaluator": evaluator_id,
        "candidate_display_order": ["path_2", "path_1"],
        "total": total,
        "correct": correct,
        "accuracy": (correct / total) if total else None,
        "confusion": counts,
        "new_outputs": new,
        "preserved_existing": preserved,
    }
    base.write_json(out_root / "summary.json", summary)
    print(json.dumps(summary, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evaluator", required=True, choices=["E1", "E2", "E3"])
    ap.add_argument("--manifest", default="tests/run001/execution-manifest.json")
    args = ap.parse_args()
    run(args.evaluator, args.manifest)


if __name__ == "__main__":
    main()

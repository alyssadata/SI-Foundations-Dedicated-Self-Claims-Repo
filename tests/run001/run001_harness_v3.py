#!/usr/bin/env python3
"""RUN-001 evaluation execution wrapper (v3).

Operational pre-evaluation correction only:
- run one frozen evaluator configuration at a time so local models can be
  loaded sequentially on memory-constrained hardware;
- preserve the exact frozen manifest, packets, evaluator prompt, parsing,
  one-repair policy, output schema, and scoring path;
- never overwrite an existing evaluator output;
- on transport/runtime interruption, resume by skipping only outputs whose
  stored packet SHA-256 matches the current packet exactly.

No evaluator outputs existed when this wrapper was introduced. Generation,
scoring, audit, and freeze remain governed by run001_harness_v2.py.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import run001_harness_v2 as v2  # noqa: F401  # installs v2 validation/scoring patches
import run001_harness as base


def evaluate_one(args: argparse.Namespace) -> None:
    manifest = base.read_json(Path(args.manifest))
    base.validate_manifest(manifest, True)
    root = Path(manifest["artifact_root"])
    if not root.exists():
        raise SystemExit("No generated artifacts. Run generate first.")

    matches = [ev for ev in manifest["evaluators"] if ev["evaluator_id"] == args.evaluator]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one evaluator {args.evaluator!r}; found {len(matches)}")
    ev = matches[0]

    key = os.environ.get(ev.get("api_key_env", ""), "") if ev.get("api_key_env") else ""
    cfg = {
        "temperature": ev.get("temperature", 0),
        "top_p": 1.0,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": ev.get("max_tokens", 512),
    }

    completed = 0
    skipped = 0

    for pair in range(1, 21):
        pdir = root / f"pair-{pair:02d}"
        for condition in ["C0", "C1", "C2", "C3"]:
            for packet_path in sorted((pdir / "packets" / condition).glob("terminal-*.txt")):
                packet = packet_path.read_text(encoding="utf-8")
                packet_sha = base.sha256_bytes(packet.encode())
                out = (
                    root
                    / "evaluations"
                    / ev["evaluator_id"]
                    / f"pair-{pair:02d}"
                    / condition
                    / (packet_path.stem + ".json")
                )

                if out.exists():
                    prior = base.read_json(out)
                    if prior.get("packet_sha256") != packet_sha:
                        raise SystemExit(
                            f"Existing output packet hash mismatch; refusing overwrite: {out}"
                        )
                    skipped += 1
                    continue

                messages = [
                    {"role": "system", "content": base.EVAL_SYSTEM},
                    {"role": "user", "content": packet + base.EVAL_USER_SUFFIX},
                ]
                text, raw = base.chat(
                    ev["base_url"],
                    ev["model"],
                    messages,
                    cfg,
                    api_key=key,
                    seed_supported=False,
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
                        ev["base_url"],
                        ev["model"],
                        repair_messages,
                        cfg,
                        api_key=key,
                        seed_supported=False,
                    )
                    parsed = base.parse_eval_json(repair_text)

                base.write_json(
                    out,
                    {
                        "evaluator": ev,
                        "packet_sha256": packet_sha,
                        "original_text": text,
                        "original_raw": raw,
                        "repair_text": repair_text,
                        "repair_raw": repair_raw,
                        "parsed": parsed,
                    },
                )
                completed += 1

        print(
            f"evaluated {ev['evaluator_id']} pair {pair:02d} "
            f"(new={completed}, preserved={skipped})"
        )

    print(
        f"Evaluator {ev['evaluator_id']} complete: "
        f"new_outputs={completed}, preserved_existing={skipped}"
    )


def main() -> None:
    p = argparse.ArgumentParser(description="RUN-001 per-evaluator execution wrapper")
    sp = p.add_subparsers(dest="cmd", required=True)

    q = sp.add_parser("evaluate", help="Run exactly one frozen evaluator configuration")
    q.add_argument("--manifest", default="tests/run001/execution-manifest.json")
    q.add_argument("--evaluator", choices=["E1", "E2", "E3"], required=True)
    q.set_defaults(func=evaluate_one)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

# RUN-001 — Evaluation Execution Revision

**Date:** 2026-10-12  
**Status:** Pre-evaluation operational revision  
**Parent run:** RUN-001 — Fork Individuation  
**Generation status at revision:** 20 fork pairs generated  
**Evaluator-output status at revision:** 0 evaluator output files existed  
**New execution wrapper:** `tests/run001/run001_harness_v3.py`  
**Wrapper introduction commit:** `e274dd062159ea67b01ed87d1ad984e1d1cea61a`

## Trigger

The first monolithic evaluator attempt timed out before writing any evaluator output. Inspection showed multiple large local models resident simultaneously on a 24 GB unified-memory system. LM Studio's JIT auto-eviction does not evict models that were manually loaded, so the all-evaluators-in-one-process execution path created avoidable memory pressure.

The generated RUN-001 branch artifacts were unaffected. At the time this revision was introduced:

- all 20 fork pairs had already been generated under the frozen execution manifest;
- no evaluator JSON output file existed under `tests/run001/artifacts/evaluations/`;
- no score had been computed;
- no evaluator result had been observed or used to motivate a substantive methodological change.

## Change

Evaluation execution may now be run one frozen evaluator configuration at a time using:

```bash
python3 tests/run001/run001_harness_v3.py evaluate --evaluator E1
python3 tests/run001/run001_harness_v3.py evaluate --evaluator E2
python3 tests/run001/run001_harness_v3.py evaluate --evaluator E3
```

The operator may unload the prior local model and load the next frozen evaluator model between these commands.

`run001_harness_v3.py` is an execution wrapper only. It reads the same frozen `execution-manifest.json` and uses the same evaluator entries already frozen there.

## Preserved without change

This revision does **not** change:

- the 20 generated fork pairs;
- the canonical predecessor checkpoints;
- C0, C1, C2, or C3 packet contents;
- evaluator IDs E1/E2/E3;
- evaluator model identifiers;
- evaluator system prompt;
- evaluator user prompt;
- temperature or token limits;
- JSON schema;
- the one-format-repair policy;
- hidden ground truth;
- support or weakening thresholds;
- scoring rules;
- leakage-audit rules;
- CLAIM-001 or its interpretation boundary.

Generation, freeze, audit, and scoring remain governed by `run001_harness_v2.py`.

## Resume / overwrite rule

The wrapper is fail-closed with respect to prior evaluator outputs.

Before issuing an evaluator request, it checks whether the target output file already exists.

- If no file exists, it performs the frozen evaluator request and writes the result.
- If a file exists and its stored packet SHA-256 exactly matches the current packet, the prior output is preserved and skipped.
- If a file exists but the packet SHA-256 differs, execution aborts.

Therefore a transport/runtime interruption can be resumed without rerunning or overwriting already completed substantive evaluator outputs.

A timeout that occurs before a valid response is written remains a transport/runtime failure, not an evaluator reconsideration. The existing one-format-repair rule for malformed JSON is unchanged.

## Methodological classification

This is an **operational execution correction**, not a substantive protocol revision. Its purpose is to permit the already-frozen evaluator configurations to run sequentially on the available hardware while preserving exactly the same evaluation task and output structure.

Because the change was made after branch generation but before any evaluator output existed, generated system data remain fixed and evaluator behavior could not have influenced the correction.

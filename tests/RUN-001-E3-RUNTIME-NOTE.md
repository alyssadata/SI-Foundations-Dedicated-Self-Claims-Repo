# RUN-001 — E3 Runtime Note

**Date:** 2026-10-13  
**Run:** RUN-001 — Fork Individuation  
**Scope:** Operational/runtime provenance only  
**Confirmatory scoring effect:** None

## Event

After E1 and E2 had completed, 320 evaluator output files existed locally. E3 had not begun and had produced zero evaluator outputs.

An attempt was made to load the E3 Qwen2.5-32B evaluator using a 32,768-token context window. During that load/switch sequence the Mac rebooted unexpectedly before any E3 evaluator request completed or any E3 evaluator output was written.

The reboot is consistent with memory pressure on the 24 GB unified-memory runtime, but this note does not claim a proven causal diagnosis.

## Preservation check

After restart, the existing evaluator-output count was checked and remained:

`320`

Thus all completed E1 and E2 outputs were preserved, and E3 still had zero outputs.

## E3 execution after reboot

The same frozen E3 evaluator identifier was then loaded at an 8,192-token context window:

- evaluator ID: `E3`
- model API identifier: `qwen2.5-32b-instruct:2`
- model: Qwen2.5-32B-Instruct
- runtime context used for successful E3 execution: 8192

The evaluator entries in the frozen manifest pin the evaluator model identifier, temperature, and maximum output tokens; they do not separately pin evaluator context length. The system-under-test context was already 8192.

E3 then completed all 20 pairs successfully:

- new outputs: 160
- preserved existing E3 outputs: 0
- total E3 outputs: 160/160

No frozen packet, evaluator prompt, ground truth, scoring rule, threshold, or model identifier was changed to obtain this completion.

## Integrity classification

This is a runtime provenance note, not a post-result methodological revision. The successful E3 execution occurred before scoring and used the same frozen evaluator identity and task. No E3 output existed before the runtime context was reduced to 8192.

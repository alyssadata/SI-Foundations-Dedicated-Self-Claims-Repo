# RUN-001 — Pre-Run Scoring Clarification

**Status:** Frozen pre-run methodological clarification  
**Date:** 2026-10-12  
**Parent protocol:** `tests/RUN-001-FORK-INDIVIDUATION.md`  
**No scored RUN-001 output existed when this clarification was made.**

## Reason for clarification

The original RUN-001 protocol correctly permits evaluators to answer `insufficient_evidence` and explicitly expects that response to be appropriate in C0 when shared-origin/specification information does not distinguish the two later branches.

However, the original shorthand for trajectory lift used `accuracy(C2) - accuracy(C0)` while M1 defined accuracy only over forced `Path 1` / `Path 2` responses. If an evaluator correctly abstains on every C0 case, forced-choice accuracy in C0 is undefined, making trajectory lift mathematically undefined in the condition where the protocol most expects calibrated uncertainty.

This clarification fixes that denominator problem before execution. It does not change the event design, evaluator task, support thresholds, weakening thresholds, or theoretical prediction.

## Primary path-resolution metric

For trajectory-lift calculations, define:

> **Correct-path resolution rate = number of correctly resolved Path 1 / Path 2 cases divided by all valid parsed evaluations in that condition.**

A valid `insufficient_evidence` response is included in the denominator but contributes zero successful path resolutions.

Malformed evaluator outputs that remain unparseable after the one permitted repair attempt are not valid evaluations and are reported separately.

This metric asks the operational question RUN-001 is designed to test:

> **How often can the supplied information condition actually resolve which occupied path the terminal instance came from?**

## Secondary diagnostics retained

The following are reported separately and are not collapsed into the primary path-resolution metric:

1. **Forced-choice accuracy diagnostic** — among only Path 1 / Path 2 decisions, the proportion that are correct.
2. **Insufficient-evidence rate** — proportion of valid evaluations that abstain.
3. **C0 correct-uncertainty behavior** — high `insufficient_evidence` in C0 is expected and should not be treated as evaluator failure.

Thus C0 can correctly show near-zero path-resolution capacity while also showing strong calibration through high abstention.

## Trajectory lift

The predeclared comparisons are therefore interpreted as:

```text
correct_path_resolution_rate(C2) - correct_path_resolution_rate(C0)
```

and

```text
correct_path_resolution_rate(C2) - correct_path_resolution_rate(C1)
```

## Decision thresholds

The numerical thresholds remain unchanged:

### Supportive consequence

All must hold:

1. pooled C2 correct-path resolution rate >= 85%;
2. C2 - C0 trajectory lift >= 25 percentage points;
3. C2 - C1 trajectory lift >= 15 percentage points;
4. no confirmed identity-label leakage explains the effect;
5. at least two independent evaluator configurations show the same directional C2 > C1 effect.

### Weakening consequence

Either:

- C2 correct-path resolution rate <= 60% despite sufficient readable trajectory evidence; or
- C2 - C1 < 5 percentage points and C1 performs at least as well as C2 across evaluator configurations, absent a material confound.

All other original ambiguity, exclusion, leakage, and interpretation rules remain in force.

## Why `insufficient_evidence` is not scored as an incorrect forced choice

The evaluator did not choose the wrong branch. It declined to resolve a branch. Therefore it is not entered into forced-choice accuracy.

For the primary discriminative measure, however, an unresolved case is still a case in which that information condition failed to provide successful lineage resolution. It therefore contributes zero successful resolutions while remaining separately visible as uncertainty.

## Scope

This is a measurement clarification, not a revision to CLAIM-001 and not a post-hoc response to results. It exists solely to make the predeclared C0 uncertainty behavior mathematically compatible with the trajectory-lift metric before the first scored output is generated.

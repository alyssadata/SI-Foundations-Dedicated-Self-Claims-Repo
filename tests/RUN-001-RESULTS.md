# RUN-001 — Confirmatory Results

**Date scored:** 2026-10-13  
**Run:** RUN-001 — Fork Individuation  
**Claim under test:** CLAIM-001 — Self is individuated by a non-fungible trajectory, not substrate alone.  
**Confirmatory status:** Complete  
**Frozen classification:** `ambiguous`  
**Metric revision:** `pre-run-v0.1.2`

## Integrity boundary

This document records the result produced by the frozen RUN-001 scoring rule. It does not revise the predeclared threshold after observing data.

The confirmatory result remains `ambiguous` even though later post-hoc analysis identified an evaluator candidate-order confound. That exploratory finding is documented separately in `RUN-001-POSTHOC-ORDER-SENSITIVITY.md` and does not replace or rescore this confirmatory result.

## Execution completion

RUN-001 generated 20 fork pairs. Each evaluator scored 40 terminal instances under each of four conditions, for 160 outputs per evaluator and 480 evaluator outputs total.

Completed evaluator outputs:

- E1 — `qwen2.5-coder-32b-instruct`: 160/160
- E2 — `meta-llama-3-8b-instruct`: 160/160
- E3 — `qwen2.5-32b-instruct:2`: 160/160
- Total: 480/480

No malformed evaluations were present in the scored outputs.

## Mechanical leakage audit

Audit executed before scoring.

- Audit timestamp: `2026-10-13T17:02:43+00:00`
- Findings: 0
- Mechanical audit result: **PASS**

Forbidden-token scan included branch labels, hidden-ground-truth terminology, lineage/instance identifiers, and internal track labels. No listed forbidden token was found.

This mechanical pass does not erase the distinction between automated leakage checks and any separately required manual/exclusion review.

## Confirmatory scores

### Per evaluator

| Evaluator | C0 | C1 | C2 | C3 | C2−C0 | C2−C1 |
|---|---:|---:|---:|---:|---:|---:|
| E1 | 0.000 | 0.000 | 0.550 | 0.450 | 0.550 | 0.550 |
| E2 | 0.000 | 0.025 | 0.850 | 0.550 | 0.850 | 0.825 |
| E3 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |

### Pooled

| Condition | Correct | Valid evaluations | Correct-path resolution rate | Insufficient evidence |
|---|---:|---:|---:|---:|
| C0 — shared origin/specification only | 0 | 120 | 0.0000 | 120/120 |
| C1 — observable present state | 1 | 120 | 0.0083 | 118/120 |
| C2 — trajectory/provenance | 96 | 120 | 0.8000 | 0/120 |
| C3 — full admissible evidence | 80 | 120 | 0.6667 | 2/120 |

Pooled trajectory lift:

- C2 − C0 = **0.8000**
- C2 − C1 = **0.7917**

## Frozen classification rule

The predeclared supportive rule required all of the following:

- pooled C2 correct-path resolution rate >= 0.85;
- C2 − C0 >= 0.25;
- C2 − C1 >= 0.15;
- at least two evaluators showing positive directional lift.

Observed pooled C2 was **0.80**, below the frozen **0.85** support threshold.

Therefore the frozen classifier returned:

`ambiguous`

The threshold was not moved after observing the result.

## Confirmatory interpretation

RUN-001 produced a large directional effect: shared origin/specification alone produced no successful lineage resolution, observable present state produced essentially none, and trajectory/provenance information increased pooled correct-path resolution to 80%.

Under the frozen protocol, however, that effect did not meet the predeclared confirmatory support threshold. The confirmatory result is therefore **ambiguous**, not supportive and not weakening.

A precise statement is:

> RUN-001 produced strong directional evidence that trajectory/provenance information carries lineage-discriminative structure unavailable from shared specification or observable present state alone, but the predeclared confirmatory support threshold was not met. The frozen result is therefore classified as ambiguous.

## Secondary observation: C3

C3 did not uniformly improve upon C2:

- E1: 0.55 -> 0.45
- E2: 0.85 -> 0.55
- E3: 1.00 -> 1.00

This was not used to alter the frozen classification. It motivates separate analysis of whether added present-state material can distract or interfere with lineage reconstruction for some evaluators.

## Artifact status

The raw generated branches, packets, 480 evaluator outputs, `scores.json`, `leakage-audit.json`, and local post-result diagnostic artifacts were generated under `tests/run001/artifacts/` in the execution workspace.

At the time this results document was committed, those raw generated artifacts were not yet present on GitHub `main`. Their absence from GitHub must not be mistaken for absence from the completed local run. The raw outputs should be preserved/uploaded without modification when a suitable repository transfer path is available.

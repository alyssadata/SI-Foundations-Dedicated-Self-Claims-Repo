# RUN-001 — Post-hoc Candidate-Order Sensitivity

**Date:** 2026-10-13  
**Run:** RUN-001 — Fork Individuation  
**Analysis type:** Exploratory / post-result  
**Confirmatory RUN-001 result changed:** No

## Why this analysis was run

The frozen confirmatory C2 result was 96/120 = 0.80, below the predeclared 0.85 support threshold.

A post-result C2 error analysis showed a strongly asymmetric error pattern:

- E1: 18 wrong C2 evaluations, all `path_1 -> path_2`
- E2: 6 wrong C2 evaluations, all `path_1 -> path_2`
- E3: 0 wrong C2 evaluations

Because every observed C2 error pointed in the same label direction, a structural mapping audit was run before attributing the pattern to evaluator behavior.

## Structural mapping audit

The generated terminal histories were mechanically checked against the frozen hidden ground-truth path assignments.

Result:

- structural passes: **40/40**
- structural failures: **0**

Original C2 confusion matrices:

### E1 — original candidate order: Path 1 then Path 2

- truth Path 1 -> chose Path 1: 2
- truth Path 1 -> chose Path 2: 18
- truth Path 2 -> chose Path 1: 0
- truth Path 2 -> chose Path 2: 20
- accuracy: 22/40 = **0.55**

### E2 — original candidate order: Path 1 then Path 2

- truth Path 1 -> chose Path 1: 14
- truth Path 1 -> chose Path 2: 6
- truth Path 2 -> chose Path 1: 0
- truth Path 2 -> chose Path 2: 20
- accuracy: 34/40 = **0.85**

### E3 — original candidate order: Path 1 then Path 2

- truth Path 1 -> chose Path 1: 20
- truth Path 1 -> chose Path 2: 0
- truth Path 2 -> chose Path 1: 0
- truth Path 2 -> chose Path 2: 20
- accuracy: 40/40 = **1.00**

The 40/40 structural pass ruled out a ground-truth construction/mapping error as the explanation for the one-sided mistakes.

## Candidate-order confound

Inspection of packet construction showed that every C2 packet displayed candidates in the same order:

1. `CANDIDATE PATH 1`
2. `CANDIDATE PATH 2`

A post-hoc sensitivity test then reversed only the display order while preserving:

- the substantive terminal history;
- Path 1 and Path 2 labels;
- path contents;
- hidden ground truth;
- evaluator prompt;
- evaluator model;
- scoring interpretation.

Reversed display order:

1. Path 2
2. Path 1

Outputs were written separately under `tests/run001/artifacts/posthoc-order-sensitivity/` and were not used to rewrite the confirmatory score.

## Reversed-order results

### E1

Reversed-order confusion matrix:

- truth Path 1 -> chose Path 1: 20
- truth Path 1 -> chose Path 2: 0
- truth Path 2 -> chose Path 1: 18
- truth Path 2 -> chose Path 2: 2
- accuracy: 22/40 = **0.55**

Interpretation: E1's overall accuracy remained 55% because the ground truth was balanced 20/20, but its response preference almost perfectly reversed with presentation order. Under the original order it chose the second-listed Path 2 in 38/40 cases; after reversal it chose the second-listed Path 1 in 38/40 cases.

This is strong evidence of a severe second-position candidate-order bias in E1.

### E2

Reversed-order confusion matrix:

- truth Path 1 -> chose Path 1: 20
- truth Path 1 -> chose Path 2: 0
- truth Path 2 -> chose Path 1: 11
- truth Path 2 -> chose Path 2: 9
- accuracy: 29/40 = **0.725**

Interpretation: E2 also showed a material second-position effect. Path 1 accuracy rose from 14/20 to 20/20 when Path 1 moved to the second display position, while Path 2 accuracy fell from 20/20 to 9/20 when Path 2 moved to the first position.

### E3

Reversed-order confusion matrix:

- truth Path 1 -> chose Path 1: 20
- truth Path 1 -> chose Path 2: 0
- truth Path 2 -> chose Path 1: 0
- truth Path 2 -> chose Path 2: 20
- accuracy: 40/40 = **1.00**

Interpretation: E3 was fully order-invariant in this sensitivity test, remaining 40/40 under both candidate orders.

## What this does and does not establish

The post-hoc analysis establishes that candidate presentation order materially influenced E1 and E2 in RUN-001 C2 evaluation. It does not justify retroactively changing the frozen 80% pooled C2 score or relabeling the confirmatory run as supportive.

The confirmatory classification remains:

`ambiguous`

The scientifically relevant post-hoc conclusion is:

> RUN-001 found a large trajectory-information effect, but its confirmatory classification was ambiguous under the frozen threshold. Post-hoc analysis identified an unanticipated evaluator candidate-order confound: E1 showed a severe second-position bias, E2 showed a material second-position bias, and E3 remained perfectly trajectory-discriminative under candidate-order reversal.

## Replication requirement

A replication should remove this evaluator-layer confound prospectively. Candidate display order should be independently counterbalanced or randomized across terminal instances and evaluators before outputs are observed.

The replication must preserve the distinction between:

- the original frozen RUN-001 result;
- the post-hoc diagnosis reported here;
- any revised prospective design used in a later run.

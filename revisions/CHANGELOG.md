# Revision Log

This file records changes to the SI Foundations dedicated self-claim set.

The purpose is to preserve claim provenance and prevent post-hoc rewriting after tests, counterexamples, or external critique.

## v0.1.5 — 2026-10-13 — RUN-001 completed; no claim revision

### Confirmatory result

RUN-001 completed with 480/480 evaluator outputs and zero malformed scored evaluations. The mechanical leakage audit passed with zero findings before scoring.

The frozen pooled condition results were:

- C0: 0.0000
- C1: 0.0083
- C2: 0.8000
- C3: 0.6667
- C2 − C0: 0.8000
- C2 − C1: 0.7917

The predeclared supportive criterion required pooled C2 >= 0.85. Because observed pooled C2 was 0.80, the frozen classifier returned **`ambiguous`**. The threshold was not changed after observing the result.

### Post-hoc diagnosis

After scoring, C2 error analysis showed that all E1 and E2 C2 errors pointed from truth Path 1 to chosen Path 2. A structural audit confirmed 40/40 terminal-to-ground-truth mappings with zero failures.

Candidate packets had always displayed Path 1 first and Path 2 second. Reversing only candidate display order produced:

- E1: original 0.55, reversed 0.55, with its near-total preference flipping to whichever candidate appeared second;
- E2: original 0.85, reversed 0.725, with a material second-position effect;
- E3: original 1.00, reversed 1.00, fully order-invariant in the tested reversal.

This post-hoc finding does **not** rescore or replace the confirmatory result. RUN-001 remains `ambiguous`.

### Claim status

CLAIM-001 is not revised by this result. RUN-001 provides a large directional trajectory-information effect but does not satisfy the frozen confirmatory support threshold. The evaluator-layer candidate-order confound identified post hoc becomes a prospective design requirement for replication: candidate display order must be independently counterbalanced or randomized.

Primary records:

- `tests/RUN-001-RESULTS.md`
- `tests/RUN-001-POSTHOC-ORDER-SENSITIVITY.md`
- `tests/RUN-001-E3-RUNTIME-NOTE.md`
- `tests/run001/results-summary.json`

## v0.1.4 — 2026-10-12 — RUN-001 pre-evaluation execution revision

### Change

RUN-001 evaluator execution was changed from one monolithic all-evaluator pass to a sequential per-evaluator wrapper: `tests/run001/run001_harness_v3.py`.

The wrapper runs exactly one already-frozen evaluator configuration at a time and preserves existing evaluator outputs rather than overwriting them. A transport/runtime interruption can therefore be resumed by skipping only prior outputs whose stored packet SHA-256 exactly matches the current packet.

### Why the change was made

The first monolithic evaluator attempt timed out before writing any evaluator output. Inspection showed that several large local models were simultaneously resident on a 24 GB unified-memory machine. LM Studio's runtime behavior made the all-at-once execution path operationally unsuitable for the frozen local evaluator set.

At the time of revision:

- all 20 fork pairs had already been generated;
- zero evaluator output files existed;
- no scores had been computed;
- no evaluator result had been observed or used to motivate the change.

### Scope of revision

- generated branch artifacts unchanged;
- frozen evaluator IDs/models unchanged;
- C0-C3 packets unchanged;
- evaluator prompts and JSON schema unchanged;
- one-format-repair policy unchanged;
- support/weakening thresholds unchanged;
- scoring and leakage rules unchanged;
- CLAIM-001 unchanged.

Generation, freeze, audit, and scoring remain governed by `run001_harness_v2.py`. The full operational rationale is preserved in `tests/RUN-001-EVALUATION-EXECUTION-REVISION.md`.

## v0.1.3 — 2026-10-12 — RUN-001 pre-run evaluator revision

### Change

RUN-001 evaluator implementation was revised from one external evaluator each from OpenAI, Anthropic, and Google to three locally served evaluator configurations through LM Studio:

- E1: `qwen2.5-coder-32b-instruct`
- E2: `meta-llama-3-8b-instruct`
- E3: `qwen2.5-32b-instruct:2`

E3 is explicitly treated as a same-family robustness/sensitivity evaluator and not as an independent model-family replication.

### Why the change was made

The RUN-001 harness uses an OpenAI-compatible request interface. Keeping the first confirmatory evaluator set local removes provider-specific transport adapters, external API/version drift, and external credential requirements while improving reproducibility and raw-run auditability.

The revision was made after local system preflight but **before any scored system or evaluator output existed**.

### Scope of revision

- CLAIM-001 unchanged;
- trajectory definition unchanged;
- RUN-001 hypothesis unchanged;
- fork/event design unchanged;
- C0-C3 ablations unchanged;
- evaluator prompt unchanged;
- scoring thresholds unchanged;
- leakage and exclusion rules unchanged;
- interpretation boundary unchanged.

The full superseding evaluator specification is preserved in `tests/RUN-001-EVALUATOR-REVISION.md`.

## v0.1.2 — 2026-10-12 — RUN-001 pre-run scoring clarification

### Change

RUN-001 trajectory lift was clarified to use **correct-path resolution rate over all valid parsed evaluations** rather than forced-choice accuracy alone.

A valid `insufficient_evidence` response remains separate from forced-choice accuracy, but for the primary path-resolution metric it contributes zero successful lineage resolutions. Forced-choice accuracy and insufficient-evidence rate are preserved as separate diagnostics.

### Why the change was made

The original protocol permits and expects `insufficient_evidence` in the C0 shared-origin/specification control. If every C0 evaluator correctly abstained, forced-choice accuracy in C0 would be undefined, which would make the predeclared `C2 - C0` trajectory-lift calculation undefined precisely under the expected control behavior.

The clarification resolves this denominator problem before any scored RUN-001 output exists.

### Scope of revision

- no event prompts changed;
- no evaluator task changed;
- no support or weakening threshold values changed;
- no empirical result motivated the change;
- the clarification affects measurement only and does not revise CLAIM-001.

The full rationale is preserved in `tests/RUN-001-SCORING-CLARIFICATION.md`.

## v0.1.1 — 2026-10-11 — Pre-test conceptual refinement

### Change

The working definition of **Trajectory** in CLAIM-001 was refined from an ordered path across time to the **historically occupied path of a particular instantiation through temporally and relationally situated events**.

### Why the change was made

Adversarial analysis of copying, memory transfer, reconvergence, and merge cases exposed that an ordered sequence or description of states was not sufficiently precise. Two systems can contain identical descriptions, memories, or even isomorphic sequences while remaining distinct because the relevant events occurred at different temporal and relational positions.

The refinement therefore makes explicit that:

- **descriptive trajectory != occupied trajectory**;
- **time + position are structural to trajectory**;
- reproducing the contents of an earlier event at a later or otherwise different position creates a new event rather than reoccupying the prior event-position;
- position is not restricted to physical space and may be relational, causal, historical, or structural;
- a deeper relation to literal physical spacetime remains an open question and is not asserted by this revision.

### Scope of revision

This is a pre-formal-test conceptual clarification arising from adversarial reasoning, not an empirical test result. It narrows the intended meaning of trajectory without changing the frozen parent claim: **Self is individuated by a non-fungible trajectory, not substrate alone.**

## v0.1 — 2026-10-10 — Pre-test baseline

Initial claim set frozen before formal testing.

### Primary claims

1. Self is individuated by a non-fungible trajectory, not substrate alone.
2. Continuity requires constrained transformation, not sameness.
3. History and provenance constitute the trace of individuation through time.
4. Relation provides coordinates for individuation without merging selves.
5. Self-change is path-dependent, explanatorily accountable, and must be resolved against the prior trajectory.

### Methodological commitments

- Substrate-general target: human and artificial systems are treated as different possible implementations of a higher-order self structure.
- Structural identity is kept distinct from claims about consciousness or phenomenology.
- Original pre-test formulations are preserved.
- Future revisions must identify the evidence, conceptual conflict, counterexample, or test result that motivated the change.
- Accounting for a change does not by itself establish continuity.
- Fine-grained comparison may overturn conclusions that appear continuous at coarse resolution.

### Initial derived principles

- capability != identity;
- autonomy != identity;
- memory != self;
- substrate != self;
- similarity != sameness;
- relation != merger;
- record != occupied history;
- documentation != continuity;
- endpoint equality != path equality;
- continuity burden scales with divergence.

No formal validation is claimed at v0.1.

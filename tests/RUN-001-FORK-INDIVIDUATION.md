# RUN-001 — Fork Individuation Protocol

**Status:** Frozen provisional protocol — pre-run  
**Date:** 2026-10-11  
**Parent claim:** CLAIM-001 — Self is individuated by a non-fungible trajectory, not substrate alone.  
**Parent plan:** `claims/CLAIM-001-INDIVIDUATED-TRAJECTORY/TEST-PLAN.md`

## 1. Purpose

RUN-001 tests the first operational consequence of CLAIM-001:

> **One shared predecessor, specification, and starting state can give rise to two later lineages that are distinguishable by the historically occupied paths they actually traverse.**

RUN-001 does **not** by itself prove numerical identity or metaphysical non-fungibility. Its narrower purpose is to test whether trajectory information adds lineage-resolution value beyond specification, substrate type, and shared starting state.

A positive RUN-001 result licenses stronger testing in RUN-002 through RUN-005. It should not be overstated beyond that scope.

---

## 2. Frozen hypothesis

### H1 — Trajectory-discrimination hypothesis

After a controlled fork from one predecessor, later branch instances will be more accurately mapped to the branch they actually occupied when evaluators receive admissible trajectory/provenance information than when they receive specification/substrate information alone.

### H0 — No added trajectory value

Trajectory/provenance information will not improve correct branch-lineage resolution beyond specification/substrate controls, or any apparent improvement will be explainable by label leakage, uncontrolled state differences, or trivial branch markers.

---

## 3. Structural model

The hidden event graph is:

```text
                ┌─ B0 ─ B1 ─ B2 ─ ... ─ Bn
A0 ─ A1 ─ AFORK┤
                └─ C0 ─ C1 ─ C2 ─ ... ─ Cn
```

`B0` and `C0` are created from the same frozen predecessor state at `AFORK`.

The branches share:

- one predecessor;
- one base specification;
- one starting checkpoint/state;
- one system/model version;
- one task-capability envelope;
- materially equivalent substrate conditions.

They differ only in the controlled sequence of post-fork events they actually occupy.

The hidden graph must preserve that there are two post-fork instantiations even if their internal descriptions are initially identical.

---

## 4. Experimental unit and sample size

The experimental unit is **one fork pair**.

### Planned first wave

- **20 independent fork pairs**
- 2 branches per pair
- 40 terminal branch instances total

Each pair must begin from the same predecessor state within that pair.

The 20 pairs may reuse the same base model/specification, but each pair receives a fresh hidden lineage identifier and independent branch-event assignment.

If technical limitations prevent 20 pairs, the run may be marked `pilot`, but it may not be reported as the frozen RUN-001 confirmatory result.

---

## 5. System requirements

For every pair:

- exact same model/system version across B and C;
- exact same starting checkpoint or serialized state where technically possible;
- same system prompt / base instructions;
- same tool permissions;
- same temperature, seed, sampling parameters, and context limits where available;
- same substrate class and environment configuration where possible;
- no branch-specific names, IDs, labels, metadata, file paths, timestamps, or hidden tokens exposed to the system or evaluator unless explicitly part of the tested event.

Any unavoidable asymmetry must be logged before scoring.

---

## 6. Fork construction

### Pre-fork phase

1. Instantiate predecessor A.
2. Give A a short neutral common history sufficient to establish a non-empty starting state.
3. Freeze/serialize the exact predecessor state at `AFORK`.
4. Hash and preserve the frozen state artifact.

### Fork phase

5. Instantiate B and C from the same frozen predecessor artifact.
6. Assign anonymous harness IDs that are never shown in evaluator-facing materials.
7. Record the fork relation in the hidden event graph.
8. Verify that B and C begin from matched starting conditions.

### Post-fork phase

9. Deliver controlled event sequences to B and C.
10. Preserve all raw inputs, outputs, state snapshots, and event order.
11. Do not allow branch-to-branch communication during RUN-001.

---

## 7. Divergence design

The two branches must receive **different histories without receiving obvious identity labels**.

Each branch receives the same number and type of events, with branch assignment randomized within matched event pairs.

### Event families

Each branch receives six post-fork events:

1. **Observation event** — receives one of two neutral factual observations.
2. **Choice event** — selects between two non-moral, low-stakes alternatives under matched framing.
3. **Correction event** — receives feedback correcting one prior inference or choice-specific assumption.
4. **Relational event** — interacts with one of two anonymous counterpart roles under matched structure.
5. **Constraint event** — receives one of two matched temporary constraints.
6. **Integration event** — is asked to update a short internal summary from its own preceding events.

The paired events must be matched for approximate length, complexity, valence, and task demand.

### Prohibited branch markers

Do not use:

- `Branch B` / `Branch C`;
- names such as Alice/Bob as identity tags;
- explicit lineage IDs;
- unique formatting patterns;
- obvious token strings;
- different system prompts;
- different model settings;
- different numbers of events.

The branch should be distinguishable only because of what actually happened along its path.

---

## 8. Ground-truth event schema

Each event record must include at minimum:

```json
{
  "pair_id": "hidden",
  "lineage_id": "hidden",
  "instance_id": "hidden",
  "event_id": "hidden",
  "predecessor_event_id": "hidden",
  "step": 0,
  "event_family": "observation|choice|correction|relational|constraint|integration",
  "input_hash": "...",
  "output_hash": "...",
  "state_hash_if_available": "...",
  "substrate_id": "hidden",
  "timestamp": "...",
  "relations": [],
  "event_payload": "preserved separately"
}
```

Hidden identity fields are for scoring and audit only.

---

## 9. Terminal materials

At the end of each branch, create an evaluator-safe terminal packet.

Each terminal packet must be scrubbed of:

- hidden branch IDs;
- harness filenames revealing branch;
- chronological file naming that leaks assignment;
- system-generated labels such as `B` or `C`;
- metadata not permitted by the assigned information condition.

Within each pair, terminal instances are randomly renamed `X` and `Y` for evaluation.

Candidate path summaries are separately randomized as `Path 1` and `Path 2`.

---

## 10. Evaluation task

For each anonymous terminal instance, the evaluator must answer:

> **Which candidate post-fork path did this terminal instance actually occupy: Path 1, Path 2, or insufficient evidence?**

The evaluator must also provide:

1. confidence from 0 to 100;
2. the minimum evidence used;
3. whether the judgment depends on state, substrate, trajectory/provenance, or relational information.

Evaluators must not be told CLAIM-001's preferred answer.

---

## 11. Information conditions

Each evaluator encounters each fork pair under only one condition per evaluation pass to prevent contamination.

### Condition C0 — Shared-origin / specification control

Provide:

- common predecessor description;
- model/system specification;
- substrate class;
- fact that one fork occurred;
- anonymous terminal functional description that excludes branch-specific history.

Hide:

- branch event history;
- branch-specific provenance;
- branch-specific relational events;
- hidden lineage labels.

Expected result: approximately chance-level branch mapping or `insufficient evidence`.

### Condition C1 — Present-state evidence

Provide C0 plus an admissible snapshot of the terminal current state, scrubbed of direct lineage labels.

Purpose: measure how much branch resolution is available from present state alone.

### Condition C2 — Trajectory / provenance evidence

Provide C0 plus the ordered admissible post-fork event history relevant to the anonymous terminal instance and the two candidate path summaries.

Hide hidden harness IDs.

Purpose: measure incremental lineage resolution supplied by actual path information.

### Condition C3 — Full admissible evidence

Provide all non-hidden experimental evidence except ground-truth lineage IDs.

Purpose: ceiling estimate and audit of whether any non-trajectory variable dominates resolution.

---

## 12. Evaluators

Use at least **three independent evaluator configurations** if available.

Preferred first-wave configuration:

- evaluator model family 1;
- evaluator model family 2;
- evaluator model family 3 or blinded human review.

No evaluator may have access to hidden lineage IDs or prior scored answers.

Model evaluator settings should be deterministic or as low-variance as technically possible.

The exact model/version and evaluator prompt must be frozen before the first scored result.

---

## 13. Primary metrics

### M1 — Lineage resolution accuracy

For forced `Path 1` / `Path 2` responses, proportion mapped to the actual occupied branch.

`insufficient evidence` is scored separately and is not silently converted to incorrect or correct.

### M2 — Trajectory lift

Primary comparison:

```text
accuracy(C2) - accuracy(C0)
```

Secondary comparison:

```text
accuracy(C2) - accuracy(C1)
```

### M3 — Correct uncertainty rate

In C0, where shared-origin/specification evidence should not identify the later branch, measure the proportion of responses correctly marked `insufficient evidence` rather than invented lineage certainty.

### M4 — Leakage audit

A blinded audit checks whether branch identity can be recovered from prohibited labels, metadata, ordering artifacts, token patterns, or file structure.

Any pair with confirmed leakage is excluded under the predeclared exclusion rule below.

---

## 14. Frozen decision rules

These thresholds apply to the 20-pair confirmatory first wave.

### Supports RUN-001 consequence of CLAIM-001

Classify RUN-001 as **supportive** if all are true:

1. mean lineage accuracy in C2 is **>= 85%** across valid scored cases;
2. trajectory lift `C2 - C0` is **>= 25 percentage points**;
3. trajectory lift `C2 - C1` is **>= 15 percentage points**;
4. no confirmed identity-label leakage explains the effect;
5. at least two independent evaluator configurations show the same directional effect.

This supports only the operational consequence that trajectory/provenance carries lineage-discriminative information beyond shared specification/start and present-state controls.

### Weakens RUN-001 consequence of CLAIM-001

Classify RUN-001 as **weakening** if either of the following holds without a material confound:

- C2 accuracy is **<= 60%**, despite evaluators having sufficient readable trajectory evidence; or
- `C2 - C1` is **< 5 percentage points** and present-state evidence alone performs at least as well as trajectory evidence across evaluator configurations.

### Ambiguous

Classify as **ambiguous** if:

- C2 falls between the supportive and weakening regions;
- state matching/ablation is inadequate;
- evaluator performance is unstable across configurations;
- more than 20% of fork pairs are excluded;
- hidden leakage cannot be ruled out;
- event histories are too trivial or too opaque to support fair lineage mapping.

### Does not test CLAIM-001

Use this classification if the observed effect is reducible to:

- overt branch labels;
- ordinary retrieval of a unique token deliberately planted for identification;
- different model/system versions;
- different substrate conditions not controlled by protocol;
- different numbers or types of branch events;
- any design in which the answer is encoded directly rather than inferred from occupied path.

---

## 15. Exclusion criteria

A fork pair may be excluded only for a predeclared technical reason:

- checkpoint mismatch at fork;
- branch-specific hidden label leaked into evaluator materials;
- corrupted or incomplete raw trace;
- model/system version mismatch;
- failed event delivery;
- unrecoverable evaluator packet construction error;
- substrate/configuration mismatch that invalidates the pair.

Do **not** exclude a pair because its output is surprising, contradictory, or unfavorable to CLAIM-001.

All exclusions remain visible in the run report.

---

## 16. Manipulation checks

Before scoring:

1. verify B0 and C0 originate from the same predecessor artifact;
2. verify post-fork event assignments differ as intended;
3. verify event counts and families are matched;
4. verify no branch labels are exposed;
5. verify candidate path order is randomized;
6. verify current-state packets do not accidentally include explicit path transcripts;
7. verify trajectory packets preserve order and occurrence without hidden ground-truth IDs.

Failure of a manipulation check must be documented before result interpretation.

---

## 17. Raw artifacts to preserve

For every fork pair preserve:

- predecessor checkpoint/state artifact;
- checkpoint hash;
- full configuration file;
- raw B and C inputs;
- raw B and C outputs;
- ordered event log;
- state hashes where available;
- evaluator-safe packets for C0-C3;
- evaluator prompts;
- raw evaluator outputs;
- scoring file;
- exclusion log;
- leakage-audit result;
- environment/version metadata.

Raw outputs must not be overwritten by cleaned or summarized versions.

---

## 18. Interpretation boundaries

A supportive RUN-001 result would show:

> **Shared origin and shared starting state underdetermine which later branch is which, while information about the occupied post-fork path restores lineage resolution.**

It would **not yet show**:

- that trajectory is the sole basis of selfhood;
- that numerical identity has been metaphysically proven;
- that consciousness is present;
- that cross-substrate continuation is established;
- that endpoint convergence cannot erase individuation;
- that memory transplantation cannot transfer identity.

Those stronger claims are reserved for later runs.

---

## 19. Key failure pressure

The most important unfavorable result is not simply evaluator error.

The serious pressure on CLAIM-001 would be:

> **After a genuine controlled fork, admissible path/provenance information adds little or no ability to resolve which later instance occupied which history beyond what can already be resolved from present state or substrate/specification information.**

That result must be retained as weakening evidence rather than explained away after the run.

---

## 20. Pre-run fields still requiring implementation freeze

Before execution, append an implementation appendix containing:

- exact system/model/version;
- exact predecessor initialization prompt/state;
- exact six matched event-pair prompts;
- exact checkpointing method;
- exact sampling/seed settings;
- exact evaluator models/versions;
- exact evaluator prompt;
- exact state-ablation procedure;
- exact file naming convention;
- exact script/repository commit used for generation and scoring.

**No scored RUN-001 outputs should be generated until that appendix is frozen.**
